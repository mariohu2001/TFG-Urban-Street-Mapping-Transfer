from flask import Blueprint, render_template, request, current_app, redirect, url_for, jsonify, session
from flask_jwt_extended import set_access_cookies, unset_access_cookies
import pyvis.network as netvis
from ..dao.place import PlaceDAO
from ..dao.category import CategoryDAO
from .. import utils
import json

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
def get_quality_indices_permutation(id: int, city: str, category: str):

    dao = PlaceDAO(current_app.driver)

    quality_indices = dao.get_quality_index_permutation(id, category, city)

    return jsonify(quality_indices)

@places_routes.route("/coords/<city>", methods=["GET"])
def get_city_coords(city: str):
    return utils.get_city_coords(city)





