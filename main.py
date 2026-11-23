
from falkordb import FalkorDB
db = FalkorDB(host="localhost", port=6379)
graph = db.select_graph("RuaTien_TV5")

accounts = [
    ("A1", "Nguyen Van An", "Chu muu"),
    ("A2", "Tran Thi Binh", "Trung gian"),
    ("A3", "Le Van Cuong", "Trung gian"),
    ("A4", "Pham Thi Dung", "Trung gian"),
    ("A5", "Cong ty TNHH Minh Long", "Vo boc"),
    ("A6", "Hoang Van Em", "Khach hang sach"),
]

transactions = [
    ("TX01", "A1", "A2", 500),
    ("TX02", "A2", "A3", 480),
    ("TX03", "A3", "A4", 460),
    ("TX04", "A4", "A1", 450),
    ("TX05", "A2", "A5", 150),
    ("TX06", "A5", "A4", 140),
    ("TX07", "A4", "A6", 20),
]

for account_id, owner, role in accounts:
    graph.query(
        """
        MERGE (a:Account {id: $id})
        SET a.owner = $owner, a.role = $role
        """,
        {"id": account_id, "owner": owner, "role": role}
    )

for tx_id, source, target, amount in transactions:
    graph.query(
        """
        MATCH (a:Account {id: $source})
        MATCH (b:Account {id: $target})
        MERGE (a)-[t:TRANSFER {tx_id: $tx_id}]->(b)
        SET t.amount = $amount
        """,
        {
            "tx_id": tx_id,
            "source": source,
            "target": target,
            "amount": amount
        }
    )

print("DA NAP DU LIEU THANH CONG!")
result = graph.query(
    "MATCH (a:Account) RETURN count(a)"
)
print("So tai khoan:", result.result_set[0][0])
result = graph.query(
    "MATCH ()-[t:TRANSFER]->() RETURN count(t)"
)
print("So giao dich:", result.result_set[0][0])
result = graph.query(
    """
    MATCH p = (a:Account {id: 'A1'})-[:TRANSFER*4]->(a)
    RETURN [n IN nodes(p) | n.id] AS cycle
    """
)

print("\nCAC CHU TRINH RUA TIEN:")
for row in result.result_set:
    print(" -> ".join(row[0]))

