from neo4j import Driver
from .base import baseDAO

class PlaceDAO(baseDAO):

    def all(self):

        cypher_query = f"""
        MATCH (n:Place)
        return n
        """

        with self.driver.session() as session:
            result = session.run(cypher_query)

            return result

    def get_by_city(self, city: str, details: bool = False):

        cypher_query = """
        MATCH (n:Place)
        WHERE n.area = $city
        """

        if details:
            cypher_query += """
            RETURN properties(n) as n
            """
        else:
            cypher_query += """
            RETURN n.id as id, n.category as category, n.coords as coords
            """

        with self.driver.session() as session:
            result = session.run(cypher_query, city=city)
            if details:
                return [r.get("n") for r in result]

            return result.data()

    def get_by_city_and_category(self, city: str, category: str, details: bool = False):

        cypher_query = f"""
        MATCH (n:Place)
        WHERE n.area = $city and n.category = $category
        """

        if details:
            cypher_query += """
            RETURN properties(n)
            """
        else:
            cypher_query += """
            RETURN n.id as id, replace(n.category, "_", " ") as category, n.coords as coords

            """

        with self.driver.session() as session:
            result = session.run(cypher_query, city=city, category=category)
            if details:
                return [r.get("n") for r in result]


            return result.data()
        

    def get_cities(self):
        cypher_query = """
        MATCH (n:Place)
        RETURN DISTINCT(n.area) as ciudades
        """
        with self.driver.session() as session:
            result = session.run(cypher_query)
            return result.value("ciudades")
        
    def get_categories(self):
        cypher_query = """
        MATCH (n:Place)
        RETURN DISTINCT(n.category) as category
        """
        with self.driver.session() as session:
            result = session.run(cypher_query)
            return result.value("category")


    def get_by_id(self, id: str):

        cypher_query = """
        MATCH (n:Place)
        WHERE n.id = $id
        RETURN n
        """
        with self.driver.session() as session:
            result = session.run(cypher_query, id=id)
            return result.single().get("n")
