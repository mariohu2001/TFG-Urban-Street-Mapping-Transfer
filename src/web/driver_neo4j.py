from neo4j import GraphDatabase, Driver
from flask import current_app


def init_neo4j(uri: str, username: str, password: str) -> Driver:

    current_app.driver = GraphDatabase.driver(uri, auth=(username, password))

    current_app.driver.verify_connectivity()

    return current_app.driver


def get_driver() -> Driver:
    return current_app.driver


def close_driver():
    if current_app.driver != None:
        current_app.driver.close()
        current_app.driver = None

        return current_app.driver
