from utils.neo4j_driver import neo4j_driver
from common_queries import get_cities
import json
import time
from neo4j import Result, Session, Transaction, Driver


driver: Driver = neo4j_driver


def write_places_to_json(tx: Transaction, city: str) -> None:
    cypher_query = """
    MATCH (n:Place)
    where n.area = $city
    return n.category as Categoria, apoc.convert.fromJsonMap(n.Q) as QualityIndices
    """

    result: Result = tx.run(cypher_query, city=city)

    with open(f"../models/dataset/Q_{city}.json", "w") as file:
        json.dump(result.data(), file, indent=4, ensure_ascii=False)


if __name__ == "__main__":

    with driver.session() as session:
        for city in get_cities():
            print(city)
            session.execute_read(write_places_to_json, city)
