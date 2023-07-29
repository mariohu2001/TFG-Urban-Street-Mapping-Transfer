from neo4j import Driver, Transaction, Result
from flask import current_app
from concurrent.futures import ProcessPoolExecutor, as_completed




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


def get_zscore_matrix(city: str, driver: Driver) -> dict:
    cypher_query = """
    MATCH (p:Category)-[r:Rel]-(q:Category)
    where p.city = $city and p.city = q.city
    return p.name as i, q.name as j, r.z_score as value
    """
    with driver.session() as session:

        result: Result = session.run(cypher_query, city=city)
        result_dict = result.data()

        return create_matrix(result_dict)


def get_jensen_coeff_matrix(city: str, driver: Driver) -> dict:
    cypher_query = """
    MATCH (p:Category)-[r:Jensen]->(q:Category)
    where p.city = $city and p.city = q.city
    return p.name as i, q.name as j, log(r.coeff) as value
    """
    with driver.session() as session:
        result: Result = session.run(cypher_query, city=city)
        result_dict = result.data()

        return create_matrix(result_dict)


def get_avg_nei_matrix(city: str, driver: Driver) -> dict:
    cypher_query = """
    MATCH (c:Category)-[r:Rel]-(k:Category)
    where c.city = $city and k.city = c.city
    return c.name as i, k.name as j, toFloat(r.real_value)/toFloat(c.n_nodes) as value
    """
    with driver.session() as session:
        result: Result = session.run(cypher_query, city=city)
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


def get_nei_matrix_coords(tx: Transaction, lat: float, lon: float, driver: Driver) -> dict:
    cypher_query = """
    with Point({latitude: $lat, longitude: $lon}) as point
    match (n:Place)
    where point.distance(point, n.coords) <= 100
    return n.category as cat, count(n) as nei
    """

    result: Result = tx.run(cypher_query, lat=lat, lon=lon)

    nei = result.data()
    nei_matrix = dict()
    for n in nei:
        nei_matrix[n["cat"]] = n["nei"]

    return nei


def get_quality_indices_coords(coords: dict, jensen: dict, perm: dict, nei_avg: dict, categories: list, driver: Driver) -> dict:
    full_Q = {}
    with driver.session() as session:
        for coord in coords:
            lat, lon = coord["lat"], coord["lon"]
            id = coord["number"]
            full_Q[id] = {}
            Q = {}
            nei = session.execute_read(get_nei_matrix_coords, lat, lon)

            for i in categories:
                Q_perm = 0
                Q_perm_raw = 0
                Q_jensen = 0
                Q_jensen_raw = 0
                for j in categories:
                    Q_perm += perm[i][j] * (nei.get(j, 0) - nei_avg[i][j])
                    Q_perm_raw += perm[i][j] * (nei.get(j, 0))
                    Q_jensen += jensen[i][j] * (nei.get(j, 0) - nei_avg[i][j])
                    Q_jensen_raw += jensen[i][j] * (nei.get(j, 0))
                Q[i] = {
                    "Qperm": Q_perm,
                    "Qperm_raw": Q_perm_raw,
                    "Qjensen": Q_jensen,
                    "Qjensen_raw": Q_jensen_raw
                }
            full_Q[id] = Q

    return full_Q


def get_quality_indices_places(places: dict, jensen: dict, perm: dict, nei_avg: dict, categories: list, driver: Driver) -> dict:
    full_Q = {}

    with driver.session() as session:
        for place in places:
            node_id: int = place["id"]
            Q = {}
            full_Q[node_id] = {}

            nei = session.execute_read(get_nei_matrix, node_id)
            for i in categories:
                Q_perm = 0
                Q_perm_raw = 0
                Q_jensen = 0
                Q_jensen_raw = 0
                for j in categories:
                    Q_perm += perm[i][j] * (nei.get(j, 0) - nei_avg[i][j])
                    Q_perm_raw += perm[i][j] * (nei.get(j, 0))
                    Q_jensen += jensen[i][j] * (nei.get(j, 0) - nei_avg[i][j])
                    Q_jensen_raw += jensen[i][j] * (nei.get(j, 0))
                Q[i] = {
                    "Qperm": Q_perm,
                    "Qperm_raw": Q_perm_raw,
                    "Qjensen": Q_jensen,
                    "Qjensen_raw": Q_jensen_raw
                }
            place[node_id] = Q
    return full_Q


def get_categories(city: str, driver: Driver):

    cypher_query = """
    MATCH (n:Place)
    WHERE n.area = $city
    return distinct(n.categories) as cats
    """
    with driver.session() as session:
        result: Result = session.run(cypher_query, city)
        return result["cats"]


def get_quality_indices(coords: dict, places: dict, city: str, driver: Driver):

    with ProcessPoolExecutor() as pool:
        jensen_f = pool.submit(get_jensen_coeff_matrix, city, driver)
        perm_f = pool.submit(get_zscore_matrix, city, driver)
        nei_avg_f = pool.submit(get_avg_nei_matrix, city, driver)
        categories_f = pool.submit(get_categories, city, driver)

    jensen = jensen_f.result()
    perm = perm_f.result()
    nei_avg = nei_avg_f.result()
    categories = categories_f.result()

    with ProcessPoolExecutor() as pool:

        places_q = pool.submit(get_quality_indices_places,
                               places, jensen, perm, nei_avg, categories, driver)
        coords_q = pool.submit(get_quality_indices_coords,
                               coords, jensen, perm, nei_avg, categories, driver)

        return {"coords": coords_q.result(), "places": places_q.result()}


def calculate_tops(quality_indices):
    with ProcessPoolExecutor() as pool:
        tops = dict(pool.map(get_top, quality_indices.items()))

    return tops


def get_top(k: int, v: dict):
    sorted_tops = {}
    for key in v.keys():
        sorted_tops[key] = list(
            sorted(v[key].keys(), key=lambda x: x, reverse=True))
    return k, sorted_tops


def get_tops(coords: dict, places: dict, city: str):
    quality_indices = get_quality_indices(coords, places, city)

    q_places = quality_indices["places"]
    q_coords = quality_indices["coords"]

    with ProcessPoolExecutor() as pool:
        nodes_f = pool.submit(calculate_tops, q_places)
        coords_f = pool.submit(calculate_tops, q_coords)

        return {"places": nodes_f.result(), "coords": coords_f.result()}
