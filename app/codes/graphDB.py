import time

from app.routers.request_models import GraphType


def createPersonIdNode(conn, personId):
    milliseconds = int(round(time.time() * 1000))
    checkDataExists = conn.query("MATCH (a:Person) where a.personId=$personId return count(a)", {'personId': personId})

    if (checkDataExists[0]['count(a)'] == 0):
        result = conn.query("CREATE (a:Person) "
                            "SET a.personId = $personId "
                            "SET a.createTimeStamp =$time "
                            "RETURN a.personId + ', from node ' + id(a)", {'personId': personId, 'time': milliseconds})
        return result[0]

    return 0


def createRelationBetweenNodes(conn, personId1, personId2, trustScore):
    milliseconds = int(round(time.time() * 1000))
    checkPersonExists = conn.query("MATCH (a:Person) "
                                   "where a.personId=$personId1  "
                                   "return count(a)", {'personId1': personId1})
    print(checkPersonExists[0]['count(a)'])
    if (checkPersonExists[0]['count(a)'] == 0):
        createPersonIdNode(conn, personId1)
    checkPersonExists = conn.query("MATCH (a:Person) "
                                   "where a.personId=$personId1  "
                                   "return count(a)", {'personId1': personId2})
    if (checkPersonExists[0]['count(a)'] == 0):
        createPersonIdNode(conn, personId2)
    checkDataExists = conn.query("MATCH (a:Person)-[rel:TRUSTSCORE]-(b:Person) "
                                 "where a.personId=$personId1 and b.personId=$personId2 "
                                 "return count(rel)", {'personId1': personId1, 'personId2': personId2})
    if (checkDataExists[0]['count(rel)'] > 0):
        result = conn.query("MATCH (a:Person)-[rel:TRUSTSCORE]-(b:Person) "
                            "where a.personId=$personId1 and b.personId=$personId2 "
                            "SET rel.value = $value1 "
                            "RETURN rel.value ", {'personId1': personId1, 'personId2': personId2, 'value1': trustScore})
    else:
        result = conn.query("MATCH (n),(b) where "
                            "n.personId= $personId1 "
                            "and b.personId= $personId2 "
                            "CREATE (n)-[r:TRUSTSCORE{value:$value1}]->(b)"
                            "RETURN n ", {'personId1': personId1, 'personId2': personId2, 'value1': trustScore})

    return result


def getTrustScorePath(conn, personId1, personId2, type: GraphType):
    if (type == GraphType.ShortestPath):
        result = conn.query("MATCH (a:Person {personId: $personId1} ), "
                            " (b:Person {personId: $personId2}), "
                            " p = shortestPath((a)-[:TRUSTSCORE*]-(b)) "
                            "WHERE all(r IN relationships(p) WHERE r.value IS NOT NULL) "
                            "RETURN p", {'personId1': personId1, 'personId2': personId2})
    elif (type == GraphType.AllPath):
        result = conn.query("MATCH (a:Person {personId: $personId1} ), "
                            " (b:Person {personId: $personId2}), "
                            " p = (a)-[:TRUSTSCORE*]-(b) "
                            "WHERE all(r IN relationships(p) WHERE r.value IS NOT NULL) "
                            "RETURN p", {'personId1': personId1, 'personId2': personId2})
    elif (type == GraphType.PageRank):
        result = "Not Implemented Yet."

    return result


def getLevelConnectedData(conn, personId, level):
    checkDataExists = conn.query("MATCH (a:Person) where a.personId=$personId return count(a)", {'personId': personId})
    print(personId)
    print(checkDataExists[0]['count(a)'])
    if (checkDataExists[0]['count(a)'] > 0):
        result = conn.query(
            "MATCH (Person{personId :$personId})-[a:TRUSTSCORE*" + str(level) + ".." + str(level) + "]->(connected) "
                                                                                        "RETURN connected,a",
            {'personId': personId})
        return result

    return 0


def get_graph_data(conn, personId):
    check_data_exists = conn.query("MATCH (a:Person) where a.personId=$personId return count(a)", {'personId': personId})
    print(check_data_exists[0]['count(a)'])
    if check_data_exists[0]['count(a)'] > 0:
        inbound = conn.query("MATCH p=    (Person{personId :$personId})-[:TRUSTSCORE*1..1]->(connected) "
                             "WHERE all(r IN relationships(p) WHERE r.value IS NOT NULL) RETURN relationships(p)",
                             {'personId': personId})
        outbound = conn.query("MATCH p=    (Person{personId :$personId})<-[:TRUSTSCORE*1..1]-(connected) "
                              "WHERE all(r IN relationships(p) WHERE r.value IS NOT NULL) RETURN relationships(p)",
                              {'personId': personId})
        result = {
            'inbound': inbound,
            'outbound': outbound,
        }
        return result

    return {'inbound': None, 'outbound': None}
