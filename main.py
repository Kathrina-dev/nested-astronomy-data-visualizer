import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pyarrow.parquet as pq
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/data")
def get_data(field: str = "flux", mode: str = "full", limit: int = 100):
    start = time.time()

    if mode == "full":
        table = pq.read_table("astro.parquet")
    else:
        table = pq.read_table("astro.parquet", columns=["object_id", "observations"])

    table = table.slice(0, limit)
    data = table.to_pylist()[:limit]

    result = []
    for obj in data:
        values = [obs[field] for obs in obj["observations"]]

        avg_value = sum(values) / len(values)

        result.append({
            "object_id": obj.get("object_id", "unknown"),
            "value": avg_value
        })

    end = time.time()

    return {
        "mode": mode,
        "time_taken": round(end - start, 5),
        "data": result
    }

@app.get("/stream")
def stream_data(field: str = "flux", limit: int = 1000):
    table = pq.read_table("astro.parquet", columns=["object_id", "observations"])
    table = table.slice(0, limit)

    data = table.to_pylist()

    def generate():
        for obj in data:
            band_values = {"g": [], "r": [], "i": []}

            for obs in obj["observations"]:
                band_values[obs["band"]].append(obs[field])

            # average per band
            band_avg = {
                band: (sum(vals) / len(vals)) if vals else None
                for band, vals in band_values.items()
            }

            yield json.dumps({
                "object_id": obj["object_id"],
                "bands": band_avg
            }) + "\n"

    return StreamingResponse(generate(), media_type="application/json")