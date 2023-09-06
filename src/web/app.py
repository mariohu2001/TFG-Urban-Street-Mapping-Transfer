import os
import joblib
import threading
import time
import random

from flask import Flask, jsonify, render_template, request, url_for, redirect, session
from configparser import ConfigParser
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity
from sklearn.ensemble import RandomForestClassifier
from .driver_neo4j import init_neo4j

from .dao.placesDAO import PlaceDAO

from neo4j import Driver, Result

from .routes.views.accounts import accounts_routes
from .routes.places import places_routes
from .routes.category import categories_routes
from .authentication import role_required
from .routes.views.common import common_routes
from .routes.views.maps import map_routes

from .utils import get_city_coords, get_local_rf_model, get_transfer_rf_model
from .quality_indices import get_quality_indices, get_tops

import pandas as pd
import numpy as np

from dotenv import load_dotenv
# from .routes.users import users
# from .routes.common import common
# from driver_neo4j import init_neo4j




def create_app():

    load_dotenv()
    static_folder = os.path.join(os.path.dirname(__file__), ".", "static")
    template_folder = os.path.join(static_folder, "templates")
    app = Flask(__name__, static_url_path='/',
                static_folder=static_folder, template_folder=template_folder)



    app.config.from_mapping(
        NEO4J_URI=os.getenv("NEO4J_URI"),
        NEO4J_USERNAME=os.getenv("NEO4J_USER"),
        NEO4J_PASSWORD=os.getenv("NEO4J_PASSWORD"),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY"),
        JWT_COOKIE_SECURE=False,
        JWT_TOKEN_LOCATION=["cookies"],
        DEFAULT_USER=os.getenv("DEFAULT_USER"),
        DEFAULT_PASSWORD=os.getenv("DEFAULT_PASSWORD"),
        SECRET_KEY=os.getenv("SECRET_KEY")
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

 
    def auradb_maintain():
        driver : Driver = app.driver
        while True:
            with driver.session() as session:
                res : Result = session.run("""
            MATCH (u:User) return {
                role: u.role,
                surname: u.surname,
                name: u.name,
                username:u.user_name
                                           } as prop""")
                for prop in res.value("prop"):
                        print(prop, flush=True)
            time.sleep(random.randint(86400,172800))

    auradb_thread = threading.Thread(target=auradb_maintain)
    auradb_thread.daemon=True
    auradb_thread.start()

    @jwt_required
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

    @jwt_required
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

    @jwt_required
    @app.route("/protected")
    @role_required(["admin"])
    def protected():

        return get_jwt_identity()

    return app



if __name__ == "__main__":
    create_app().run()
