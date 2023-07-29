from neo4j import Driver, Result, Transaction
from operaciones_bd.common_queries import get_categories

from .base import baseDAO


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


def get_nei_matrix(tx: Transaction, lat: float, lon: float) -> dict:
    cypher_query = """
    with point({longitude: $longitude, latitude: $latitude}) AS point
    Match (m:Place)
    where point.distance(point, m.coords) <= 100  
    return count(m) as nei, m.category as cat
    """

    result: Result = tx.run(cypher_query, latitude=lat, longitude=lon)

    nei = result.data()
    nei_matrix = dict()
    for n in nei:
        nei_matrix[n["cat"]] = n["nei"]

    return nei_matrix


class CoordsDAO(baseDAO):

    def get_top_categories(self, coords_list: list, city: str, ntop: int = 5):

        tops = dict()

        categories = get_categories(city)

        with self.driver.session() as session:
            jensen = session.execute_read(get_jensen_coeff_matrix, city)
            zscore = session.execute_read(get_zscore_matrix, city)
            nei_avg = session.execute_read(get_avg_nei_matrix, city)

            for coord in coords_list:
                coord_top = dict()

                nei = session.execute_read(
                    get_nei_matrix, coord["lat"], coord("lon"))
                Q = dict()
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

                quality_indices_names = [
                    "Qperm", "Qperm_raw", "Qjensen", "Qjensen_raw"]
                for q in quality_indices_names:
                    coord_top[q] = sorted(
                        Q, key=lambda x: x[q], reverse=True)[:ntop]

                tops[coord["num"]] = coord_top

        return tops
