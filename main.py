import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pyarrow.parquet as pq
from fastapi.responses import StreamingResponse
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Read-Time-Ms"],
)

@app.get("/stream")
def stream_data(limit: int = 1000, mode: str = "full"):

    start = time.time()

    if mode == "full":
        table = pq.read_table("astro_full.parquet")

    # NOTE:
    # This still reads full nested struct due to PyArrow limitation.
    # We simulate sub-column behavior at I/O level.
    elif mode == "partial":
        table = pq.read_table("astro_partial.parquet", columns=["object_id", "observations"])

    # NOTE:
    # This still reads full nested struct due to PyArrow limitation.
    # We simulate sub-column behavior at I/O level.
    elif mode == "simulated":
        table = pq.read_table("astro_flux.parquet")

    table = table.slice(0, limit)
    data = table.to_pylist()

    read_time = (time.time() - start) * 1000

    def generate():
        for obj in data:

            if mode == "simulated":
                yield json.dumps({
                    "object_id": obj["object_id"],
                    "bands": {
                        "g": obj["flux"],
                        "r": obj["flux"],
                        "i": obj["flux"]
                    }
                }) + "\n"

            else:
                band_values = {"g": [], "r": [], "i": []}

                for obs in obj["observations"]:
                    band_values[obs["band"]].append(obs["flux"])

                band_avg = {
                    band: (sum(vals) / len(vals)) if vals else None
                    for band, vals in band_values.items()
                }

                yield json.dumps({
                    "object_id": obj["object_id"],
                    "bands": band_avg
                }) + "\n"

    response = StreamingResponse(generate(), media_type="application/json")
    response.headers["X-Read-Time-Ms"] = str(round(read_time, 2))

    return response

import os

@app.get("/benchmark")
def benchmark(limit: int = 1000):
    results = {}

    configs = {
        "full": ("astro_full.parquet", None),
        "partial": ("astro_partial.parquet", ["object_id", "observations"]),
        "simulated": ("astro_flux.parquet", None),
    }

    for mode, (file, cols) in configs.items():
        start = time.time()

        table = pq.read_table(file, columns=cols)
        table = table.slice(0, limit)
        _ = table.to_pylist()

        elapsed = (time.time() - start) * 1000
        size = os.path.getsize(file) / 1024  # KB

        results[mode] = {
            "time_ms": round(elapsed, 2),
            "size_kb": round(size, 2)
        }

    return results