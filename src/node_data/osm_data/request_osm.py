from OSMPythonTools.overpass import Overpass, overpassQueryBuilder, OverpassResult
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.element import Element
from node_data.osm_data.osm_exception import InvalidCityNameException


import json


_nominatim_api = Nominatim()
_overpass_api = Overpass()


def get_osm_elements(city: str, elements=["node", "way", "relation"], selector=[], out=["body"], timeout=1000) -> OverpassResult:
    areaId: str = _nominatim_api.query(city).areaId()
    if areaId == "":
        raise InvalidCityNameException(f"La ciudad con nombre {city} no existe o no tiene un area Id")
    query = overpassQueryBuilder(
        area=areaId, elementType=elements, selector=selector, out=out)
    return _overpass_api.query(query, timeout=timeout)


# def get_osm_elements(city="", elements=["node", "way", "relation"], selector=[], out=["body"], timeout=1000):
#     areaId = _nominatim_api.query(city).areaId()
#     query = overpassQueryBuilder(
#         area=areaId, elementType=elements, selector=selector, out=out)
#     return _overpass_api.query(query, timeout=timeout)


# result = get_osm_elements(city="Comunidad de Madrid", selector=["natural","amenity"])
