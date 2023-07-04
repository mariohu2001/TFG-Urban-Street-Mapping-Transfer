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
        return distinct(n.name) as value, replace(n.name, "_", " ") as name order by name
        """

        with self.driver.session() as session:
            result: Result = session.run(cypher_query, city=city)

            return result.values()

    def get_by_city(self, city: str):
        cypher_query = """
        MATCH (n:Category)
        WHERE n.city = $city
        return distinct(n.name) as name order by name
        """

        with self.driver.session() as session:
            result: Result = session.run(cypher_query, city=city)

            return result.value("name")

    def get_city_categories_edges(self, city: str):
        cypher_query = """
        MATCH (n:Category)-[r:Rel]->(m:Category)
        where n.city = $city and m.city = $city
        and r.real_value > 0 and n <> m   
        return n.name as from, r.real_value as interaction, m.name as to
        """

        with self.driver.session() as session:
            result: Result = session.run(cypher_query, city=city)

            return result.data()

    def get_visjs_nodes(self, city: str):
        cypher_query = """
        MATCH (n:Category)-[r:Rel]-()
        where n.city = $city
        return id(n) as id, replace(n.name,"_"," ") as label, sum(r.real_value) as value, toString(n.n_nodes) + " nodes" as title,
        n.type as group
        """

        with self.driver.session() as session:
            result = session.run(cypher_query, city=city).data()

        for node in result:
            node["label"] = node["label"].replace("_", " ")

        return result

    def get_visjs_edges(self, city: str):
        cypher_query = """
        MATCH (n:Category)-[r:Rel]->(m:Category)
        where n.city = $city and m.city = $city
        and r.real_value > 0 and n <> m   
        return id(n) as from, r.real_value as value, id(m) as to,replace(n.name, "_", " ")+" - "+replace(m.name, "_", " ")+": "+ toString(r.real_value) as title
        """

        with self.driver.session() as session:
            result: Result = session.run(cypher_query, city=city)

            return result.data()   


    def get_intersection_categories_between_cities(self, city_1: str, city_2: str) :
        cypher_query = """
        match (c:Category) where c.city = $city_1
        with collect(c.name) as cats
        match (q:Category)
        where q.name in cats and q.city = $city_2
        return q.name as value, replace(q.name, "_", " ") as name order by name
        """

        with self.driver.session() as session:
            result : Result = session.run(cypher_query, city_1=city_1, city_2=city_2)

            return result.values()