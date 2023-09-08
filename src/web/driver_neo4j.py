from neo4j import GraphDatabase, Driver, Record
from flask import current_app
import bcrypt
import time

def init_neo4j(uri: str, username: str, password: str) -> Driver:

    current_app.driver = GraphDatabase.driver(uri, auth=(username, password))

    admin_username: str = current_app.config["DEFAULT_USER"]
    admin_pass: str = current_app.config["DEFAULT_PASSWORD"]

    encrypted_pass = bcrypt.hashpw(admin_pass.encode(
        "utf8"), bcrypt.gensalt()).decode('utf8')

    # Comprobamos la conectividad con la base de datos
    


    while True:
        try:
            current_app.driver.verify_connectivity()
            break
        except Exception as ex:
            print("Intentando conectar a la base de datos...")
            time.sleep(5)
    
    # Creamos el usuario admin de la web
    with current_app.driver.session() as session:
        session.run("""
        MERGE (n:User
        {
        user_name: $user_name,
        name: 'admin',
        surname: 'admin',
        role: 'admin'
        })
        ON CREATE
            set n.password = $password, n.userId = randomUuid()
        
        """, user_name=admin_username, password=encrypted_pass)

    return current_app.driver


def get_driver() -> Driver:
    return current_app.driver


def close_driver():
    if current_app.driver != None:
        current_app.driver.close()
        current_app.driver = None

        return current_app.driver
