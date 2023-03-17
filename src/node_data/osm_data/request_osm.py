import json

from OSMPythonTools.element import Element
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import (Overpass, OverpassResult,
                                     overpassQueryBuilder)

from node_data.osm_data.osm_exception import InvalidCityNameException

_nominatim_api = Nominatim()
_overpass_api = Overpass()


def get_osm_elements(
    city: str,
    elements=["node", "way", "relation"],
    selector=[],
    out=["body"],
    timeout=1000,
) -> OverpassResult:
    areaId: str = _nominatim_api.query(city).areaId()
    if areaId == "":
        raise InvalidCityNameException(
            f"La ciudad con nombre {city} no existe o no tiene un area Id"
        )
    query = overpassQueryBuilder(
        area=areaId, elementType=elements, selector=selector, out=out
    )
    return _overpass_api.query(query, timeout=timeout)



