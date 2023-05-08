import os
from flask import Flask, render_template, url_for, redirect, session
from configparser import ConfigParser
from flask_jwt_extended import JWTManager, jwt_required
from .driver_neo4j import init_neo4j


from .routes.accounts import accounts_routes
from .routes.places import places_routes
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

    @app.route('/')
    def index():
        return redirect(url_for('home'))

    @app.route('/home')
    def home():
        print(session.get("is_logged"),session.get("current_user"))
        return render_template("home.html", usuario=session.get("current_user"), logged=session.get("is_logged"))

    @app.route('/test')
    def test():
        return render_template("test.html")

    @app.route('/map')
    def map():
        return render_template("map.html")

    @app.route("/protected")
    @jwt_required()
    def protected():

        return "protegido"

    return app
