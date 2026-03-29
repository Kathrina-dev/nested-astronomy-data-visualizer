from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pyarrow.parquet as pq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (for dev)
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/data")
def get_data(field: str = "flux"):
    table = pq.read_table("astro.parquet")
    data = table.to_pylist()

    result = []
    for obj in data:
        values = [obs[field] for obs in obj["observations"]]
        result.append({
            "object_id": obj["object_id"],
            "values": values
        })

    return result