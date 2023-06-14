from neo4j import Driver, Result
from .base import baseDAO


class CategoryDAO(baseDAO):

    def all(self):

        cypher_query = f"""
        MATCH (n:Category)
        return n
        """

        with self.driver.session() as session:
            result = session.run(cypher_query)

            return result.data()
        
    def get_by_city_values_names(self, city: str):
        cypher_query = """
        MATCH (n:Category)
        WHERE n.city = $city
        return distinct(n.name) as value, replace(n.name, "_", " ") as name
        """

        with self.driver.session() as session:
            result: Result = session.run(cypher_query, city=city)

            return result.values()

    def get_by_city(self, city: str):
        cypher_query = """
        MATCH (n:Category)
        WHERE n.city = $city
        return distinct(n.name) as name
        """

        with self.driver.session() as session:
            result: Result = session.run(cypher_query, city=city)

            return result.value("name")

    def get_city_categories_edges(self, city: str):
        cypher_query = """
        MATCH (n:Category)-[r]->(m:Category)
        where n.city = $city and m.city = $city
        and r.real_value > 0 and n <> m   
        return n.name as from, r.real_value as interaction, m.name as to
        """

        with self.driver.session() as session:
            result: Result = session.run(cypher_query, city=city)

            return result.data()

    def get_visjs_nodes(self, city: str):
        cypher_query = """
        MATCH (n:Category)
        where n.city = $city
        return id(n) as id, n.name as label
        """

        with self.driver.session() as session:
            result = session.run(cypher_query, city=city).data()

        for node in result:
            node["label"] = node["label"].replace("_", " ")

        return result

    def get_visjs_edges(self, city: str):
        cypher_query = """
        MATCH (n:Category)-[r]->(m:Category)
        where n.city = $city and m.city = $city
        and r.real_value > 0 and n <> m   
        return id(n) as from, r.real_value as value, id(m) as to, toString(r.real_value) as title
        """

        with self.driver.session() as session:
            result: Result = session.run(cypher_query, city=city)

            return result.data()    
