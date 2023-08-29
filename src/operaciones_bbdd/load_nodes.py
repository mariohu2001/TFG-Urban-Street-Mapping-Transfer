import re
import logging
from neo4j import GraphDatabase, Driver, Result, Transaction
from OSMPythonTools.overpass import overpassQueryBuilder
import concurrent.futures
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import Overpass
import urllib.parse
import time
from osm_exception import InvalidCityNameException
from utils.neo4j_driver import neo4j_driver


OSM_URL = "https://overpass-api.de/api/interpreter?data=[out:json][timeout:1000];"

driver: Driver = neo4j_driver


def load_node_apoc(tx: Transaction,city: str, ine_municipio: int,  common_node_label: str, selector: str = "amenity"):

    overpass_api = Overpass()
    
    
    print(f'area[name={city}]["ine:municipio"={ine_municipio}]; out body;')
    city_id = overpass_api.query(f'area[name="{city}"]["ine:municipio"={ine_municipio}]; out body;').elements()[0].id()

    if city_id == "":
        raise InvalidCityNameException(
            f"País con nombre {city} no existe o no tiene un area Id")


    query = OSM_URL + urllib.parse.quote(overpassQueryBuilder(
        area=city_id, elementType="node", selector=selector))

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



def rename_nodes_to_category(tx: Transaction, node_label_to_rename: str = "Place"):
    category_query = f"""MATCH (n:{node_label_to_rename})
    where n.category is not null
    return distinct(n.category) as category, n.type as type"""

    node_categories: Result = tx.run(category_query)

    for nc in node_categories:
        category: str = nc["category"]
        type: str = nc["type"]

        for sub_category in re.split(";|:|,", category):

            format_category: str = sub_category.replace(
                " ", "_").replace("-", "_").capitalize()

            if not re.match("(\w|\ )+$", format_category):
                logging.warning(f"{format_category} does not match regex")
                continue

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


def load_city_nodes(city: str, ine_code:int, common_node_label="Place", selectors: list = ["amenity"]):
    logging.basicConfig(level=logging.INFO)

    for selector in selectors:
        with driver.session() as session:

            logging.info(
                f">>>Cargando datos de la ciudad {city} tag {selector}")
            session.execute_write(load_node_apoc,city, ine_code,
                                  common_node_label, selector)
            logging.info(
                f">>>Renombrando nodos de la ciudad {city} tag {selector}")
            session.execute_write(rename_nodes_to_category, common_node_label)
            input("Esperando a corregir multiples categorias")


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




if __name__ == "__main__":
    # ciudades = ["Sevilla", "Zaragoza", "Valencia"]
    ciudades = {"Palencia": "34120", "León": "24089", "Salamanca": "37274", "Valladolid": "47186",
                "Burgos": "09059"}
    tags = ["shop", "amenity"]

    # for city, code in ciudades.items():
    #     load_city_nodes(city, code, "Place", tags)
    # input("Espera")
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     futures = [executor.submit(link_nodes, city, 100) for city in ciudades]
    #     concurrent.futures.wait(futures)

    for city in ciudades.keys():
        print(city)
        link_nodes(city, 100)
