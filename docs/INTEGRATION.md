# Backend Integration Guide for FastAPI & Machine Learning

**Target Audience:** Member 1 (ML/GNN) & Member 2 (SNA/FastAPI)  
**System Layer:** React Frontend to FastAPI Backend

---

## 1. Architecture Flow

```text
React Frontend (Port 5173)
       │
       │ HTTP / JSON via Axios Centralized Layer
       ▼
FastAPI Server (Port 8000)
       ├── GET  /health
       ├── GET  /statistics
       ├── GET  /user/{id}
       ├── GET  /user/{id}/network
       ├── GET  /network
       ├── GET  /communities
       ├── GET  /community/{id}
       ├── GET  /coordination
       ├── GET  /model-performance
       └── POST /predict
       │
       ├── Graph ML / RGCN Model Engine
       ├── NetworkX / iGraph Social Network Centrality
       └── Community Detection (Louvain / Infomap)
```

---

## 2. Setting Up CORS in FastAPI

The FastAPI backend must enable CORS for local development origins.

### Example in `main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MGTAB SNA Detection API", version="1.0.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 3. Frontend Mock Fallback Behavior

The frontend automatically detects backend status:

1. If FastAPI is running on `http://localhost:8000`, the frontend automatically consumes live API results with live latency indicators.
2. If FastAPI is offline or an endpoint returns 500/404, the frontend automatically falls back to isolated MGTAB research mock data so the UI remains navigable.
3. To force live-only or force-mock, configure `.env`:
   ```bash
   VITE_API_BASE_URL=http://localhost:8000
   VITE_USE_MOCK=false
   ```

---

## 4. Normalizers and Schema Flexibility

All UI components consume typed contracts defined in `src/types/`.  
If backend fields are named slightly differently (e.g. `communityId` vs `community_id`), services in `src/services/` normalize them before passing to UI components.

---

## 5. Verification Steps

1. Start FastAPI:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
2. Start Frontend:
   ```bash
   npm run dev
   ```
3. Open `http://localhost:5173`.
4. Check the top header badge: It should display **`FastAPI Live (XXms)`** in green.
