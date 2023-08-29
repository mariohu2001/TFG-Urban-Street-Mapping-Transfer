from utils.neo4j_driver import neo4j_driver
from neo4j import Result, Session, Transaction, Driver
import concurrent.futures
from common_queries import get_cities, get_categories, get_city_places_ids
import json
import time

driver: Driver = neo4j_driver

Q_keys = ["Qjensen", "Qjensen_raw", "Qperm", "Qperm_raw"]


def get_city_nodes_quality_indices(tx: Transaction, city: str):
    cypher_query = """
    MATCH (n:Place)
    WHERE n.area = $city
    return apoc.convert.fromJsonMap(n.Q) as Q, n.category as category
    """

    result: Result = tx.run(cypher_query, city=city)

    return result.data()


def calculate_indice_mrr(nodes: list, indice: str):
    mrr = 0
    for node in nodes:
        mrr+= calculate_node_mrr(node, indice)

    return mrr/len(nodes)

def calculate_node_mrr(node: dict, indice: str):
    Q: dict = node["Q"]
    category: str = node["category"]

    sorted_categories: list = sorted(
        Q.keys(), key=lambda x: Q[x][indice], reverse=True)

    return 1.0/(sorted_categories.index(category) + 1)

def calculate_mrr(nodes: list):
    MRR = dict()

    for q in Q_keys:

        MRR[q] = calculate_indice_mrr(nodes, q)

    return MRR


if __name__ == "__main__":

    cities = get_cities()
    quality_indices_MRR = dict()

    with neo4j_driver.session() as session:

        for city in cities:
            print(city)
            quality_indices_MRR[city] = dict()
            nodes_qs = session.execute_read(
                get_city_nodes_quality_indices, city)
            
            quality_indices_MRR[city] = calculate_mrr(nodes_qs)

    
    with open("MRR.json", "w", encoding="UTF-8") as file:
        json.dump(quality_indices_MRR, file, indent=4, ensure_ascii=False)
