from flask import Blueprint, render_template, request, current_app, redirect, url_for, jsonify, session, abort
from flask_jwt_extended import jwt_required
from ..dao.placesDAO import PlaceDAO
from ..dao.categoryDAO import CategoryDAO
from .. import utils
from ..quality_indices import get_quality_indices
import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

places_routes = Blueprint("places", __name__, url_prefix='/')


@places_routes.route("/places/<city>", methods=["GET"])
def get_city_places(city: str):

    details = bool(request.args.get("details", False))
    dao = PlaceDAO(current_app.driver)

    places = dao.get_by_city(city, details=details)

    return jsonify(places)


@places_routes.route("/places/<city>/<category>", methods=["GET"])
def get_city_category_places(city: str, category: str):
    details = bool(request.args.get("details", False))
    dao = PlaceDAO(current_app.driver)

    places = dao.get_by_city_and_category(
        city=city, category=category, details=details)

    return jsonify(places)


@places_routes.route("/place/<id>", methods=["GET"])
def get_place_by_id(id: str):

    dao = PlaceDAO(current_app.driver)

    place = dao.get_by_id(id)

    return jsonify(place)

@places_routes.route("/quality_indices/permutation/<string:city>/<string:category>/<int:id>")
@jwt_required()
def get_quality_indices_permutation(id: int, city: str, category: str):

    dao = PlaceDAO(current_app.driver)

    quality_indices = dao.get_quality_index_permutation(id, category, city)

    return jsonify(quality_indices)

@places_routes.route("/quality_indices/jensen/<string:city>/<string:category>/<int:id>")
@jwt_required()
def get_quality_indices_jensen(id: int, city: str, category: str):

    dao = PlaceDAO(current_app.driver)

    quality_indices = dao.get_quality_index_jensen(id, category, city)

    return jsonify(quality_indices)

@places_routes.route("/quality_indices/jensen/<string:city>/<string:category>/<string:coords>")
@jwt_required()
def get_quality_indices_jensen_coords(coords: str, city: str, category: str):

    dao = PlaceDAO(current_app.driver)

    try:
        lat, lon = coords.split(":")

        quality_indices = dao.get_quality_index_jensen_coords(float(lat), float(lon), category, city)
    except:
        abort(400, "Formato incorrecto")
    return jsonify(quality_indices)

@places_routes.route("/quality_indices/permutation/<string:city>/<string:category>/<string:coords>")
@jwt_required()
def get_quality_indices_permutation_coords(coords: str, city: str, category: str):

    dao = PlaceDAO(current_app.driver)

    try:
        lat, lon = coords.split(":")

        quality_indices = dao.get_quality_index_permutation_coords(float(lat), float(lon), category, city)
    except:
        abort(400, "Formato incorrecto")

    return jsonify(quality_indices)

@places_routes.route("/quality_indices/all/<string:city>/<string:category>/<string:coords>")
@jwt_required()
def get_all_quality_indices_coords(coords: str, city: str, category: str):
    
    dao = PlaceDAO(current_app.driver)

    try:
        lat, lon = coords.split(":")

        quality_indices = dao.get_all_quality_indices_coords(float(lat), float(lon), category, city)
    except:
        abort(400, "Formato incorrecto")
    return jsonify(quality_indices)


@places_routes.route("/quality_indices/all/<string:city>", methods=["POST"])
def get_quality_indices_api(city: str):
        body = request.get_json()
        places = body.get("places")
        coords = body.get("coords")

        response = get_quality_indices(city=city, places=places, coords=coords, driver=current_app.driver)
        model : RandomForestClassifier = utils.get_local_rf_model(city)

        for k,coord in response["coords"].items():
            data = {"QualityIndices": coord}
            data = pd.json_normalize(data)
            data = data[model.feature_names_in_]

            probs = [ [i,j] for i,j in zip(list(model.predict_proba(data).ravel()), list(model.classes_))]
            for probi, probj in probs:
                response["coords"][k][probj]["random_forest"] = probi

        for k,coord in response["places"].items():
            data = {"QualityIndices": coord}
            data = pd.json_normalize(data)
            data = data[model.feature_names_in_]
            probs = [ [i,j] for i,j in zip(list(model.predict_proba(data).ravel()), list(model.classes_))]
            for probi, probj in probs:
                response["places"][k][probj]["random_forest"] = probi

        return jsonify(response)


@places_routes.route("/quality_indices/all/<string:city>/<string:category>/<int:id>")
@jwt_required()
def get_all_quality_indices_place(id: int, city: str, category: str):
    dao = PlaceDAO(current_app.driver)

    quality_indices = dao.get_all_quality_indices_place(id, category, city)

    return jsonify(quality_indices)

@places_routes.route("/coords/<city>", methods=["GET"])
def get_city_coords(city: str):
    return utils.get_city_coords(city)


    





