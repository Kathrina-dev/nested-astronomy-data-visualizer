# Nested Data vs Columnar Reality

### Why sub-column access matters (and why it currently fails)

Live demo: [https://YOUR_USERNAME.github.io/astro-visualizer/](https://kathrina-dev.github.io/nested-astronomy-data-visualizer/)

---

## The Problem

Modern data formats like Parquet are **columnar**, but once you introduce **nested structures**, things break down.

Even if you only need one field, systems often end up reading:

* the entire nested struct
* all sibling fields (`band`, etc.)
* the full column chunk

Result: **no real I/O savings**

---

## What This Demo Shows

This project simulates three realistic access patterns:

| Mode                | What happens                                   | Reality             |
| ------------------- | ---------------------------------------------- | ------------------- |
| **Full Read**       | Reads entire dataset                           | Baseline            |
| **Partial Read**    | Selects columns, but still loads nested struct |  No real gain       |
| **Sub-column Read** | Reads pre-flattened flux-only file             |  True optimization  |

---

## Why This Matters

The benchmark includes:

* **Read time (ms)**
* **Bytes read (KB)**

Example outcome:

```
Full:        4.2 MB, 120 ms
Partial:     4.2 MB, 115 ms
Sub-column:  0.9 MB, 25 ms
```

---

## How It Works

### 1. Data Generation

We generate synthetic astronomical observations:

```python
object_id → [
  { flux, band },
  { flux, band },
  ...
]
```

Then create three datasets:

* `astro_full.parquet` → nested structure
* `astro_partial.parquet` → same schema (tests PyArrow limitation)
* `astro_flux.parquet` → flattened (true sub-column access)

---

### 2. Backend (FastAPI)

* Streams data via `/stream`
* Benchmarks via `/benchmark`
* Measures:

  * read time
  * file size (I/O proxy)

---

### 3. Frontend

* Streams data incrementally
* Renders band averages
* Displays:

  * backend read time
  * frontend render time
  * mode comparison

---

## Key Limitation (Important)

PyArrow currently cannot efficiently read sub-fields inside nested lists:

```python
pq.read_table(..., columns=["observations.flux"])
```

This does **not** avoid reading the full struct.

---

## The Takeaway

To get real performance gains:

* You must **flatten or restructure your data**
* Or use systems that support **true nested column pruning**

---

## Run Locally

### 1. Install dependencies

```
pip install fastapi uvicorn pyarrow
```

### 2. Generate data

```
python generate-data.py
```

### 3. Start backend

```
uvicorn main:app --reload
```

### 4. Open frontend

```
index.html
```

---

## Deployment

* Frontend → GitHub Pages
* Backend → Render

---

## Future Ideas

* True nested column pruning (when supported)
* Arrow dataset scanning
* Compression comparisons (Snappy vs ZSTD)
* Real astronomical datasets
