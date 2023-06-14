from neo4j import Driver
import bcrypt
from .base import baseDAO

class UserDAO(baseDAO):

    def all(self):

        cypher_query = f"""
        MATCH (u:User)
        return u
        """

        with self.driver.session() as session:
            result = session.run(cypher_query)

            return result

    def get_by_username(self, username: str):

        cypher_query = """
        MATCH (u:User)
        where u.user_name = $username
        return u
        """

        with self.driver.session() as session:
            result = session.run(cypher_query, username=username)
            return result.single()

    def get_by_email(self, email: str):

        cypher_query = """
        MATCH (u:User)
        where u.mail = $email
        return u
        """


        with self.driver.session() as session:
            result = session.run(cypher_query, email=email)
            return result.single()

    def create_user(self, userdata: dict):

        encrypted_password: str = bcrypt.hashpw(userdata["password"].encode(
            "utf8"), bcrypt.gensalt()).decode('utf8')

        userdata["password"] = encrypted_password

        cypher_query = """
            CREATE (u:User{
            userId: randomUuid(),
            user_name: $username,
            password: $password,
            name: $first_name,
            surname: $surname,
            admin: False,
            mail: $email
            }
            )
        """
        with self.driver.session() as session:
            session.run(cypher_query, **userdata)
