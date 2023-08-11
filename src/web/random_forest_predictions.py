from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from flask import current_app


def get_local_top(city: str, quality_indices):

    tops = dict()



    model: RandomForestClassifier = current_app.local_models[city]

    for number, indices in quality_indices:
        df = pd.json_normalize(indices)

        preds = model.predict_proba(df)

        cat_prob = [(pred, cat) for pred, cat in zip(preds, model.classes_)]

        tops[number] = [x[1] for x in sorted(cat_prob, key=lambda x: x[0], reverse=True)]

    return tops
