import os
import joblib

from flask import Flask, jsonify, render_template, request, url_for, redirect, session
from configparser import ConfigParser
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity
from .driver_neo4j import init_neo4j

from .dao.place import PlaceDAO

from .routes.accounts import accounts_routes
from .routes.places import places_routes
from .routes.category import categories_routes
from .routes.authentication import role_required


from .utils import get_city_coords
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

        print(">>> Cargando modelos")
        app.local_models = joblib.load("web/models/local/local.gz")
        app.transfer_model = joblib.load("web/models/transfer/transfer.gz")
        print(">>> Finalizado cargando modelos")
        jwt = JWTManager(app)

    app.register_blueprint(accounts_routes)
    app.register_blueprint(places_routes)
    app.register_blueprint(categories_routes)

    @app.route('/')
    def index():
        return redirect(url_for('home'))

    @app.route('/home')
    def home():
        print(session.get("current_user"))
        return render_template("home.html", usuario=session.get("current_user"))

    @app.route('/test')
    def test():

        dao = PlaceDAO(app.driver)
        return jsonify(dao.get_quality_index_permutation([2, 3], "Bar", "Ciudad"), usuario=session.get("current_user"))

    @app.route('/recomendation/<city>', methods=["GET", "POST"])
    def recomendation(city: str):
        places: list = [int(place) for place in request.args.getlist('place')]

        coords: list = [tuple(coord.split(":"))
                        for coord in request.args.getlist('coords')]
        dao = PlaceDAO(app.driver)

        nodos = {}

        marker_index = 1
        for p in places:
            nodos[marker_index] = dao.get_by_id(p)
            marker_index += 1

        coords_markers = {}
        for c in coords:
            coords_markers[marker_index] = {
                "lat": float(c[0]),
                "lon": float(c[1]),
                "category": "Coords",
                "area": city
            }
            marker_index += 1

        city_coords = get_city_coords(city)

        return render_template("recomendations.html", usuario=session.get("current_user"),
                               nodos=nodos, nodosCoords=coords_markers, city=city, coords=list(
                                   city_coords.values()),
                               metrics=["permutation", "jensen"])

    @app.route('/top/<city>')
    def best_category(city: str):
        places: list = [int(place) for place in request.args.getlist('place')]

        coords: list = [tuple(coord.split(":"))
                        for coord in request.args.getlist('coords')]
        dao = PlaceDAO(app.driver)

        nodos = {}
        coords_markers = {}
        marker_index = 1

        for p in places:
            nodos[marker_index] = (dao.get_by_id(p))
            marker_index += 1
        for c in coords:
            coords_markers[marker_index] = {
                "lat": float(c[0]),
                "lon": float(c[1]),
                "category": "Coords",
                "area": city
            }
            marker_index += 1
            
        city_coords = get_city_coords(city)
        return render_template("topCategories.html",usuario=session.get("current_user"),
                               nodos=nodos, nodosCoords=coords_markers, city=city, coords=list(
                                   city_coords.values()))

    @app.route('/tops', methods=['POST'])
    def get_places_tops():
        body = request.get_json()

        places = body.get("places")
        coords = body.get("coords")
        city = body.get("city")

        tops = get_tops(coords, places, city, app.driver, app.local_models[city])
        return jsonify(tops)

    @app.route('/map')
    def map():

        placesDAO = PlaceDAO(app.driver)

        ciudades = placesDAO.get_cities()

        return render_template("map.html", cities=ciudades, categories=[], usuario=session.get("current_user"))

    @app.route('/transfer/<city>')
    def transfer_recomendation(city: str):

        places: list = [int(place) for place in request.args.getlist('place')]

        coords: list = [tuple(coord.split(":"))
                        for coord in request.args.getlist('coords')]
        dao = PlaceDAO(app.driver)

        nodos = []

        for p in places:
            nodos.append(dao.get_by_id(p))

        coords_markers = []
        for c in coords:
            coords_markers.append({
                "lat": float(c[0]),
                "lon": float(c[1]),
                "category": "Coords",
                "area": city
            })

        city_coords = get_city_coords(city)
        cities = dao.get_cities()
        cities.remove(city)
        return render_template("transfer.html", nodos=nodos, city=city, cities=cities,
                               coords=list(city_coords.values()), nodosCoords=coords_markers, usuario=session.get("current_user"))

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
