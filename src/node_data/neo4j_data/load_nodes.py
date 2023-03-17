import re
import logging
from neo4j import GraphDatabase, Driver, Session, Result
from OSMPythonTools.overpass import OverpassResult, Overpass, overpassQueryBuilder
from OSMPythonTools.element import Element
from configparser import ConfigParser
from OSMPythonTools.nominatim import Nominatim
import concurrent.futures
import urllib.parse
import sys
import time
from node_data.osm_data.osm_exception import InvalidCityNameException


_config: ConfigParser = ConfigParser()
_config.read("../config/neo4j_config.ini")
_uri, _neo4j_password = _config["neo4j"].values()


driver: Driver = GraphDatabase.driver(_uri, auth=("neo4j", _neo4j_password))


def load_node_apoc(tx: Session, city: str, common_node_label: str):
    nominatim_api = Nominatim()
    areaId = nominatim_api.query(city).areaId()

    if areaId == "":
        raise InvalidCityNameException(
            f"La ciudad con nombre {city} no existe o no tiene un area Id")

    query = "https://overpass-api.de/api/interpreter?data=[out:json][timeout:1000];" + urllib.parse.quote(overpassQueryBuilder(
        area=areaId, elementType="node", selector="amenity"))

    apoc_stmt = f"""
    CALL apoc.load.json(\"{query}\") 
    YIELD value
    UNWIND value.elements AS row
    CREATE (n:{common_node_label} {{id:row.id}})
    SET n += row.tags, n.type = row.type, n.lat = row.lat, n.lon = row.lon, n.area = '{city}'
    WITH n, point({{latitude:n.lat,longitude:n.lon}}) as p
    SET n.coords = p
    """
    # MERGE (n:{common_node_label} {{id:row.id}})
    # ON CREATE SET n += row.tags, n.type = row.type, n.lat = row.lat, n.lon = row.lon, n.area = "{city}"

    tx.run(apoc_stmt)


def update_city_nodes(tx: Session, city: str, common_node_label: str):
    nominatim_api = Nominatim()
    areaId = nominatim_api.query(city).areaId()

    if areaId == "":
        raise InvalidCityNameException(
            f"La ciudad con nombre {city} no existe o no tiene un area Id")

    query = "https://overpass-api.de/api/interpreter?data=[out:json][timeout:1000];" + urllib.parse.quote(overpassQueryBuilder(
        area=areaId, elementType="node", selector="amenity"))

    apoc_stmt = f"""
    CALL apoc.load.json(\"{query}\") 
    YIELD value
    UNWIND value.elements AS row
    MERGE (n:{common_node_label} {{id:row.id, area:"{city}"}})
    ON CREATE 
    SET n += row.tags, n.type = row.type, n.lat = row.lat, n.lon = row.lon, n.area = '{city}'
    """

    tx.run(apoc_stmt)
    rename_nodes_to_amenity(tx, common_node_label)


def rename_nodes_to_amenity(tx: Session, node_label_to_rename: str):
    amenity_query = f"""MATCH (n:{node_label_to_rename})
    where n.amenity is not null
    return distinct(n.amenity) as amenity"""

    node_amenities: Result = tx.run(amenity_query)

    for am in node_amenities:
        amenity: str = am["amenity"]

        for sub_amenity in re.split(";|:", amenity):

            format_amenity: str = sub_amenity.replace(
                " ", "_").replace("-", "_").capitalize()
            if not re.match("(\w|\ )+$", format_amenity):
                logging.warning(f"{format_amenity} does not match regex")
                continue

            # print(f"Renombrado de {amenity}")
            rename_update = f"""\
            MATCH (n:{node_label_to_rename})
            where n.amenity = "{amenity}"
            SET n:`{format_amenity}`
            """
            # REMOVE n:{node_label_to_rename}
            tx.run(rename_update)

            category_create = f"""MERGE (n:Category {{name:$amenity}}) """

            tx.run(category_create, amenity=format_amenity)
        # tx.run(f"MATCH (n:{node_label_to_rename}) where n.amenity = '{amenity}' REMOVE n:{node_label_to_rename}  ")


def load_city_nodes(city: str, common_node_label="Place"):
    logging.basicConfig(level=logging.INFO)
    with driver.session() as session:
        logging.info(f">>>Cargando datos de la ciudad {city}")
        session.execute_write(load_node_apoc, city, common_node_label)
        logging.info(f">>>Renombrando nodos de la ciudad {city}")
        session.execute_write(rename_nodes_to_amenity, common_node_label)
        # logging.info(">>>Enlazando nodos")

    logging.info(">>>Finalizado!!!")


def link_nodes(city: str, link_distance: int, common_node_label: str = "Place"):

    with driver.session() as session:
        city_nodes = session.run(f"""MATCH(n:{common_node_label}  {{ area:$city }}) 
        return id(n) as id""", city=city).values()

    with driver.session() as session:
        for i, id in enumerate(city_nodes):
            time_ini = time.time()
            session.run(f"""MATCH(n:{common_node_label})
            MATCH (m:{common_node_label}{{area:$city}}) 
            WHERE NOT (n)--(m) AND n<>m and id(n) = $id
            with n,m, point.distance(n.coords, m.coords) as distance
            WHERE distance <= $distance
            CREATE (n)-[r:IS_NEAR {{distance: distance}}]->(m)
            """, city=city, distance=link_distance, id=id[0])
            time_fin = time.time()
            print(f">>>{i}/{len(city_nodes)}|id{id}:{city}>T:{time_fin-time_ini}", flush=True)
