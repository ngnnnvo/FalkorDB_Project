from falkordb import FalkorDB

db = FalkorDB(host="localhost", port=6379)
graph = db.select_graph("RuaTien_Large")

# Dem tai khoan
result = graph.query("""
MATCH (a:Account)
RETURN count(a) AS total
""")
print("Tong tai khoan:", result.result_set[0][0])

# Dem giao dich
result = graph.query("""
MATCH ()-[t:TRANSFER]->()
RETURN count(t) AS total
""")
print("Tong giao dich:", result.result_set[0][0])

# Kiem tra 3 chu trinh
for size in [4, 5, 6]:
    query = f"""
    MATCH p = (a:Account)-[:TRANSFER*{size}]->(a)
    WHERE a.id STARTS WITH 'R'
    RETURN DISTINCT [n IN nodes(p) | n.id]
    LIMIT 1
    """

    result = graph.query(query)

    print(f"\nChu trinh {size} buoc:")

    if result.result_set:
        for row in result.result_set:
            print(" -> ".join(row[0]))
    else:
        print("Khong tim thay")