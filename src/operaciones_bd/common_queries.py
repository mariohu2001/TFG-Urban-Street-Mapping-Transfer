from typing import List
from utils.neo4j_driver import neo4j_driver
from neo4j import Result


def obtain_cities():

    with neo4j_driver.session() as session:
        cities: Result = session.run(f"""
        MATCH (n:Place)
        return distinct(n.area) as cities
        """)
        return cities.value('cities')



