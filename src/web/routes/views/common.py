from flask import Blueprint, flash, render_template, request, current_app, redirect, url_for, jsonify, session

from web.dao.placesDAO import PlaceDAO


common_routes = Blueprint("common", __name__, url_prefix='/')

@common_routes.route("/category_net", methods=["GET"])
def get_city_category_net():
    dao = PlaceDAO(current_app.driver)

    cities = dao.get_cities()

    return render_template("category_net.html", cities=cities, usuario=session.get("current_user"))


@common_routes.route('/')
def index():
    return redirect(url_for('common.home'))

@common_routes.route('/home')
def home():
    return render_template("home.html", usuario=session.get("current_user"))
