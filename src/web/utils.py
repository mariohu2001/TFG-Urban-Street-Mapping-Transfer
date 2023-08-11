import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from OSMPythonTools.overpass import Overpass, OverpassResult, overpassQueryBuilder
from OSMPythonTools.nominatim import Nominatim, NominatimResult
from neo4j import Driver
from flask import current_app

def get_city_coords(city):
    nominatim = Nominatim()
    overpass = Overpass()

    area = nominatim.query(city, countrycode="ES").areaId()

    query = overpassQueryBuilder(
        area=area, elementType="node", selector='"place"="city"')

    result: OverpassResult = overpass.query(query)

    node = result.elements()[0]

    return {"lat": node.lat(), "lon": node.lon()}


# def get_top_city_random_forest(city:str, quality_indices: dict):

#     model: RandomForestClassifier = current_app.local_models[city]

#     data = pd.json_normalize(quality_indices)

#     probs = model.predict_proba(data)

#     ranking = [ [category, prob] for category, prob in zip(model.classes_, probs)]

#     ranking.sort(key=lambda x: x[1])


#     return [rank[0] for rank in ranking ]


# def get_top_city_random_forest_transfer(city:str, quality_indices: dict):

#     model: RandomForestClassifier = current_app.transfer_model

#     data = pd.json_normalize(quality_indices)

#     probs = model.predict_proba(data)

#     ranking = [ [category, prob] for category, prob in zip(model.classes_, probs)]

#     ranking.sort(key=lambda x: x[1])


#     return [rank[0] for rank in ranking ]




