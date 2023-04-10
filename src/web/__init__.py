import os
from flask import Flask, render_template, url_for, redirect
from configparser import ConfigParser
# from driver_neo4j import init_neo4j

def create_app():

    static_folder = os.path.join(os.path.dirname(__file__), ".", "public")
    template_folder = os.path.join(static_folder,"templates" )
    config_folder = os.path.join(os.path.dirname(__file__), '..', 'config')
    app = Flask(__name__, static_url_path='/', static_folder=static_folder, template_folder=template_folder)
    # Neo4j config
    config: ConfigParser = ConfigParser()
    config.read(config_folder+r"\config.ini")
    print(config_folder+"/config.ini")
    neo4j_uri, neo4j_user, neo4j_password = config["neo4j"].values()

    # with app.app_context():
    #     init_neo4j(neo4j_uri, neo4j_user, neo4j_password)

    @app.route('/')
    def index():
        return redirect(url_for('home'))
    
    @app.route('/home')
    def home():
        return render_template("home.html")

    @app.route('/test')
    def test():
        return render_template("test.html")


    return app

if __name__ == "__main__":
    print("hola")
