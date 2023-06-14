from flask import Blueprint, render_template, request, current_app, redirect, url_for, jsonify, session
from flask_jwt_extended import set_access_cookies, unset_access_cookies
import pyvis.network as netvis
from ..dao.place import PlaceDAO
from ..dao.category import CategoryDAO
from .. import utils
import json


categories_routes = Blueprint("categories", __name__, url_prefix='/')


@categories_routes.route("/categories/nodes/<city>", methods = ["GET"])
def get_city_categories(city: str):
    DAO = CategoryDAO(current_app.driver)

    categories_nodes = list(map(lambda x: x["label"].replace("_", " "),DAO.get_visjs_nodes(city))) 

    return jsonify(categories_nodes)


@categories_routes.route("/categories/edges/<city>", methods=["GET"])
def get_city_categories_edges(city: str):
    DAO = CategoryDAO(current_app.driver)

    categories_edges = DAO.get_visjs_edges(city)

    return jsonify(categories_edges)

@categories_routes.route("/categories/<city>", methods = ["GET"])
def get_categories_by_city(city: str):
    DAO = CategoryDAO(current_app.driver)

    categories = DAO.get_by_city_values_names(city)

    return jsonify(categories)





@categories_routes.route("/category_net/<city>", methods=["GET"])
def get_city_category_net(city: str):
    dao = CategoryDAO(current_app.driver)

    categories = dao.get_visjs_nodes(city)
    categories_edges = dao.get_visjs_edges(city)

    return render_template("category_net.html", nodes=categories, edges=categories_edges)

