import logging
from neo4j import Driver, Transaction
from time import time
from utils.neo4j_driver import neo4j_driver
import concurrent.futures
import time
from utils.logger import create_logger
from common_queries import obtain_cities

driver: Driver = neo4j_driver


def permutate_amenities(tx: Transaction, city: str, logger: logging.Logger):
    query = f"""
    match (n:Place)
    where n.area = $city
    // Obtengo las listas de amenities e ids de cada nodo
    WITH collect(n.amenity) AS amenities, collect(id(n)) as ids
    // Permuto la lista de ids de nodos
    with amenities, apoc.coll.shuffle(ids) as ids
    // Creo un contador para acceder a todos los elementos de las listas anteriores
    // unwind funciona como un bucle
    unwind range(0,size(ids)-1) as counter
    // Obtengo el nodo con el id en la posición de counter en la lista de ids
    match (m)
    where id(m) = ids[counter]
    // Cambio el atributo "sim_amenity" del nodo con el id indexado por counter
    set m.sim_amenity = amenities[counter]

    """

    count_query = f"""
    match (n:Place),(m:Place)
    where n.area = $city and m.area = $city
    and n.sim_amenity <=  m.sim_amenity
    optional match (n)-[r]-(m)
    with n.sim_amenity as n_am, m.sim_amenity as m_am, count(DISTINCT(r)) as n_rels
    match (q:Amenity)-[z]-(p:Amenity)
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


if __name__ == "__main__":
    n_sims = 1000

    cities = obtain_cities()

    with concurrent.futures.ProcessPoolExecutor() as pool:
        futures = [pool.submit(permutate_city, c, n_sims) for c in cities]
        concurrent.futures.wait(futures)
    print("fin")
