# generate_data.py
import pyarrow as pa
import pyarrow.parquet as pq

data = [
    {
        "object_id": 1,
        "observations": [
            {"time": 1, "flux": 10, "band": "g"},
            {"time": 2, "flux": 15, "band": "r"},
        ],
    },
    {
        "object_id": 2,
        "observations": [
            {"time": 1, "flux": 5, "band": "g"},
            {"time": 2, "flux": 7, "band": "r"},
        ],
    },
]

table = pa.Table.from_pylist(data)
pq.write_table(table, "astro.parquet")