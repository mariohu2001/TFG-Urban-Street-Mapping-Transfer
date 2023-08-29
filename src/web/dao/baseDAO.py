from neo4j import Driver


class baseDAO:

    def __init__(self, driver: Driver) -> None:
        self.driver = driver
