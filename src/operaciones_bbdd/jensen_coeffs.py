from utils.neo4j_driver import neo4j_driver
from neo4j import Result, Session, Transaction, Driver
import concurrent.futures
from common_queries import get_cities

driver: Driver = neo4j_driver


def create_jensen_net(tx: Transaction, city: str):
    cypher_query = """
    MATCH (q:Category), (p:Category)
    where q.city = p.city and q.city = $city
    MERGE (q)-[r:Jensen]->(p)
    """

    tx.run(cypher_query, city=city)



    
def intra_category_coeff(tx: Transaction, city: str):
    cypher_query = """MATCH (p:Place)
        where p.area = $city
    call {
        with p
        match (p)-[z]-()
        return count(z) as totalRels
    }
    call{
        with p
        match (p)-[r]-(m)
        where m.category = p.category
        return count(r) as rels
    }
    call{
        match (n:Place)
        where n.area = $city
        return count(n) as totalN
    }
    call apoc.when(
        rels = 0 and totalRels = 0,
        "return 0 as sum_div",
        "return toFloat(rels)/toFloat(totalRels) as sum_div",
        {rels:rels, totalRels:totalRels}
    ) yield value
    with totalN,count(p) as A,sum(value.sum_div) as sumatorio, p.category as cat
    with totalN, A, (1/toFloat(A)) * sumatorio as numerador, cat
    call apoc.when(
        numerador = 0 and (toFloat(A-1)/toFloat(totalN-1)) = 0,
        "return 0 as resultado",
        "return numerador/(toFloat(A-1)/toFloat(totalN-1)) as resultado",
        {numerador:numerador, A:A, totalN:totalN}
    ) yield value

    match (c:Category)-[x]->(c)
    where c.city = $city and c.name = cat
    set x.coeff = value.resultado"""

    tx.run(cypher_query, city=city)


def inter_category_coeff(tx: Transaction, city: str):
    cypher_query = """
    MATCH (p:Place), (q:Category)
    where p.area = $city and q.city = $city and p.category <> q.name
    call {
        with p
        match (p)-[z]-()
        return count(z) as Nt
    }
    call{
        with p
        match (p)-[r]-(m)
        where m.category = p.category
        return count(r) as Na
    }
    call{
        with p,q
        match (p)-[r]-(m)
        where m.category = q.name
        return count(r) as Nb 
    }
    call{
        match (n:Place)
        where n.area = $city
        return count(n) as T
    }
    call{
        with p,q 
        match (n:Place)
        where n.category = q.name and n.area = $city
        return count(n) as B
    }

    call apoc.when(
        Nb = 0 and Nt - Na = 0,
        "return 0 as sum_div",
        "return (toFloat(Nb)/(toFloat(Nt)-toFloat(Na))) as sum_div",
        {Nb:Nb, Nt:Nt, Na:Na}
    ) yield value
    with count(p) as A,B,T, sum(value.sum_div) as sumatorio, q as cat, p.category as pcat
    with  A,B,T, ((toFloat(1)/toFloat(A)) * sumatorio) as numerador, cat, pcat
    call apoc.when(
        numerador = 0 and (toFloat(B)/toFloat(T-A)) = 0,
        "return 0 as resultado",
        "return numerador/(toFloat(B)/toFloat(T-A)) as resultado",
        {numerador:numerador, B:B, T:T, A:A}
    ) yield value
    match (c:Category)-[r:Jensen]->(cat)
    where c.name = pcat
    set r.coeff = value.resultado
    """
    tx.run(cypher_query, city=city)

def calculate_jensen(city:str):
    with driver.session() as session:
            print(city, flush=True)
            session.execute_write(create_jensen_net, city)
            print(f"Creada red Jensen {city}", flush=True)
            session.execute_write(intra_category_coeff, city)
            print(f"Calculados coeficientes intra {city}", flush=True)
            session.execute_write(inter_category_coeff, city)
            print(f"Calculados coeficientes inter {city}", flush=True)


if __name__ == "__main__":
    
    cities = get_cities()

    with concurrent.futures.ProcessPoolExecutor as pool:
        futures = [pool.submit(calculate_jensen, c) for c in cities]
        concurrent.futures.wait(futures)
    print("fin")