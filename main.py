import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pyarrow.parquet as pq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/data")
def get_data(field: str = "flux", mode: str = "full"):
    start = time.time()

    if mode == "full":
        table = pq.read_table("astro.parquet")

    else:  # partial read
        table = pq.read_table("astro.parquet", columns=["observations"])

    data = table.to_pylist()

    result = []
    for obj in data:
        values = [obs[field] for obs in obj["observations"]]
        result.append({
            "object_id": obj.get("object_id", "unknown"),
            "values": values
        })

    end = time.time()

    return {
        "mode": mode,
        "time_taken": round(end - start, 5),
        "data": result
    }