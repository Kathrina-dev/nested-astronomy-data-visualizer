import pyarrow as pa
import pyarrow.parquet as pq
import random

N_OBJECTS = 10000
N_OBS = 50

# 1. FULL
obs_struct = pa.struct([
    ("flux", pa.float32()),
    ("band", pa.string())
])

schema_full = pa.schema([
    ("object_id", pa.int32()),
    ("observations", pa.list_(obs_struct))
])

full_data = []

for i in range(N_OBJECTS):
    observations = []
    for j in range(N_OBS):
        observations.append({
            "flux": float(j * 2 + random.randint(-10, 10)),
            "band": random.choice(["g", "r", "i"])
        })

    full_data.append({
        "object_id": i,
        "observations": observations
    })

full_table = pa.Table.from_pylist(full_data, schema=schema_full)
pq.write_table(full_table, "astro_full.parquet")


# 2. PARTIAL
pq.write_table(full_table, "astro_partial.parquet")


# 3. SUB-COLUMN (FLATTENED FLUX)

flat_data = []
flat_schema = pa.schema([
    ("object_id", pa.int32()),
    ("flux", pa.float32())
])

for obj in full_data:
    flux_values = [obs["flux"] for obs in obj["observations"]]

    flat_data.append({
        "object_id": obj["object_id"],
        "flux": sum(flux_values) / len(flux_values)
    })


flat_table = pa.Table.from_pylist(flat_data, schema=flat_schema)
pq.write_table(flat_table, "astro_flux.parquet")

print("Files created:")
print(" - astro_full.parquet")
print(" - astro_partial.parquet")
print(" - astro_flux.parquet")