from utils.neo4j_driver import neo4j_driver
from neo4j import Result, Session, Transaction, Driver
import concurrent.futures
from common_queries import get_cities, get_categories, get_city_places_ids
import json
import time

driver: Driver = neo4j_driver


def create_matrix(rows: list) -> dict:

    matrix_dict = dict()

    for row in rows:
        source = row["i"]
        target = row["j"]
        zscore = row["value"]

        if source not in matrix_dict:
            matrix_dict[source] = dict()

        matrix_dict[source][target] = zscore

    return matrix_dict


def get_zscore_matrix(tx: Transaction, city: str) -> dict:
    cypher_query = """
    MATCH (p:Category)-[r:Rel]-(q:Category)
    where p.city = $city and p.city = q.city
    return p.name as i, q.name as j, r.z_score as value 
    """

    result: Result = tx.run(cypher_query, city=city)
    result_dict = result.data()

    return create_matrix(result_dict)


def get_jensen_coeff_matrix(tx: Transaction, city: str) -> dict:
    cypher_query = """
    MATCH (p:Category)-[r:Jensen]->(q:Category)
    where p.city = $city and p.city = q.city
    return p.name as i, q.name as j, log(r.coeff) as value
    """

    result: Result = tx.run(cypher_query, city=city)
    result_dict = result.data()

    return create_matrix(result_dict)


def get_avg_nei_matrix(tx: Transaction, city: str) -> dict:
    cypher_query = """
    MATCH (c:Category)-[r:Rel]-(k:Category)
    where c.city = $city and k.city = c.city
    return c.name as i, k.name as j, toFloat(r.real_value)/toFloat(c.n_nodes) as value
    """

    result: Result = tx.run(cypher_query, city=city)
    result_dict = result.data()

    return create_matrix(result_dict)


def get_nei_matrix(tx: Transaction, id: int) -> dict:
    cypher_query = """
    MATCH (n:Place), (p:Category)
    where id(n) = $id
    and n.area = p.city
    match (m:Place)
    where m.category = p.name and m.area = n.area
    optional match (n)-[r]-(m)
    return count(r) as nei, m.category as cat
    """

    result: Result = tx.run(cypher_query, id=id)

    nei = result.data()
    nei_matrix = dict()
    for n in nei:
        nei_matrix[n["cat"]] = n["nei"]

    return nei_matrix


def assign_quality_indexes(tx: Transaction, id: int, Q: dict):
    cypher_query = """
    MATCH (n:Place)
    WHERE id(n) = $id
    SET n.Q = $Q
    """

    tx.run(cypher_query, id=id, Q=json.dumps(Q))


if __name__ == "__main__":

    ciudades = get_cities()
    for ciudad in ciudades:
        print(ciudad)
        categories = get_categories(ciudad)


        Q = dict()
        timeini = time.time()
        with driver.session() as session:
            jensen = session.execute_read(get_jensen_coeff_matrix, ciudad)
            zscore = session.execute_read(get_zscore_matrix, ciudad)
            nei_avg = session.execute_read(get_avg_nei_matrix, ciudad)

            for id in get_city_places_ids(ciudad):
                nei = session.execute_read(get_nei_matrix, id)

                for i in categories:
                    Q_perm = 0
                    Q_perm_raw = 0
                    Q_jensen = 0
                    Q_jensen_raw = 0
                    for j in categories:
                        Q_perm += zscore[i][j] * (nei[j] - nei_avg[i][j])
                        Q_perm_raw += zscore[i][j] * (nei[j])
                        Q_jensen += jensen[i][j] * (nei[j] - nei_avg[i][j])
                        Q_jensen_raw += jensen[i][j] * (nei[j])

                    Q[i] = {
                        "Qperm": Q_perm,
                        "Qperm_raw": Q_perm_raw,
                        "Qjensen": Q_jensen,
                        "Qjensen_raw": Q_jensen_raw
                    }

                session.execute_write(assign_quality_indexes, id, Q)
            # with open("Q.json", "w") as file:
            #     json.dump(Q, file, indent=4)

            print(f"Tiempo {time.time() - timeini} s")
