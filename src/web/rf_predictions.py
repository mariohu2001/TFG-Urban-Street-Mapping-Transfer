from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from flask import current_app

from .utils import get_local_rf_model, get_transfer_rf_model, transform_transfer_dataset


def get_local_top(city: str, quality_indices):

    tops = dict()

    model: RandomForestClassifier = get_local_rf_model(city)

    for number, indices in quality_indices:
        df = pd.json_normalize(indices)

        preds = model.predict_proba(df)

        cat_prob = [(pred, cat) for pred, cat in zip(preds, model.classes_)]

        tops[number] = [x[1]
                        for x in sorted(cat_prob, key=lambda x: x[0], reverse=True)]

    return tops


def get_transfer_top(source_city: str, target_city: str, quality_indices):
    tops = dict()

    model: RandomForestClassifier = get_transfer_rf_model(
        source_city, target_city)
    
    dataset = transform_transfer_dataset(quality_indices, model)

    preds = model.predict_proba(dataset)

    

