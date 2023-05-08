import re
import logging
from neo4j import GraphDatabase, Driver, Result, Transaction
from OSMPythonTools.overpass import overpassQueryBuilder
import concurrent.futures
from OSMPythonTools.nominatim import Nominatim
import urllib.parse
import time
from osm_exception import InvalidCityNameException
from utils.neo4j_driver import neo4j_driver


OSM_URL = "https://overpass-api.de/api/interpreter?data=[out:json][timeout:1000];"

driver: Driver = neo4j_driver


def load_node_apoc(tx: Transaction, city: str, common_node_label: str, selector: str = "amenity"):
    nominatim_api = Nominatim()
    areaId = nominatim_api.query(city).areaId()

    if areaId == "":
        raise InvalidCityNameException(
            f"La ciudad con nombre {city} no existe o no tiene un area Id")

    query = OSM_URL + urllib.parse.quote(overpassQueryBuilder(
        area=areaId, elementType="node", selector=selector))

    apoc_stmt = f"""
    CALL apoc.load.json(\"{query}\") 
    YIELD value
    UNWIND value.elements AS row
    MERGE (n:{common_node_label} {{id:row.id}})
    ON CREATE SET
     n += row.tags, n.area = '{city}',
     n.category = row.tags.{selector},
     n.type = "{selector}"
    REMOVE n.{selector}
    WITH n, point({{latitude:row.lat,longitude:row.lon}}) as p
    SET n.coords = p
    """

    tx.run(apoc_stmt)


def update_city_nodes(tx: Transaction, city: str, common_node_label: str, selector="amenity"):
    nominatim_api = Nominatim()
    areaId = nominatim_api.query(city).areaId()

    if areaId == "":
        raise InvalidCityNameException(
            f"La ciudad con nombre {city} no existe o no tiene un area Id")

    query = OSM_URL + urllib.parse.quote(overpassQueryBuilder(
        area=areaId, elementType="node", selector=selector))

    apoc_stmt = f"""
    CALL apoc.load.json(\"{query}\") 
    YIELD value
    UNWIND value.elements AS row
    MERGE (n:{common_node_label} {{id:row.id, area:"{city}"}})
    ON CREATE 
    SET n += row.tags, n.type = row.type, n.lat = row.lat, n.lon = row.lon, n.area = '{city}'
    SET n.category = row.tags.{selector}
    REMOVE n.{selector}
    """

    tx.run(apoc_stmt)
    rename_nodes_to_category(tx, common_node_label)


def rename_nodes_to_category(tx: Transaction, node_label_to_rename: str = "Place"):
    category_query = f"""MATCH (n:{node_label_to_rename})
    where n.category is not null
    return distinct(n.category) as category"""

    node_categories: Result = tx.run(category_query)

    for nc in node_categories:
        category: str = nc["category"]

        for sub_category in re.split(";|:|,", category):

            format_category: str = sub_category.replace(
                " ", "_").replace("-", "_").capitalize()
            if not re.match("(\w|\ )+$", format_category):
                logging.warning(f"{format_category} does not match regex")
                continue

            # print(f"Renombrado de {amenity}")
            rename_update = f"""\
            MATCH (n:{node_label_to_rename})
            where n.category = "{category}"
            SET n:`{format_category}`
            """
            # REMOVE n:{node_label_to_rename}
            tx.run(rename_update)

        # tx.run(f"MATCH (n:{node_label_to_rename}) where n.amenity = '{amenity}' REMOVE n:{node_label_to_rename}  ")
    tx.run("""MATCH (n:Place)
           SET n.category = toUpper(substring(n.category, 0, 1)) + substring(n.category, 1)""")


def load_city_nodes(city: str, common_node_label="Place", selectors: list = ["amenity"]):
    logging.basicConfig(level=logging.INFO)

    for selector in selectors:
        with driver.session() as session:

            logging.info(
                f">>>Cargando datos de la ciudad {city} tag {selector}")
            session.execute_write(load_node_apoc, city,
                                    common_node_label, selector)
            logging.info(
                f">>>Renombrando nodos de la ciudad {city} tag {selector}")
            session.execute_write(rename_nodes_to_category, common_node_label)
            input("Esperando a corregir multiples categorias")

    with driver.session() as session:    
        session.execute_write(create_categories_net, city)
        logging.info("Creando red de categorias")

    logging.info(">>>Finalizado!!!")




def link_nodes(city: str, link_distance: int, common_node_label: str = "Place"):

    with driver.session() as session:
        session.run(f"""
        MATCH(n:{common_node_label} {{area:$city}}),(m:{common_node_label} {{area:$city}})
        WHERE NOT (n)--(m) AND id(n) < id(m)
        with n,m, point.distance(n.coords, m.coords) as distance
        WHERE distance <= $distance
        CREATE (n)-[r:IS_NEAR {{distance: distance}}]->(m)
        """, city=city, distance=link_distance)


def create_categories_net(tx: Transaction, city: str, method: str = "permutation"):
    query = f"""match (n:Place)
    where n.area = $city
    with collect(distinct(n.category)) as tags
    unwind tags as tag
    create (m:Category {{name: tag, city: $city}})
    """
    tx.run(query, city=city)

    tx.run(f"""
    match (n:Category),(m:Category)
    where id(n) <= id(m) and n.city = $city and m.city = $city
    create (n)-[r:Rel {{sim_value : [], method:$method}}]->(m)
    """, city=city, method=method)


if __name__ == "__main__":
    # ciudades = ["Sevilla", "Zaragoza", "Valencia"]
    ciudades = ["León", "Salamanca","Valladolid", "Burgos", "Palencia", "Zamora"]
    tags = ["shop", "amenity"]

    for c in ciudades:
        load_city_nodes(c, "Place", tags)
    input("Espera")
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(link_nodes, city, 100) for city in ciudades]
        concurrent.futures.wait(futures)
