# generate_data.py
import pyarrow as pa
import pyarrow.parquet as pq
import random

data = []
for i in range(10000):
    data.append({
        "object_id": i,
        "observations": [
            {
                "time": j,
                "flux": j * 2 + random.randint(-10, 10),
                "band": random.choice(["g", "r", "i"])
            }
            for j in range(50)
        ],
    })

table = pa.Table.from_pylist(data)
pq.write_table(table, "astro.parquet")