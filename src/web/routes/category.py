from flask import Blueprint, render_template, request, current_app, redirect, url_for, jsonify, session
from flask_jwt_extended import set_access_cookies, unset_access_cookies
from ..dao.placesDAO import PlaceDAO
from ..dao.categoryDAO import CategoryDAO
from .. import utils
import json


categories_routes = Blueprint("categories", __name__, url_prefix='/')


@categories_routes.route("/categories/nodes/<city>", methods=["GET"])
def get_city_categories(city: str):
    DAO = CategoryDAO(current_app.driver)

    categories_nodes = DAO.get_visjs_nodes(city)

    return jsonify(categories_nodes)


@categories_routes.route("/categories/edges/<city>", methods=["GET"])
def get_city_categories_edges(city: str):
    DAO = CategoryDAO(current_app.driver)

    categories_edges = DAO.get_visjs_edges(city)

    return jsonify(categories_edges)


@categories_routes.route("/categories/<city>", methods=["GET"])
def get_categories_by_city(city: str):
    DAO = CategoryDAO(current_app.driver)

    categories = DAO.get_by_city_values_names(city)

    return jsonify(categories)


@categories_routes.route("/categories/<city1>/<city2>")
def get_categories_intersection(city1: str, city2: str):
    DAO = CategoryDAO(current_app.driver)

    categories = DAO.get_intersection_categories_between_cities(city1, city2)

    return jsonify(categories)


@categories_routes.route("/network/<city>")
def get_category_net_components(city: str):
    dao = CategoryDAO(current_app.driver)

    nodes = dao.get_visjs_nodes(city)
    edges = dao.get_visjs_edges(city)

    return jsonify({"nodes": nodes, "edges": edges})
