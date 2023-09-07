from flask import Blueprint, flash, render_template, request, current_app, redirect, url_for, jsonify, session, abort
from flask_jwt_extended import jwt_required, get_jwt
from ...dao.placesDAO import PlaceDAO
from ...dao.categoryDAO import CategoryDAO
from ...utils import get_city_coords

map_routes = Blueprint("maps", __name__, url_prefix='/')


@map_routes.route('/recomendation/<city>', methods=["GET", "POST"])
@jwt_required()
def recomendation(city: str):
    dao = PlaceDAO(current_app.driver)
    if city not in dao.get_cities():
        abort(404)
    try:
        places: list = [int(place) for place in request.args.getlist('place')]

        coords: list = [tuple(coord.split(":"))
                        for coord in request.args.getlist('coords')]

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
        catsDAO = CategoryDAO(current_app.driver)
        categories = catsDAO.get_by_city(city)
        categories = [[cat, cat.replace("_", " ")]for cat in categories]
        city_coords = get_city_coords(city)
    except:
        abort(400)
    return render_template("recomendations.html", usuario=session.get("current_user"),
                           nodos=nodos, nodosCoords=coords_markers, city=city, coords=list(
        city_coords.values()), categories=categories)


@map_routes.route('/top/<city>')
@jwt_required()
def best_category(city: str):
    dao = PlaceDAO(current_app.driver)
    if city not in dao.get_cities():
        abort(404)
    try:
        places: list = [int(place) for place in request.args.getlist('place')]

        coords: list = [tuple(coord.split(":"))
                        for coord in request.args.getlist('coords')]
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
    except:
        abort(400)
    return render_template("topCategories.html", usuario=session.get("current_user"),
                           nodos=nodos, nodosCoords=coords_markers, city=city, coords=list(
        city_coords.values()))


@map_routes.route('/map')
def map():

    placesDAO = PlaceDAO(current_app.driver)

    ciudades = placesDAO.get_cities()

    return render_template("map.html", cities=ciudades, categories=[], usuario=session.get("current_user"))


@map_routes.route('/transfer/<city>')
@jwt_required()
def transfer_recomendation(city: str):
    dao = PlaceDAO(current_app.driver)
    if city not in dao.get_cities():
        abort(404)
    try:
        places: list = [int(place) for place in request.args.getlist('place')]

        coords: list = [tuple(coord.split(":"))
                        for coord in request.args.getlist('coords')]

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
        cities = dao.get_cities()
        cities.remove(city)
    except:
        abort(400)
    return render_template("transfer.html", nodos=nodos, city=city, cities=cities,
                           coords=list(city_coords.values()), nodosCoords=coords_markers, usuario=session.get("current_user"))
