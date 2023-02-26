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
from node_data.osm_data.osm_exception import InvalidCityNameException



_config: ConfigParser = ConfigParser()
_config.read("../config/neo4j_config.ini")
_uri, _neo4j_password = _config["neo4j"].values()


driver: Driver = GraphDatabase.driver(_uri, auth=("neo4j", _neo4j_password))


# def load_nodes(tx: Session, node_name: str, overpass_result: OverpassResult):

#     for i, element in enumerate(overpass_result.elements()):
#         print(f"{i}//{len(overpass_result.elements())}")
#         create_stmt: str = f"""MERGE (n:{node_name} {{ id : $id, lat : $lat,  lon : $lon """
#         node_tags: dict = _rename_dict_items(element.tags(), [":", "-"], "_")
#         # print(node_tags)
#         for tag in node_tags.keys():
#             create_stmt += f', {tag}:${tag}'
#         create_stmt += "}) "

#         tx.run(create_stmt, id=element.id(),
#                lat=element.lat(), lon=element.lon(), **node_tags)


# def load_node(tx: Session, node_name: str, overpass_element: Element):
#     create_stmt: str = f"""MERGE (n:{node_name} {{ id : $id, lat : $lat,  lon : $lon """
#     node_tags: dict = _rename_dict_items(
#         overpass_element.tags(), [":", "-"], "_")
#     # print(node_tags)
#     for tag in node_tags.keys():
#         create_stmt += f', {tag}:${tag}'
#     create_stmt += "}) "

#     tx.run(create_stmt, id=overpass_element.id(),
#            lat=overpass_element.lat(), lon=overpass_element.lon(), **node_tags)


def load_node_apoc(tx: Session, city: str, common_node_label: str):
    nominatim_api = Nominatim()
    areaId = nominatim_api.query(city).areaId()
    if areaId == "":
        raise InvalidCityNameException(
            f"La ciudad con nombre {city} no existe o no tiene un area Id")
    query = "https://overpass-api.de/api/interpreter?data=[out:json];" + urllib.parse.quote(overpassQueryBuilder(
        area=areaId, elementType="node", selector="amenity"))
    apoc_stmt = f"""
    CALL apoc.load.json(\"{query}\") 
    YIELD value
    UNWIND value.elements AS row
    CREATE (n:{common_node_label})
    SET n.type = row.type, n.id = row.id, n.lat = row.lat, n.lon = row.lon, n.area = "{city}"
    SET n += row.tags
    """
    tx.run(apoc_stmt)


def rename_nodes_to_amenity(tx: Session, node_label_to_rename: str):
    amenity_query = f"""MATCH (n:{node_label_to_rename})
    where n.amenity is not null
    return distinct(n.amenity) as amenity"""

    node_amenities: Result = tx.run(amenity_query)

    for am in node_amenities:
        amenity: str = am["amenity"]
        if not re.match("(\w|\ )+$", amenity):
            print(f"{amenity} does not match regex")
            continue

        # print(f"Renombrado de {amenity}")
        rename_update = f"""\
        MATCH (n:{node_label_to_rename})
        where n.amenity = "{amenity}"
        SET n:{amenity.capitalize().replace(" ", "")}
        REMOVE n:{node_label_to_rename}
        """
        tx.run(rename_update)



def load_city_nodes(city: str, common_node_label="Nodo"):
    logging.basicConfig(level=logging.INFO)
    with driver.session() as session:
        logging.info(f">>>Cargando datos de la ciudad {city}")
        session.execute_write(load_node_apoc, city, common_node_label)
        logging.info(f">>>Renombrando nodos de la ciudad {city}")
        session.execute_write(rename_nodes_to_amenity, common_node_label)
        # logging.info(">>>Enlazando nodos")

    logging.info(">>>Finalizado!!!")
