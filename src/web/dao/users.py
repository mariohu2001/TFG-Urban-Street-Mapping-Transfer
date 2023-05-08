from neo4j import Driver


class UserDAO():

    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    def all(self):

        cypher_query = f"""
        MATCH (u:User)
        return u
        """

        with self.driver.session() as session:
            result = session.run(cypher_query)

            return result