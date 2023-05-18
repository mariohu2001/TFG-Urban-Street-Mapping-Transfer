from neo4j import Neo4jDriver, Session, Driver, GraphDatabase, Result
from utils.neo4j_driver import neo4j_driver
import common_queries
import numpy as np

driver: Driver = neo4j_driver


def get_category_tags(city: str):
    with driver.session() as session:
        result: Result = session.run(
            # f"MATCH (n) where n.area = '{city}' RETURN DISTINCT(n.amenity)")
            f"match (n) where n.area = '{city}'unwind labels(n) as lab return distinct(lab)")
        return result.values()


def get_number_of_nodes_category(category: str):
    with driver.session() as session:

        result: Result = session.run(
            f"MATCH (n:{category}) return COUNT(n) as c")
        return result.value("c")[0]


def get_category_numbers_city(category: str, city: str):
    with driver.session() as session:

        result: Result = session.run(
            f"MATCH (n:{category}) where n.area = $city return COUNT(*)", city=city)
        return result.value("COUNT(*)")[0]


def get_n_of_nodes_by_appareance():
    with driver.session() as session:
        result: Result = session.run(f"""MATCH (n:Place) WITH
        [i IN RANGE(0,size(labels(n) ) - 2 )| labels(n)[i] ] as tag, n
        UNWIND tag as amenity
        RETURN amenity, count(n) as count_of_nodes
        ORDER BY count_of_nodes desc""")
        return result.values("amenity", "count_of_nodes")


def calculate_percentile(city: str):

    with driver.session() as session:
        result: Result = session.run(f"""
        MATCH (n:Category)-[r]->(m:Category)
        WHERE n.city = $city and m.city = $city
        return n.name as o, m.name as t, r.sim_value as sims
        """, city=city)

        for i in result.values():

            o_node, t_node, sims = i

            perc_25 = np.percentile(sims, 2.5)
            perc_975 = np.percentile(sims, 97.5)
            std_dev = np.std(sims)
            mean = np.mean(sims)

            session.run(f"""
            MATCH (n:Category)-[r]->(m:Category)
            where n.name = $o_name and m.name = $t_name
            and n.city = $city and m.city = $city
            SET r.perc_25 = $perc_25
            SET r.perc_975 = $perc_975
            SET r.mean = $mean
            SET r.std_dev = $std_dev
            """, city=city, o_name=o_node, t_name=t_node, perc_25=perc_25, perc_975=perc_975, mean=mean, std_dev=std_dev)


def significant_relationships(city: str):

    with driver.session() as session:
        session.run(f"""
        MATCH (n:Place),(m:Place)
        WHERE n.area = $city and m.area = $city and n.category <= m.category
        OPTIONAL MATCH (n)-[r:IS_NEAR]-(m)
        with  n.category as n, m.category as m, count(DISTINCT(r)) as count
        match (p:Category)-[z:Rel]-(q:Category)
        where p.city = $city and q.city=$city
        and p.name = n and q.name = m  
        set z.relevant = (count > z.perc_975 or count < z.perc_25)
        set z.real_value = count
        """, city=city)


def calculate_z_score(city: str):

    with driver.session() as session:
        result: Result = session.run(f"""
            MATCH (n:Category)-[r]->(m:Category)
            WHERE n.city = $city and m.city = $city
            return n.name as o, m.name as t, r.mean as media, r.std_dev as dev, r.real_value as real
            """, city=city)

        for r in result.values():
            origin, target, mean, dev, real = r

            z_score: float = (real - mean)/dev if dev != 0 else 0

            session.run("""
            MATCH (n:Category)-[r]->(m:Category)
            where n.name = $o_name and m.name = $t_name
            and n.city = $city and m.city = $city
            SET r.z_score = $z_score
            """, o_name=origin, t_name=target, city=city, z_score=z_score)


if __name__ == "__main__":
    ciudades = common_queries.obtain_cities()

    for c in ciudades:
        print(c)
        calculate_percentile(c)
    print("Acabados Percentiles")
    for c in ciudades:
        print(c)
        significant_relationships(c)
        calculate_z_score(c)
