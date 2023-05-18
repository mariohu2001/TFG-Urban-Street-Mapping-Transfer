from OSMPythonTools.overpass import Overpass, OverpassResult, overpassQueryBuilder
from OSMPythonTools.nominatim import Nominatim, NominatimResult


def get_city_coords(city):
    nominatim = Nominatim()
    overpass = Overpass()

    area = nominatim.query(city, countrycode="ES").areaId()

    query = overpassQueryBuilder(
        area=area, elementType="node", selector='"place"="city"')

    result: OverpassResult = overpass.query(query)

    node = result.elements()[0]

    return {"lat": node.lat(), "lon": node.lon()}
