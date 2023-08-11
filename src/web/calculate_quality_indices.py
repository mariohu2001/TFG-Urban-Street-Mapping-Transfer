from neo4j import Driver, Transaction, Result, Session
from flask import current_app
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier


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
    where n.id = $id
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


def get_nei_matrix_coords(tx: Transaction, lat: float, lon: float) -> dict:
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

    return nei_matrix


def get_quality_indices_coords(session: Session, coords: dict, jensen: dict, perm: dict, nei_avg: dict, categories: list) -> dict:
    full_Q = {}

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


def get_quality_indices_places(session: Session, places: dict, jensen: dict, perm: dict, nei_avg: dict, categories: list) -> dict:
    full_Q = {}

    for place in places:
        node_id: int = place["id"]
        Q = {}

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
        full_Q[place["number"]] = Q

    return full_Q


def get_categories(city: str, driver: Driver):

    cypher_query = """
    MATCH (n:Place)
    WHERE n.area = $city
    return distinct(n.category) as cats order by cats
    """
    with driver.session() as session:
        result: Result = session.run(cypher_query, city=city)
        cats = result.value("cats")
        return cats


def get_quality_indices(coords: dict, places: dict, city: str, driver: Driver):

    categories = get_categories(city, driver)
    jensen = get_jensen_coeff_matrix(city, driver)
    perm = get_zscore_matrix(city, driver)
    nei_avg = get_avg_nei_matrix(city, driver)

    places_q = get_quality_indices_places(driver.session(),
                                          places, jensen, perm, nei_avg, categories)
    coords_q = get_quality_indices_coords(driver.session(),
                                          coords, jensen, perm, nei_avg, categories)

    return {"coords": coords_q, "places": places_q}


def calculate_tops(quality_indices):
    with ProcessPoolExecutor() as pool:
        tops = dict(pool.map(get_top, quality_indices.items()))


    return tops


def get_top(items):
    k, v = items
    sorted_tops = {}
    for key in ["Qperm", "Qperm_raw", "Qjensen", "Qjensen_raw"]:
        sorted_tops[key] = list(
            sorted(v.keys(), key=lambda x: v[x][key], reverse=True))

    # sorted_tops["random_forest"] = [
    #     "Bar" for i in range(len(sorted_tops["Qperm"]))]
    return k, sorted_tops


def get_local_top_rf(city: str, quality_indices, model: RandomForestClassifier):

    tops = dict()

    for number, indices in quality_indices.items():

        df = pd.json_normalize({"QualityIndices": indices},)
        df = df[model.feature_names_in_]
        predictions = model.predict_proba(df)

        cat_prob = []
        print(model.classes_, type(model.classes_))
        for c, p in zip(model.classes_.flatten(),predictions.flatten()):

            cat_prob.append((p,c))

        tops[number] = [x[1]
                        for x in sorted(cat_prob, key=lambda x: x[0], reverse=True)]

    print(tops, flush=True)
    return tops


def get_tops(coords: dict, places: dict, city: str, driver: Driver, model: RandomForestClassifier):
    quality_indices = get_quality_indices(coords, places, city, driver)

    q_places = quality_indices["places"]
    q_coords = quality_indices["coords"]

    with ProcessPoolExecutor() as pool:
        nodes_f = pool.submit(calculate_tops, q_places)
        coords_f = pool.submit(calculate_tops, q_coords)

        # LLamada a método de RF
        rf_places = pool.submit(get_local_top_rf, city, q_places, model)
        rf_coords = pool.submit(get_local_top_rf, city, q_coords, model)

        places_tops = nodes_f.result()
        coords_tops = coords_f.result()

        rfp = rf_places.result()
        rfc = rf_coords.result()

        print(rfc, rfp, flush=True)

        for k, v in rfp.items():
            places_tops[k]["random_forest"] = v

        for k, v in rfc.items():
            coords_tops[k]["random_forest"] = v

        ret = {"places": places_tops, "coords":  coords_tops}
        print(ret)
        return ret
