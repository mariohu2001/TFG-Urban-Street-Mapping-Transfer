import logging
from neo4j import Driver, Transaction
from time import time
from utils.neo4j_driver import neo4j_driver
import concurrent.futures
import time
from utils.logger import create_logger
from common_queries import get_cities

driver: Driver = neo4j_driver


def permutate_amenities(tx: Transaction, city: str, logger: logging.Logger):
    query = f"""
    match (n:Place)
    where n.area = $city
    // Obtengo las listas de amenities e ids de cada nodo
    WITH collect(n.category) AS categories, collect(id(n)) as ids
    // Permuto la lista de ids de nodos
    with categories, apoc.coll.shuffle(ids) as ids
    // Creo un contador para acceder a todos los elementos de las listas anteriores
    // unwind funciona como un bucle
    unwind range(0,size(ids)-1) as counter
    // Obtengo el nodo con el id en la posición de counter en la lista de ids
    match (m)
    where id(m) = ids[counter]
    // Cambio el atributo "sim_amenity" del nodo con el id indexado por counter
    set m.sim_category = categories[counter]

    """

    count_query = f"""
    match (n:Place),(m:Place)
    where n.area = $city and m.area = $city
    and n.sim_category <=  m.sim_category
    optional match (n)-[r]-(m)
    with n.sim_category as n_am, m.sim_category as m_am, count(DISTINCT(r)) as n_rels
    match (q:Category)-[z:Rel]-(p:Category)
    where q.name = n_am and p.name = m_am and q.city = $city and p.city = $city
    set z.sim_value = z.sim_value +  n_rels
    """
    tx.run(query, city=city)
    logger.info("Permutadas las amenities")
    tx.run(count_query, city=city)
    logger.info("Realizado el recuento de amenities")


def permutate_city(city: str, times: int):

    logger = create_logger(f"{city}-logger", f"permutation-{city}")

    t_ini_total = time.time()
    with driver.session() as session:

        for i in range(times):

            logger.info(f"Comenzada Simulación {i+1}/{times}")
            t_ini = time.time()
            session.execute_write(permutate_amenities, city, logger)
            logger.info(
                f"Finalizada simulación {i+1} con {time.time() - t_ini} s")
    logger.info(
        f"Finalizadas las Ejecuciones! Tiempo total: {time.time() - t_ini_total}")


def create_categories_net(tx: Transaction, city: str):
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

if __name__ == "__main__":
    n_sims = 1000

    cities = get_cities()

    for c in cities:
        with driver.session() as session:
            session.execute_write(create_categories_net, c)

    with concurrent.futures.ProcessPoolExecutor() as pool:
        futures = [pool.submit(permutate_city, c, n_sims) for c in cities]
        concurrent.futures.wait(futures)
    print("fin")