
from falkordb import FalkorDB
import random

db = FalkorDB(host="localhost", port=6380)
graph = db.select_graph("RuaTien_Large")

random.seed(42)

accounts = []

for i in range(1, 1001):
    accounts.append({
        "id": f"C{i:04d}",
        "owner": f"Khach hang {i}",
        "role": "Khach hang sach"
    })

graph.query("""
UNWIND $accounts AS account
MERGE (a:Account {id: account.id})
SET a.owner = account.owner,
    a.role = account.role
""", {"accounts": accounts})

print("Da tao 1000 tai khoan sach!")

transactions = []
used_pairs = set()

while len(transactions) < 2000:
    source = random.randint(1, 1000)
    target = random.randint(1, 1000)

    if source == target:
        continue

    if source > target:
        source, target = target, source

    pair = (source, target)

    if pair in used_pairs:
        continue

    used_pairs.add(pair)

    transactions.append({
        "tx_id": f"N{len(transactions)+1:05d}",
        "source": f"C{source:04d}",
        "target": f"C{target:04d}",
        "amount": random.randint(1, 100)
    })

graph.query("""
UNWIND $transactions AS tx
MATCH (a:Account {id: tx.source})
MATCH (b:Account {id: tx.target})
MERGE (a)-[t:TRANSFER {tx_id: tx.tx_id}]->(b)
SET t.amount = tx.amount,
    t.type = 'normal'
""", {"transactions": transactions})

print("Da tao 2000 giao dich binh thuong!")


cycle_sizes = [4, 5, 6]
suspicious_accounts = []
suspicious_transactions = []

for group_index, size in enumerate(cycle_sizes, start=1):

    ids = []

    for j in range(1, size + 1):
        account_id = f"R{group_index}_{j}"
        ids.append(account_id)

        suspicious_accounts.append({
            "id": account_id,
            "owner": f"Tai khoan nghi van {account_id}",
            "role": "Nghi van"
        })

    for j in range(size):
        suspicious_transactions.append({
            "tx_id": f"R{group_index}_TX{j+1}",
            "source": ids[j],
            "target": ids[(j + 1) % size],
            "amount": random.randint(100, 500)
        })

graph.query("""
UNWIND $accounts AS account
MERGE (a:Account {id: account.id})
SET a.owner = account.owner,
    a.role = account.role
""", {"accounts": suspicious_accounts})

graph.query("""
UNWIND $transactions AS tx
MATCH (a:Account {id: tx.source})
MATCH (b:Account {id: tx.target})
MERGE (a)-[t:TRANSFER {tx_id: tx.tx_id}]->(b)
SET t.amount = tx.amount,
    t.type = 'suspicious'
""", {"transactions": suspicious_transactions})

print("Da tao 3 duong day rua tien!")


result = graph.query("""
MATCH (a:Account)
RETURN count(a)
""")

print("Tong so tai khoan:", result.result_set[0][0])

result = graph.query("""
MATCH ()-[t:TRANSFER]->()
RETURN count(t)
""")

print("Tong so giao dich:", result.result_set[0][0])

print("HOAN THANH SINH DU LIEU!")
