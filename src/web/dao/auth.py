import datetime
import bcrypt


from flask import current_app
from flask_jwt_extended import create_access_token
from neo4j import Driver, Record, Result, Session, Transaction


class AuthDAO:

    def __init__(self, driver: Driver, jwt_secret: str) -> None:
        self.driver = driver
        self.jwt_secret = jwt_secret

    def login(self, username: str, password: str):

        def obtain_user(tx: Transaction, username: str):

            result: Result = tx.run("""
            MATCH (u:User {user_name: $username}) return u
            """, username=username)

            first: Record = result.single()

            if first is None:
                return None

            user = first.get("u")

            return user

        with self.driver.session() as session:
            user = session.execute_read(obtain_user, username)

            if user is None:
                print("Usuario no encontrado")
                return False

            if bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")) is False:
                print("Contraseña Incorrecta")
                return False

            payload = {
                "userId": user["userId"],
                "user": user["user_name"],
                "admin": user["admin"]
            }
            token = create_access_token(identity=payload)
       

            return token
