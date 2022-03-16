from neo4j import GraphDatabase

from app.codes.Neo4jConnection import *
from app.codes.graphDB import getLevelConnectedData

import time


class GraphDB:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_relation(self, personId1, personId2, trustScore):
        with self.driver.session() as session:
            response = session.write_transaction(self._create_relation_between_nodes, personId1, personId2, trustScore)
            print(response)
    def get_shortest_path(self, personId1, personId2):
        with self.driver.session() as session:
            response = session.write_transaction(self._get_shortest_path_between_person_ids, personId1, personId2)
            print(response)
    def add_person_node(self, personId):
        with self.driver.session() as session:
            response = session.write_transaction(self._create_personId_node, personId)
            print(response)

    def add_relation_between_nodes(self, personId1, personId2, trustScore):
        with self.driver.session() as session:
            greeting = session.write_transaction(self._create_personId_node, personId1, personId2, trustScore)
            print(greeting)

    @staticmethod
    def _create_personId_node(tx, personId):
        milliseconds = int(round(time.time() * 1000))
        checkDataExists = tx.run("MATCH (a:Person) where a.personId=$personId return count(a)", personId=personId)

        if (checkDataExists.single()[0] == 0):
            result = tx.run("CREATE (a:Person) "
                            "SET a.personId = $personId "
                            "SET a.createTimeStamp =$time "
                            "RETURN a.personId + ', from node ' + id(a)", personId=personId, time=milliseconds)
            return result.single()[0]

        return 0

    @staticmethod
    def _create_relation_between_nodes(tx, personId1, personId2, trustScore):
        milliseconds = int(round(time.time() * 1000))
        checkDataExists = tx.run("MATCH (a:Person)-[rel:TRUSTSCORE]-(b:Person) "
                                 "where a.personId=$personId1 and b.personId=$personId2 "
                                 "return count(rel)", personId1=personId1, personId2=personId2)
        if (checkDataExists.single()[0] > 0):
            result = tx.run("MATCH (a:Person)-[rel:TRUSTSCORE]-(b:Person) "
                            "where a.personId=$personId1 and b.personId=$personId2 "
                            "SET rel.value = $value1 "
                            "RETURN rel.value ", personId1=personId1, personId2=personId2, value1=trustScore)
        else:
            result = tx.run("MATCH (n),(b) where "
                            "n.personId= $personId1 "
                            "and b.personId= $personId2 "
                            "CREATE (n)-[r:TRUSTSCORE{value:$value1}]->(b)"
                            "RETURN n ", personId1=personId1, personId2=personId2, value1=trustScore)

        return result

    @staticmethod
    def _get_shortest_path_between_person_ids(tx, personId1, personId2):

        result = tx.run("MATCH (a:Person {personId: $personId1} ),"
                            " (b:Person {personId: $personId2}), "
                            "p = shortestPath((a)-[:TRUSTSCORE*]-(b)) "
                            "WHERE all(r IN relationships(p) WHERE r.value IS NOT NULL)"
                            "RETURN p" , personId1=personId1, personId2=personId2)

        return result.single()[0]
if __name__ == "__main__":
    # persistNode = GraphDB("bolt://localhost:7687", "neo4j", "admin")
    # persistNode.add_person_node("pi44abf3cbc6355805a6aa45eaf5771f8c401c6896")
    # persistNode.add_person_node("pi86064a36b41c5cd280e7b01c106b05cb73dbb9aq")
    #
    # persistNode.add_person_node("pi86064a36b41c5cd280e7b01c106b05cb73dbb9aa")
    # persistNode.add_person_node("pi86064a36b41c5cd280e7b01c106b05cb73dbb9ac")
    # persistNode.add_person_node("pi86064a36b41c5cd280e7b01c106b05cb73dbb9ad")
    # persistNode.add_person_node("pi86064a36b41c5cd280e7b01c106b05cb73dbb9ae")
    # persistNode.add_person_node("pi86064a36b41c5cd280e7b01c106b05cb73dbb9af")
    # persistNode.add_person_node("pi86064a36b41c5cd280e7b01c106b05cb73dbb9ag")
    # persistNode.create_relation("pi86064a36b41c5cd280e7b01c106b05cb73dbb9aq",
    #                             "pi44abf3cbc6355805a6aa45eaf5771f8c401c6896", 4.0)
    # persistNode.create_relation("pi86064a36b41c5cd280e7b01c106b05cb73dbb9aq",
    #                             "pi86064a36b41c5cd280e7b01c106b05cb73dbb9ad", 4.0)
    #
    # persistNode.create_relation("pi86064a36b41c5cd280e7b01c106b05cb73dbb9aq",
    #                             "pi86064a36b41c5cd280e7b01c106b05cb73dbb9aa", 1.0)
    #
    # persistNode.create_relation("pi86064a36b41c5cd280e7b01c106b05cb73dbb9aa",
    #                             "pi86064a36b41c5cd280e7b01c106b05cb73dbb9ac", 2.0)
    #
    # persistNode.create_relation("pi86064a36b41c5cd280e7b01c106b05cb73dbb9ac",
    #                             "pi86064a36b41c5cd280e7b01c106b05cb73dbb9ad", 3.0)
    #
    # persistNode.create_relation("pi86064a36b41c5cd280e7b01c106b05cb73dbb9ad",
    #                             "pi86064a36b41c5cd280e7b01c106b05cb73dbb9ae", 4.0)
    # persistNode.create_relation("pi86064a36b41c5cd280e7b01c106b05cb73dbb9ad",
    #                             "pi86064a36b41c5cd280e7b01c106b05cb73dbb9af", 4.0)
    # persistNode.create_relation("pi86064a36b41c5cd280e7b01c106b05cb73dbb9ad",
    #                             "pi86064a36b41c5cd280e7b01c106b05cb73dbb9ag", 4.0)
    # persistNode.create_relation("pi86064a36b41c5cd280e7b01c106b05cb73dbb9ad",
    #                             "pi86064a36b41c5cd280e7b01c106b05cb73dbb9ad", 4.0)
    # print(persistNode.get_shortest_path("pi86064a36b41c5cd280e7b01c106b05cb73dbb9aq","pi86064a36b41c5cd280e7b01c106b05cb73dbb9ae"))
    getLevelConnectedData(conn,'pid0fad2d4b130f9cda9927166e4e8abbb72dd71f2',1)
    # persistNode.close()
