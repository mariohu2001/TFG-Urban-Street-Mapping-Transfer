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

    def get_quality_index_permutation(self, id: int, category: str, city: str):

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
            result: Result = session.run(
                cypher_query, id=id, category=category, city=city)

            return result.single().data()

    def get_quality_index_permutation_coords(self, latitude: float, longitude: float, category: str, city: str):
        cypher_query = """
        with point({longitude: $longitude, latitude: $latitude}) AS point, $category as category, $city as city
        match (p:Category)
        where p.city = city and p.name = category
        call
        {
            with p, point
            match (p)-[z:Rel]-(q:Category)
            optional match (n:Place)
            where q.name = n.category and point.distance(point, n.coords) <= 100  
        return count(n) as nei,z.z_score as aij,toFloat(z.real_value)/toFloat(p.n_nodes) as mean ,q
        }
        with aij * (nei-mean) as not_raw, aij * nei as raw
        return sum(not_raw) as Q, sum(raw) as Q_raw
        """

        with self.driver.session() as session:
            result: Result = session.run(
                cypher_query, latitude=latitude, longitude=longitude, category=category, city=city)

            return result.single().data()

    def get_quality_index_jensen(self, id: int, category: str, city: str):

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
            result: Result = session.run(
                cypher_query, id=id, category=category, city=city)

            return result.single().data()

    def get_quality_index_jensen_coords(self, latitude: float, longitude: float, category: str, city: str):
        cypher_query = """
        with point({longitude: $longitude, latitude: $latitude}) AS point, $category as category, $city as city
        match (p:Category)
        where p.city = city and p.name = category
        call
        {
            with p, point
            match (p)-[z:Jensen]->(q:Category), (p)-[r:Rel]-(q)
            optional match (n:Place)
            where q.name = n.category and point.distance(point, n.coords) <= 100  
            return toFloat(log(z.coeff)) as aij, count(n) as nei, toFloat(r.real_value)/toFloat(p.n_nodes) as mean, q

        }

        with aij * (nei-mean) as not_raw, aij * nei as raw
        return sum(not_raw) as Q, sum(raw) as Q_raw
        """

        with self.driver.session() as session:
            result: Result = session.run(
                cypher_query, latitude=latitude, longitude=longitude, category=category, city=city)

            return result.single().data()

    def get_all_quality_indices_place(self, id: int, category: str, city: str):
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
            

            with n,p ,toFloat(log(z.coeff)) as aij_jensen, count(r) as nei_jensen, toFloat(x.real_value)/toFloat(p.n_nodes) as mean_jensen
         with n,p, (aij_jensen * (nei_jensen-mean_jensen)) as not_raw_jensen, (aij_jensen * nei_jensen) as raw_jensen
         with n,p, sum(not_raw_jensen) as sum_not_raw_jensen, sum(raw_jensen) as sum_raw_jensen
         return sum_raw_jensen as Qjensen_raw, sum_not_raw_jensen as Qjensen
        }

        call
        {
            with n,p
            match (m:Place),(p)-[z:Rel]-(q:Category)
            optional match (n)-[r]-(m:Place)
            where m.category = q.name and m <> n
            and m.area = n.area and p.city = q.city
            

         with  n,p ,z.z_score as aij_perm, count(r) as nei_perm, toFloat(z.real_value)/toFloat(p.n_nodes) as mean_perm
         with n,p, (aij_perm* (nei_perm-mean_perm)) as not_raw_perm, (aij_perm * nei_perm) as raw_perm
         with n,p, sum(not_raw_perm) as sum_not_raw_perm, sum(raw_perm) as sum_raw_perm
         return sum_raw_perm as Qperm_raw, sum_not_raw_perm as Qperm
        }
        return n.id as id, n.category as category, Qjensen, Qjensen_raw, Qperm, Qperm_raw
        """

        with self.driver.session() as session:
            result: Result = session.run(
                cypher_query, id=id, category=category, city=city)

            return result.single().data()

    def get_all_quality_indices_coords(self, latitude: float, longitude: float, category: str, city: str):
        cypher_query = """
        with point({longitude: $longitude, latitude: $latitude}) AS point, $category as category, $city as city
        match (p:Category)
        where p.city = city and p.name = category
        call
        {

           with p, point
            match (p)-[z:Rel]-(q:Category)
            optional match (n:Place)
            where q.name = n.category and point.distance(point, n.coords) <= 100  
            with count(n) as nei,z.z_score as aij,toFloat(z.real_value)/toFloat(p.n_nodes) as mean ,q
            with aij * (nei - mean) as not_raw, aij * nei as raw
            return sum(not_raw) as Qperm, sum(raw) as Qperm_raw
        }

        call
        {
           with p, point
            match (p)-[z:Jensen]->(q:Category), (p)-[r:Rel]-(q)
            optional match (n:Place)
            where q.name = n.category and point.distance(point, n.coords) <= 100  

            with toFloat(log(z.coeff)) as aij, count(n) as nei, toFloat(r.real_value)/toFloat(p.n_nodes) as mean, q
            with aij * (nei-mean) as not_raw, aij * nei as raw
        return sum(not_raw) as Qjensen, sum(raw) as Qjensen_raw
        }
        return Qjensen, Qjensen_raw, Qperm, Qperm_raw
        """

        with self.driver.session() as session:
            result: Result = session.run(
                cypher_query, latitude=latitude, longitude=longitude, category=category, city=city)

            return result.single().data()
