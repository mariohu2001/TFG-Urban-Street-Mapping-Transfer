from neo4j import GraphDatabase, Driver, Record
from flask import current_app
import bcrypt


def init_neo4j(uri: str, username: str, password: str) -> Driver:

    current_app.driver = GraphDatabase.driver(uri, auth=(username, password))

    admin_username: str = current_app.config["DEFAULT_USER"]
    admin_pass: str = current_app.config["DEFAULT_PASSWORD"]
    encrypted_pass = bcrypt.hashpw(admin_pass.encode(
        "utf8"), bcrypt.gensalt()).decode('utf8')
    
    # Comprobamos la conectividad con la base de datos
    current_app.driver.verify_connectivity()

    # Creamos el usuario admin de la web
    with current_app.driver.session() as session:
        admin_user: Record = session.run("""
        MATCH (n:User)
        where n.user_name = 'admin'
        and n.admin = True
        return n
        """).single()

        if admin_user is None:

            session.run("""
            CREATE (u:User{
            userId: randomUuid(),
            user_name: $user_name,
            password: $password,
            name: 'admin',
            surname: 'admin',
            admin: True
            }
            )
            """, user_name=admin_username, password=encrypted_pass)

    return current_app.driver


def get_driver() -> Driver:
    return current_app.driver


def close_driver():
    if current_app.driver != None:
        current_app.driver.close()
        current_app.driver = None

        return current_app.driver
