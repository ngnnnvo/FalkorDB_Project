
from falkordb import FalkorDB
import statistics
import time

db = FalkorDB(host="localhost", port=6379)
graph = db.select_graph("RuaTien_Large")

QUERY = """
MATCH p = (a:Account {id: 'R2_1'})-[:TRANSFER*5]->(a)
RETURN p
"""

def benchmark():
    for _ in range(5):
        graph.query(QUERY)

    times = []

    for _ in range(30):
        result = graph.query(QUERY)

        if len(result.result_set) != 1:
            raise RuntimeError("Ket qua chu trinh khong dung!")

        times.append(result.run_time_ms)

    return {
        "average": statistics.mean(times),
        "median": statistics.median(times),
        "minimum": min(times),
        "maximum": max(times)
    }

print("BAT DAU BENCHMARK")

index_removed = False

try:
    graph.query("DROP INDEX ON :Account(id)")
    index_removed = True

    print("Dang do TRUOC INDEX...")
    before = benchmark()

finally:
    if index_removed:
        graph.query(
            "CREATE INDEX FOR (a:Account) ON (a.id)"
        )

for _ in range(40):
    plan = str(graph.explain(QUERY))

    if "Node By Index Scan" in plan:
        break

    time.sleep(0.25)
else:
    raise RuntimeError("INDEX chua san sang!")

print("Dang do SAU INDEX...")
after = benchmark()


lines = [
    "KET QUA BENCHMARK (30 LAN)",
    "",
    f"Truoc INDEX - Trung binh: {before['average']:.6f} ms",
    f"Sau INDEX   - Trung binh: {after['average']:.6f} ms",
    "",
    f"Truoc INDEX - Trung vi: {before['median']:.6f} ms",
    f"Sau INDEX   - Trung vi: {after['median']:.6f} ms",
    "",
    f"Truoc INDEX - Nho nhat: {before['minimum']:.6f} ms",
    f"Sau INDEX   - Nho nhat: {after['minimum']:.6f} ms",
    "",
    f"Truoc INDEX - Lon nhat: {before['maximum']:.6f} ms",
    f"Sau INDEX   - Lon nhat: {after['maximum']:.6f} ms",
]

if after["median"] > 0:
    speedup = before["median"] / after["median"]
    lines.append(f"\nTi le thoi gian trung vi: {speedup:.2f}x")

output = "\n".join(lines)

print("\n" + output)

with open("benchmark_result.txt", "w", encoding="utf-8") as f:
    f.write(output)

print("\nDA LUU FILE benchmark_result.txt")
