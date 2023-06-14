import logging
from neo4j import Driver, Transaction
from time import time
from utils.neo4j_driver import neo4j_driver
import concurrent.futures
import time
from utils.logger import create_logger
from common_queries import obtain_cities

driver: Driver = neo4j_driver


def create_category_network(tx: Transaction, city: str):
    query = f"""match (n:Place)
    where n.area = $city
    with collect(distinct(n.category)) as tags
    unwind tags as tag
    create (m:Category {{name: tag, city: $city}})
    """
    tx.run(query, city=city)

    tx.run(f"""
    match (n:Category),(m:Category)
    where id(n) <= id(m) and n.city = $city and m.city = $city
    create (n)-[r:Rel {{sim_value : []}}]->(m)
    """, city=city,)




def set_category_info(tx:Transaction, city: str):
    # Obtenemos los valores de interacción reales entre categorías:
    cypher_query = """
    MATCH (n:Place),(m:Place)
        WHERE n.area = $city and m.area = $city and n.category <= m.category
        OPTIONAL MATCH (n)-[r:IS_NEAR]-(m)
        with  n.category as n, m.category as m, count(DISTINCT(r)) as count
        match (p:Category)-[z:Rel]-(q:Category)
        where p.city = $city and q.city=$city
        and p.name = n and q.name = m  
        set z.real_value = count
    """
    tx.run(cypher_query, city=city)


    # Obtenemos los promedios de vecinos entre categorías
    cypher_query = """
    MATCH (p:Category)
    where p.city = $city
    // Obtenemos n nodos
    CALL {
        with p
        match (n:Place)
        where n.area = p.city and n.category = p.name
        return count(distinct(n)) as total_p
    }
    set p.n_nodes = total_p
    """
    tx.run(cypher_query, city=city)



if __name__ == "__main__":

    cities = obtain_cities()
    with driver.session() as session:
        for c in cities:
            print(c)
            session.execute_write(create_category_network, c)
            session.execute_write(set_category_info, c)
    
