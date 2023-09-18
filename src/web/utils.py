import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from OSMPythonTools.overpass import Overpass, OverpassResult, overpassQueryBuilder
from OSMPythonTools.nominatim import Nominatim, NominatimResult
from neo4j import Driver
import joblib
import os

path : str = os.path.abspath(__file__)

def get_city_coords(city):
    nominatim = Nominatim()
    overpass = Overpass()

    area = nominatim.query(city, countrycode="ES").areaId()

    query = overpassQueryBuilder(
        area=area, elementType="node", selector='"place"="city"')

    result: OverpassResult = overpass.query(query)

    node = result.elements()[0]

    return {"lat": node.lat(), "lon": node.lon()}


def get_local_rf_model(city: str) -> RandomForestClassifier:
    models_path = f"{os.path.dirname(path)}/models/local/{city}.gz"

    model: RandomForestClassifier = joblib.load(models_path)

    return model


def get_transfer_rf_model(source_city: str, target_city: str) -> RandomForestClassifier:
    model_path: str = f"{os.path.dirname(path)}/models/transfer/{source_city}-{target_city}.gz"
    model: RandomForestClassifier = joblib.load(model_path)

    return model


def transform_transfer_dataset(quality_indices, model: RandomForestClassifier) -> pd.DataFrame:



    df =  pd.json_normalize({"QualityIndices": quality_indices})
    df_final_data : pd.DataFrame = df[model.feature_names_in_]

    return df_final_data


