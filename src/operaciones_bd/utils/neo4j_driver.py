from neo4j import Driver, GraphDatabase
from .get_config import get_conf_values


_uri, _user, _password = get_conf_values("neo4j")


neo4j_driver :Driver = GraphDatabase.driver(_uri, auth=(_user, _password))


