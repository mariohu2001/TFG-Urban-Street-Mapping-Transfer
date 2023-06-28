from neo4j import Driver, Result
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
            RETURN n.id as id, replace(n.category, "_", " ") as category, n.coords as coords, n.name as name
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
            RETURN n.id as id, replace(n.category, "_", " ") as category, n.coords as coords, n.name as name

            """

        with self.driver.session() as session:
            result = session.run(cypher_query, city=city, category=category)
            if details:
                return [r.get("n") for r in result]


            return result.data()
        

    def get_cities(self):
        cypher_query = """
        MATCH (n:Place)
        RETURN DISTINCT(n.area) as ciudades order by ciudades
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
        RETURN properties(n) as props
        """
        with self.driver.session() as session:
            result: Result = session.run(cypher_query, id=id)

            return result.single().get(key="props")


    def get_quality_index_permutation(self, id: int, category: str, city : str):

        cypher_query = """
        match (n:Place), (p:Category)
        where n.id = $id
        and  p.city = $city and p.name = $category
        call
        {
            with n,p
            match (m:Place),(p)-[z:Rel]-(q:Category)
            optional match (n)-[r]-(m:Place)
            where m.category = q.name and m <> n
            and m.area = n.area and p.city = q.city
            

            return z.z_score as aij, count(r) as nei, toFloat(z.real_value)/toFloat(p.n_nodes) as mean
        }

        with n,p,(aij* (nei-mean)) as not_raw, (aij * nei) as raw
        with n,p, sum(not_raw) as sum_not_raw, sum(raw) as sum_raw
        with n, sum_not_raw as Qperm, sum_raw as Qperm_raw
        return n.id as id, n.category as category ,Qperm as Q, Qperm_raw as Q_raw
        """

        with self.driver.session() as session:
            result: Result = session.run(cypher_query, id=id, category=category, city=city)

            return result.data()
        

    def get_quality_index_jensen(self, id: int, category: str, city : str):

        cypher_query = """
        match (n:Place), (p:Category)
        where n.id = $id
        and  p.city = $city and p.name = $category
        call
        {
            with n,p
            match (m:Place),(p)-[z:Jensen]->(q:Category),(p)-[x:Rel]-(q)
            optional match (n)-[r]-(m:Place)
            where m.category = q.name and m <> n
            and m.area = n.area and p.city = q.city
            

            return toFloat(log(z.coeff)) as aij, count(r) as nei, toFloat(x.real_value)/toFloat(p.n_nodes) as mean
        }

        with n,p,(aij* (nei-mean)) as not_raw, (aij * nei) as raw
        with n,p, sum(not_raw) as sum_not_raw, sum(raw) as sum_raw
        with n, sum_not_raw as Qjensen, sum_raw as Qjensen_raw
        return n.id as id, n.category as category ,toFloat(Qjensen) as Q, toFloat(Qjensen_raw) as Q_raw
        """

        with self.driver.session() as session:
            result: Result = session.run(cypher_query, id=id, category=category, city=city)

            return result.data()
    

