from neo4j import Neo4jDriver, Session, Driver, GraphDatabase, Result
from utils.neo4j_driver import neo4j_driver


driver: Driver = neo4j_driver


def get_amenity_tags(city: str):
    with driver.session() as session:
        result: Result = session.run(
            # f"MATCH (n) where n.area = '{city}' RETURN DISTINCT(n.amenity)")
            f"match (n) where n.area = '{city}'unwind labels(n) as lab return distinct(lab)")
        return result.values()


def get_number_of_nodes_amenity(amenity: str):
    with driver.session() as session:

        result: Result = session.run(
            f"MATCH (n:{amenity}) return COUNT(n) as c")
        return result.value("c")[0]

def get_amenity_numbers_city(amenity: str, city: str):
    with driver.session() as session:

        result: Result = session.run(
        f"MATCH (n:{amenity}) where n.area = $city return COUNT(*)", city=city)
        return result.value("COUNT(*)")[0]


def get_n_of_nodes_by_appareance():
    with driver.session() as session:
        result: Result = session.run(f"""MATCH (n:Place) WITH
        [i IN RANGE(0,size(labels(n) ) - 2 )| labels(n)[i] ] as tag, n
        UNWIND tag as amenity
        RETURN amenity, count(n) as count_of_nodes
        ORDER BY count_of_nodes desc""")
        return result.values("amenity", "count_of_nodes")
