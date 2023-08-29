import os
import joblib

from flask import Flask, jsonify, render_template, request, url_for, redirect, session
from configparser import ConfigParser
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity
from sklearn.ensemble import RandomForestClassifier
from .driver_neo4j import init_neo4j

from .dao.place import PlaceDAO

from .routes.views.accounts import accounts_routes
from .routes.places import places_routes
from .routes.category import categories_routes
from .routes.authentication import role_required
from .routes.views.common import common_routes
from .routes.views.maps import map_routes

from .utils import get_city_coords, get_local_rf_model, get_transfer_rf_model
from .calculate_quality_indices import get_quality_indices, get_tops

from sklearn.decomposition import PCA
import pandas as pd
import plotly.express as px
import numpy as np
# from .routes.users import users
# from .routes.common import common
# from driver_neo4j import init_neo4j


def create_app():

    static_folder = os.path.join(os.path.dirname(__file__), ".", "static")
    template_folder = os.path.join(static_folder, "templates")
    config_folder = os.path.join(os.path.dirname(__file__), '..', 'config')
    app = Flask(__name__, static_url_path='/',
                static_folder=static_folder, template_folder=template_folder)

    # Neo4j config
    config: ConfigParser = ConfigParser()
    config.read(config_folder+r"\config.ini")
    neo4j_uri, neo4j_user, neo4j_password = config["neo4j"].values()
    default_user, default_password = config["users"].values()

    app.config.from_mapping(
        NEO4J_URI=neo4j_uri,
        NEO4J_USERNAME=neo4j_user,
        NEO4J_PASSWORD=neo4j_password,
        JWT_SECRET_KEY=config["jwt"]["jwt_secret_key"],
        JWT_COOKIE_SECURE=False,
        JWT_TOKEN_LOCATION=["cookies"],
        DEFAULT_USER=default_user,
        DEFAULT_PASSWORD=default_password,
        SECRET_KEY=config["flask"]["secret_key"]
    )

    with app.app_context():
        init_neo4j(
            app.config.get('NEO4J_URI'),
            app.config.get('NEO4J_USERNAME'),
            app.config.get('NEO4J_PASSWORD'),
        )

        jwt = JWTManager(app)

    app.register_blueprint(accounts_routes)
    app.register_blueprint(places_routes)
    app.register_blueprint(categories_routes)
    app.register_blueprint(common_routes)
    app.register_blueprint(map_routes)

    @app.route('/test')
    def test():

        dao = PlaceDAO(app.driver)
        return jsonify(dao.get_quality_index_permutation([2, 3], "Bar", "Ciudad"), usuario=session.get("current_user"))

    @app.route('/tops', methods=['POST'])
    def get_places_tops():
        body = request.get_json()

        places = body.get("places")
        coords = body.get("coords")
        city = body.get("city")
        model: RandomForestClassifier = get_local_rf_model(city)
        tops = get_tops(coords, places, city, app.driver, model)
        del (model)
        return jsonify(tops)

    @app.route('/tops/transfer', methods=['POST'])
    def get_transfer_tops():
        body = request.get_json()

        source_city = body.get("source")
        target_city = body.get("target")
        places = body.get("places")
        coords = body.get("coords")
        model: RandomForestClassifier = get_transfer_rf_model(
            source_city, target_city)

        tops = get_tops(coords, places, target_city, app.driver, model)
        del (model)

        return jsonify(tops)

    @app.route('/pca', methods=["POST"])
    def quality_indices_pca():
        datos = request.get_json()

        print(datos, type(datos), type(datos[0]))

        data_df = pd.DataFrame(datos)

        pca = PCA(n_components=2)

        # features = { feature for row in datos for feature in row.keys() }
        features = ["Qjensen", "Qjensen_raw",
                    "Qpermutation", "Qpermutation_raw"]

        components = pca.fit_transform(data_df[features])

        loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

        fig = px.scatter(components, x=0, y=1)

        for i, feature in enumerate(features):
            fig.add_annotation(
                ax=0, ay=0,
                axref="x", ayref="y",
                x=loadings[i, 0],
                y=loadings[i, 1],
                showarrow=True,
                arrowsize=2,
                arrowhead=2,
                xanchor="right",
                yanchor="top"
            )
            fig.add_annotation(
                x=loadings[i, 0],
                y=loadings[i, 1],
                ax=0, ay=0,
                xanchor="center",
                yanchor="bottom",
                text=feature,
                yshift=5,
            )
        fig.show()

        # print(components.tolist(), type(components.tolist()))
        print(jsonify(components.tolist()))
        return jsonify(components.tolist())

    @app.route("/protected")
    @role_required(["admin"])
    def protected():

        return get_jwt_identity()

    return app
