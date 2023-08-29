from typing import List
from utils.neo4j_driver import neo4j_driver
from neo4j import Result


def get_cities():

    with neo4j_driver.session() as session:
        cities: Result = session.run(f"""
        MATCH (n:Place)
        return distinct(n.area) as cities
        """)
        return cities.value('cities')
    
def get_categories(city: str):

    with neo4j_driver.session() as session:
        categories: Result = session.run("""
        match (n:Place)
        where n.area = $city
        return distinct(n.category) as categories order by categories
        """, city=city)

        return categories.value("categories")
    
def get_city_places_ids(city: str):

    with neo4j_driver.session() as session:
        ids : Result = session.run("""
        MATCH (n:Place)
        WHERE n.area = $city
        RETURN id(n) as ids
        """, city=city)

        return ids.value("ids")



