from flask import Blueprint, flash, render_template, request, current_app, redirect, url_for, jsonify, session

from web.dao.placesDAO import PlaceDAO
from web.utils import get_city_coords

map_routes = Blueprint("maps",__name__, url_prefix='/')



@map_routes.route('/recomendation/<city>', methods=["GET", "POST"])
def recomendation(city: str):
    places: list = [int(place) for place in request.args.getlist('place')]

    coords: list = [tuple(coord.split(":"))
                    for coord in request.args.getlist('coords')]
    dao = PlaceDAO(current_app.driver)

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

@map_routes.route('/top/<city>')
def best_category(city: str):
    places: list = [int(place) for place in request.args.getlist('place')]

    coords: list = [tuple(coord.split(":"))
                    for coord in request.args.getlist('coords')]
    dao = PlaceDAO(current_app.driver)

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

@map_routes.route('/map')
def map():

    placesDAO = PlaceDAO(current_app.driver)

    ciudades = placesDAO.get_cities()

    return render_template("map.html", cities=ciudades, categories=[], usuario=session.get("current_user"))


@map_routes.route('/transfer/<city>')
def transfer_recomendation(city: str):

    places: list = [int(place) for place in request.args.getlist('place')]

    coords: list = [tuple(coord.split(":"))
                    for coord in request.args.getlist('coords')]
    dao = PlaceDAO(current_app.driver)

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
