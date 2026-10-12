# MGTAB-Based Bot Detection using SNA & RGCN

> Social Network Analysis and Relational Graph Convolutional Network for Twitter Bot Detection
> Built on the **MGTAB** (Multi-relational Graph-based Twitter Account Detection Benchmark) dataset

---

## Project Overview

This project implements a multi-pipeline bot detection system for Twitter accounts using the MGTAB benchmark dataset. It combines:

1. **Social Network Analysis (SNA)** — graph construction, centrality measures, community detection (Louvain), and coordination scoring
2. **Traditional ML (HistGradientBoosting)** — tabular classification using 806 features (20 profile + 768 text embeddings + 18 SNA metrics)
3. **Graph Neural Network (RGCN)** — Relational Graph Convolutional Network operating directly on the multi-relational graph with 788 node features across 7 relation types

The system includes a FastAPI backend, React TypeScript frontend dashboard, and a complete ML training/evaluation pipeline.

---

## Model Results

### RGCN (2-layer RGCNConv)

| Metric    | Value  |
|-----------|--------|
| Accuracy  | 85.78% |
| Precision | 67.96% |
| Recall    | 89.45% |
| F1-Score  | 77.24% |
| ROC-AUC   | 0.9415 |

- Architecture: 2-layer `RGCNConv` (PyG) with BatchNorm, ReLU, Dropout(0.3)
- Input: 788 features (20 profile + 768 text embeddings), 7 relation types
- Basis decomposition: 4 bases
- Trained for 24 epochs (early stopping, patience=30)
- Checkpoint: `models/rgcn_best.pt`
- Results: `results/rgcn_results.json`

### HistGradientBoosting (sklearn)

| Metric    | Value  |
|-----------|--------|
| Accuracy  | 93.77% |
| Precision | 87.30% |
| Recall    | 90.00% |
| F1-Score  | 88.63% |
| ROC-AUC   | 0.9827 |

- Model: `sklearn.ensemble.HistGradientBoostingClassifier`
- Input: 806 tabular features (20 profile + 768 text embeddings + 18 SNA)
- Saved as: `models/model.pkl`
- Feature dataset: `results/ml_dataset.csv`

> **Note:** HistGradientBoosting achieves higher overall accuracy and F1 using 806 tabular features. The RGCN operates on graph structure directly and achieves strong ROC-AUC (0.9415) using 788 node features and 7 relation types.

---

## MGTAB Dataset

- **10,199** Twitter user nodes
- **1,700,108** multi-relational edges
- **7 relation types:** followers, friends, mentions, replies, quotes, urls, hashtags
- **788 node features:** 20 profile attributes + 768 text embedding dimensions
- Labels: Binary (Human=0, Bot=1)

---

## Repository Structure

```
MGTAB-Bot-SNA/
├── backend/              # FastAPI backend
│   ├── api.py            # Route definitions
│   ├── services.py       # SNAService (graph, SNA, ML, coordination)
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── config.py         # Configuration constants
│   └── tests/            # pytest test suite
├── frontend/             # React TypeScript dashboard (Vite)
│   ├── src/pages/        # Dashboard, Users, Network, Communities, etc.
│   ├── src/mock/         # Mock data adapter (offline mode)
│   └── docs/             # API contract documentation
├── ml/                   # Machine learning pipeline
│   ├── rgcn_model.py     # RGCNBotDetector architecture
│   └── rgcn_train.py     # RGCN training pipeline
├── models/               # Trained model checkpoints
│   ├── model.pkl         # HistGradientBoosting (sklearn)
│   └── rgcn_best.pt      # RGCN checkpoint (PyTorch)
├── results/              # Evaluation results
│   ├── rgcn_results.json # RGCN metrics, architecture, confusion matrix
│   ├── ml_dataset.csv    # 806-feature tabular dataset
│   └── final_model_metrics.csv  # sklearn baseline metrics
├── dataset/              # MGTAB graph data (PyG tensors)
│   ├── features.pt       # Node feature matrix [10199, 788]
│   ├── edge_index.pt     # Edge connectivity [2, E]
│   ├── edge_type.pt      # Relation types [E]
│   └── labels.pt         # Ground truth labels [10199]
├── eda/                  # Exploratory data analysis
├── notebooks/            # Jupyter notebooks
└── requirements.txt      # Python dependencies
```

---

## API Endpoints

| Method | Endpoint              | Description                                    | Model Used            |
|--------|-----------------------|------------------------------------------------|-----------------------|
| GET    | `/health`             | System health check                            | —                     |
| GET    | `/statistics`         | Graph topology statistics                      | —                     |
| GET    | `/user/{id}`          | SNA metrics for a user                         | —                     |
| GET    | `/user/{id}/network`  | Ego-network subgraph                           | —                     |
| GET    | `/communities`        | Paginated community listing                    | —                     |
| GET    | `/community/{id}`     | Community detail + coordination analysis       | —                     |
| GET    | `/model-performance`  | Real evaluation metrics from persisted results | Both (read-only)      |
| POST   | `/predict`            | Bot/human prediction for a user ID             | **HistGradientBoosting** |

### Important: `/predict` vs RGCN

- **`/predict`** uses the HistGradientBoosting sklearn model (`models/model.pkl`) with 806 tabular features from `results/ml_dataset.csv`. It does NOT use the RGCN.
- **RGCN** evaluation results are served read-only through `/model-performance`, loaded from `results/rgcn_results.json`. RGCN inference requires the full PyG graph (features.pt, edge_index.pt, edge_type.pt) and is not served through the tabular prediction endpoint.

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- PyTorch and PyTorch Geometric (for RGCN)

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI backend
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

### Run Tests

```bash
# Run all backend tests
python -m pytest backend/tests/ -v

# Run RGCN-specific tests
python -m pytest backend/tests/test_rgcn.py -v

# Run API endpoint tests
python -m pytest backend/tests/test_api.py -v
```

---

## RGCN Training (Reproduction)

To retrain the RGCN from scratch:

```bash
python -m ml.rgcn_train
```

This will:
1. Load the MGTAB graph from `dataset/` (features.pt, edge_index.pt, edge_type.pt, labels.pt)
2. Create an 80/10/10 stratified node split
3. Train a 2-layer RGCNConv with early stopping (patience=30)
4. Save the best checkpoint to `models/rgcn_best.pt`
5. Save evaluation metrics to `results/rgcn_results.json`

**Note:** The current checkpoint and results should NOT be retrained unless intentionally redesigning the architecture.

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend   | FastAPI, Python 3.10+ |
| Frontend  | React 19, TypeScript, Vite |
| Graph Engine | Cytoscape.js |
| Charts    | Recharts |
| GNN Framework | PyTorch + PyTorch Geometric |
| Traditional ML | scikit-learn (HistGradientBoosting) |
| Graph Analysis | NetworkX |
| Community Detection | Louvain (python-louvain) |

---

## Academic Research Disclaimer

> Detection results indicate potentially coordinated behavioural patterns and topological anomalies. These exploratory research indicators should not be interpreted as definitive proof of malicious intent or verified disinformation campaigns without ground-truth validation.
