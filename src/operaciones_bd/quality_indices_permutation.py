from utils.neo4j_driver import neo4j_driver
from neo4j import Result, Session, Transaction, Driver
import concurrent.futures
from common_queries import obtain_cities

driver: Driver = neo4j_driver

def quality_indices(tx: Transaction, city: str):

    cypher_query = """
    match (n:Place),(u:Category)
    where n.area = $city and
      n.category = u.name and
        n.area = u.city 
   

    // a_ij
    call{
        with u
        match(u:Category)-[r]-(v:Category)
        return r.z_score as a_ij, v.name as categories
    }
    // nei
    call{
        with n, categories
        match (n),(m:Place)
        where n.area = m.area
        and m.category = categories and n <> m
        optional match (n)-[r]-(m)
        return count(r) as nei 
    }
    //nei_avg
    call{
        with n,categories
        match (p:Category)-[r]-(q:Category)
        where p.name = n.category and q.name = categories
        and n.area = p.city and p.city = q.city
        return toFloat(r.real_value)/toFloat(p.n_nodes) as nei_avg
    }
    with n, sum(a_ij * (nei - nei_avg)) as sumatorio
    set n.Q_permutation= sumatorio
    """

    tx.run(cypher_query, city=city)



def quality_indices_raw(tx: Transaction, city: str):
   

    cypher_query = """
    match (n:Place),(u:Category)
    where n.area = $city and
      n.category = u.name and
        n.area = u.city 
   

    // a_ij
    call{
        with u
        match(u:Category)-[r]-(v:Category)
        return r.z_score as a_ij, v.name as categories
    }
    // nei
    call{
        with n, categories
        match (n),(m:Place)
        where n.area = m.area
        and m.category = categories and n <> m
        optional match (n)-[r]-(m)
        return count(r) as nei 
    }

    with n, sum(a_ij * (nei)) as sumatorio
    set n.Q_permutation_raw= sumatorio
    """

    tx.run(cypher_query, city=city)

def set_quality_indices(city: str):

    with driver.session() as session:
        print(city, flush=True)
        session.execute_write(quality_indices_raw, city)
        print(f"Acabados Indices Raw {city}", flush=True)
        session.execute_write(quality_indices, city)
        print(f"Acabados Indices {city}", flush=True)


if __name__ == "__main__":
    cities = obtain_cities()

    with concurrent.futures.ProcessPoolExecutor() as pool:
        futures = [pool.submit( set_quality_indices, c) for c in cities]
        concurrent.futures.wait(futures)
    # for c in cities:
    #     set_quality_indices(c)
    print("fin")
