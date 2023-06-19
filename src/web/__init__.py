import os


from flask import Flask, jsonify, render_template, request, url_for, redirect, session
from configparser import ConfigParser
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity
from .driver_neo4j import init_neo4j

from .dao.place import PlaceDAO
from .routes.accounts import accounts_routes
from .routes.places import places_routes
from .routes.category import categories_routes
from .routes.authentication import role_required
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

    @app.route('/recomendation', methods=["GET", "POST"])
    def recomendation():
        places: list = [int(place) for place in request.args.getlist('place')]

        dao = PlaceDAO(app.driver)

        res = [dao.get_quality_index_permutation(
            id, "Bar", "Burgos") for id in places]

        return jsonify(res)

    @app.route('/map')
    def map():

        placesDAO = PlaceDAO(app.driver)

        ciudades = placesDAO.get_cities()

        return render_template("map.html", cities=ciudades, categories=[], usuario=session.get("current_user"))

    @app.route("/protected")
    @role_required(["admin"])
    def protected():

        return get_jwt_identity()

    return app
