# MGTAB-Based Bot Detection using SNA & RGCN

> Social Network Analysis and Relational Graph Convolutional Network for Twitter Account Bot Detection
> Benchmarked on the **MGTAB** (Multi-relational Graph-based Twitter Account Detection Benchmark) Dataset

---

## 1. Project Overview & Problem Statement

Social media platforms like Twitter (X) face coordinated disinformation and automated account manipulation. Traditional bot detection methods analyze individual accounts using isolated profile attributes or tweet text, often failing against sophisticated botnets that coordinate across multiple relational channels.

This project delivers an end-to-end bot detection and social network analysis (SNA) research platform designed around the **MGTAB benchmark**:
1. **Multi-Relational Graph Structure:** Captures 7 distinct interaction types (followers, friends, mentions, replies, quotes, URLs, hashtags).
2. **Social Network Analysis (SNA):** Computes centrality indices, PageRank, community partitions (Louvain), and heuristic coordination scores.
3. **Tabular Machine Learning Baseline:** A high-performing `HistGradientBoostingClassifier` operating on 806 features (20 profile attributes + 768 text embeddings + 18 graph SNA metrics).
4. **Relational Graph Convolutional Network (RGCN):** A 2-layer Graph Neural Network operating directly on graph connectivity with 788 node features across 7 relation types.
5. **Interactive Research Dashboard:** React TypeScript interface with Cytoscape.js network visualizer, Recharts telemetry, and dual live-backend / offline-mock capability.

---

## 2. Model Evaluation Results & Provenance

The system features two separate, strictly decoupled model pipelines:

### Comparison Table

| Metric | HistGradientBoosting Baseline | RGCN (2-layer RGCNConv) |
|---|---|---|
| **Pipeline Type** | Tabular ML (sklearn) | Graph Neural Network (PyTorch Geometric) |
| **Input Features** | 806 tabular dimensions | 788 node features + 7 edge relation types |
| **Feature Composition** | 20 profile + 768 text embeddings + 18 SNA | 20 profile + 768 text embeddings |
| **Graph Exploitation** | Precomputed SNA feature vectors | Direct relational edge convolution (`RGCNConv`) |
| **Accuracy** | **93.77%** (0.9377) | **85.78%** (0.8578) |
| **Precision** | **87.30%** (0.8730) | **67.96%** (0.6796) |
| **Recall / Sensitivity** | **90.00%** (0.9000) | **89.45%** (0.8945) |
| **F1-Score** | **88.63%** (0.8863) | **77.24%** (0.7724) |
| **ROC-AUC** | **0.9827** | **0.9415** |
| **Artifact Path** | `models/model.pkl` | `models/rgcn_best.pt` |
| **Results Record** | `results/final_model_metrics.csv` | `results/rgcn_results.json` |
| **API Serving** | Serves online `/predict` endpoint | Evaluated offline; served via `/model-performance` |

### RGCN Confusion Matrix (Holdout Test Set: 1,020 Nodes)

| | Predicted Human | Predicted Bot |
|---|---|---|
| **Actual Human** | **629** (True Negative) | **116** (False Positive) |
| **Actual Bot** | **29** (False Negative) | **246** (True Positive) |

- **Total Test Samples:** 1,020 (80/10/10 Stratified Split)
- **Trainable Parameters:** 273,210
- **Best Training Epoch:** 24 (Early stopping patience = 30)
- **Architecture Details:** 2 layers `RGCNConv` (hidden dimension = 64, 4 bases decomposition, batch normalization, ReLU, dropout = 0.3).
- **Edge Weight Note:** Edge weights (`edge_weight.pt`) are not consumed by the RGCN because PyTorch Geometric 2.8.0 `RGCNConv` does not take edge weights.

> **Honest Comparison Note:** HistGradientBoosting outperforms RGCN in accuracy (93.77% vs 85.78%) and F1 (88.63% vs 77.24%) because it consumes 806 explicit features including pre-extracted high-order SNA metrics. RGCN achieves 0.9415 ROC-AUC directly from graph topology without manual SNA feature engineering.

---

## 3. Architecture & Separation of Concerns

```text
               ┌────────────────────────────────────────────────────────┐
               │                 MGTAB Benchmark Data                   │
               │  - PyG Tensors: features.pt, edge_index.pt, etc.       │
               │  - Tabular Dataset: results/ml_dataset.csv (806 feats) │
               └──────────────────────────┬─────────────────────────────┘
                                          │
                  ┌───────────────────────┴────────────────────────┐
                  ▼                                                ▼
     ┌───────────────────────────┐                   ┌───────────────────────────┐
     │  Tabular Serving Pipeline │                   │   RGCN Graph Pipeline     │
     │  - models/model.pkl       │                   │  - ml/rgcn_model.py       │
     │  - HistGradientBoosting   │                   │  - ml/rgcn_train.py       │
     │  - Consumes 806 features  │                   │  - models/rgcn_best.pt    │
     │  - Fast single-user lookup│                   │  - results/rgcn_results.json
     └─────────────┬─────────────┘                   └─────────────┬─────────────┘
                   │                                               │
                   │ POST /predict                                 │ GET /model-performance
                   ▼                                               ▼
     ┌───────────────────────────────────────────────────────────────────────────┐
     │                      FastAPI Application Layer                            │
     │  - api.py: Routing, parameter validation, HTTP schemas                   │
     │  - services.py: SNAService, model inference, community & coordination     │
     └─────────────────────────────────────┬─────────────────────────────────────┘
                                           │
                                           │ HTTP / JSON
                                           ▼
     ┌───────────────────────────────────────────────────────────────────────────┐
     │                  React TypeScript Research Dashboard                     │
     │  - Overview Statistics & Telemetry                                       │
     │  - Cytoscape.js Multi-Relational Network Visualizer                       │
     │  - Louvain Community Inspector & Coordination Analysis                   │
     │  - Model Performance & ROC-AUC Comparison Dashboard                      │
     │  - Single User Inspection & Real-time Bot Prediction                     │
     └───────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Dataset Provenance & Preparation

- **Dataset:** MGTAB (Multi-relational Graph-based Twitter Account Detection Benchmark, Lu et al., 2022).
- **Nodes:** 10,199 Twitter users (7,431 humans, 2,768 bots).
- **Edges:** 1,700,108 multi-relational directed edges.
- **Relation Types (7):**
  - `0`: followers
  - `1`: friends
  - `2`: mentions
  - `3`: replies
  - `4`: quotes
  - `5`: urls
  - `6`: hashtags

### Dataset Directory Structure (`dataset/`)

- `dataset/features.pt`: Tensor `[10199, 788]` (20 user profile attributes + 768 text embedding dimensions).
- `dataset/edge_index.pt`: LongTensor `[2, 1700108]` (graph connectivity in COO format).
- `dataset/edge_type.pt`: LongTensor `[1700108]` (relation type IDs 0..6).
- `dataset/edge_weight.pt`: FloatTensor `[1700108]` (edge frequency/weight).
- `dataset/labels_bot.pt`: LongTensor `[10199]` (ground truth: 0 = Human, 1 = Bot).
- `dataset/labels_stance.pt`: LongTensor `[10199]` (ground truth stance labels).

### Tabular Dataset Preparation

`results/ml_dataset.csv` contains 10,199 rows and 807 columns (806 features + `bot_label`). It is generated by concatenating profile features, 768 text embeddings, and 18 SNA metrics:
```bash
python ml/prepare_dataset.py
```
*(Note: `results/ml_dataset.csv` is ~88 MB and should remain excluded from Git commits).*

---

## 5. Repository Structure

```
MGTAB-Bot-SNA/
├── backend/                  # FastAPI backend service layer
│   ├── api.py                # FastAPI routes & endpoints
│   ├── config.py             # Environment configuration & paths
│   ├── schemas.py            # Pydantic request & response models
│   ├── services.py           # Application service layer (SNA, ML, Cache)
│   ├── graph_builder.py      # NetworkX multi-relational graph loader
│   ├── sna.py                # SNA metrics engine (PageRank, centrality, clustering)
│   ├── community.py          # Louvain community detection engine
│   ├── coordination.py       # Heuristic network coordination analyzer
│   └── tests/                # Complete pytest test suite (36 tests)
│       ├── test_api.py       # Endpoints & schema contract tests (15 tests)
│       ├── test_rgcn.py      # RGCN architecture & checkpoint tests (10 tests)
│       ├── test_graph_builder.py # MultiDiGraph & subgraph tests (4 tests)
│       ├── test_sna.py       # Topological & centrality tests (3 tests)
│       ├── test_community.py # Community detection tests (2 tests)
│       └── test_coordination.py # Behavioral coordination tests (2 tests)
├── frontend/                 # React 19 + TypeScript + Vite Dashboard
│   ├── src/
│   │   ├── pages/            # Dashboard, UserAnalysis, NetworkAnalysis, etc.
│   │   ├── components/       # Reusable UI cards, tables, charts, Cytoscape view
│   │   ├── services/         # Axios API clients with fallback handling
│   │   ├── mock/             # Isolated mock data & mock adapter
│   │   └── types/            # TypeScript type declarations
│   ├── docs/                 # Frontend API contract & integration guides
│   └── package.json          # Vite, React, Cytoscape, Tailwind, Recharts
├── ml/                       # Machine Learning & GNN pipelines
│   ├── rgcn_model.py         # RGCNBotDetector architecture (PyTorch Geometric)
│   ├── rgcn_train.py         # 80/10/10 stratified training & evaluation script
│   ├── baseline.py           # Traditional ML models training (HistGradientBoosting)
│   ├── prepare_dataset.py    # 806-feature tabular dataset builder
│   └── model_comparison.py   # Baseline evaluation comparison generator
├── models/                   # Persisted model checkpoints
│   ├── model.pkl             # Trained HistGradientBoostingClassifier (sklearn)
│   └── rgcn_best.pt          # Best trained RGCN PyTorch checkpoint (epoch 24)
├── results/                  # Persisted evaluation artifacts & metrics
│   ├── rgcn_results.json     # RGCN metrics, confusion matrix & hyperparameters
│   ├── final_model_metrics.csv # HistGradientBoosting evaluation metrics
│   ├── all_models_comparison.csv # Comparison across all benchmarked models
│   ├── sna_features.csv      # Precomputed SNA feature vectors
│   └── ml_dataset.csv        # Complete 806-feature dataset (~88 MB)
├── dataset/                  # MGTAB raw PyTorch graph tensors
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 6. Installation & Prerequisites

### Supported Environment
- **OS:** Windows 10/11, Linux (Ubuntu 20.04+), macOS
- **Python:** 3.10 or 3.11 (verified on Python 3.11.5)
- **Node.js:** v18.0.0 or higher
- **npm:** v9.0.0 or higher

### Step 1: Clone Repository
```bash
git clone https://github.com/SibaNarayan312/MGTAB-Bot-SNA.git
cd MGTAB-Bot-SNA
```

### Step 2: Set Up Python Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

**Linux / macOS (Bash):**
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 7. Environment Configuration

### Backend Configuration
Backend configuration is managed via `backend/config.py`. Optional environment variables:

| Variable | Default Value | Description |
|---|---|---|
| `MGTAB_DATASET_DIR` | `<project_root>/dataset` | Path to PyTorch tensor files |
| `MGTAB_RESULTS_DIR` | `<project_root>/results` | Path to precomputed results & metrics |
| `MGTAB_MODELS_DIR` | `<project_root>/models` | Path to model checkpoints |
| `MGTAB_CACHE_ENABLED` | `true` | In-memory cache for API endpoints |

### Frontend Configuration
Create or edit `frontend/.env`:
```ini
# Backend API Base URL
VITE_API_BASE_URL=http://localhost:8000

# Force offline mock mode (true/false)
VITE_USE_MOCK=false

# Force mock prediction only (true/false)
VITE_USE_MOCK_PREDICTION=false
```

---

## 8. Running the Application

### 1. Launch FastAPI Backend

**Windows (PowerShell):**
```powershell
python -m uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
```

**Linux / macOS (Bash):**
```bash
uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
```

- API Base: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/health`

### 2. Launch React Frontend

```bash
cd frontend
npm run dev
```

- Dashboard UI: `http://localhost:5173`
- Top Header Badge: Displays **`FastAPI Live (<latency>ms)`** in green when the backend is active.

---

## 9. API Specification & Examples

### `GET /health`
Verifies backend operational status and dataset loading.
```bash
curl http://127.0.0.1:8000/health
```
```json
{
  "status": "healthy",
  "graph_loaded": true,
  "num_nodes": 10199,
  "num_edges": 1700108
}
```

### `GET /statistics`
Returns global network topology, edge type breakdown, and graph density.
```bash
curl http://127.0.0.1:8000/statistics
```

### `GET /user/{user_id}`
Returns SNA metrics, centrality indices, PageRank, community assignment, and coordination score.
```bash
curl http://127.0.0.1:8000/user/0
```

### `GET /model-performance`
Returns verified evaluation metrics, confusion matrix, model comparisons, and feature importances.
```bash
curl http://127.0.0.1:8000/model-performance
```
```json
{
  "status": "available",
  "metrics": {
    "accuracy": 0.8578,
    "precision": 0.6796,
    "recall": 0.8945,
    "f1_score": 0.7724,
    "roc_auc": 0.9415
  },
  "confusion_matrix": {
    "true_negative": 629,
    "false_positive": 116,
    "false_negative": 29,
    "true_positive": 246
  },
  "metadata": {
    "model_name": "RGCN (2-layer RGCNConv)",
    "architecture_type": "Relational Graph Convolutional Network"
  },
  "baseline_comparisons": [
    { "model_name": "HistGradientBoosting", "accuracy": 0.9377, "f1_score": 0.8863, "roc_auc": 0.9827 },
    { "model_name": "Logistic Regression", "accuracy": 0.9020, "f1_score": 0.8302, "roc_auc": null },
    { "model_name": "Random Forest", "accuracy": 0.8961, "f1_score": 0.7897, "roc_auc": null },
    { "model_name": "RGCN (2-layer)", "accuracy": 0.8578, "f1_score": 0.7724, "roc_auc": 0.9415 }
  ]
}
```

### `POST /predict`
Performs bot detection inference for a given user ID using the trained **HistGradientBoosting** tabular model.
```bash
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\"user_id\": 0}"
```
```json
{
  "status": "success",
  "message": "ML prediction executed successfully.",
  "user_id": 0,
  "prediction": 0,
  "prediction_label": "Human",
  "probability": 0.9974,
  "model_used": "HistGradientBoosting (sklearn, 806 tabular features)"
}
```

---

## 10. Reproducing Tests & Verification

### Run Complete Backend Test Suite (36 Tests)
```bash
python -m pytest backend/tests/ -v
```

### Run Focused Sub-Suites
```bash
# API & RGCN contract tests (25 tests)
python -m pytest backend/tests/test_api.py backend/tests/test_rgcn.py -v

# Graph Builder, SNA, Community, Coordination regression tests (11 tests)
python -m pytest backend/tests/test_graph_builder.py backend/tests/test_sna.py backend/tests/test_community.py backend/tests/test_coordination.py -v
```

### Run Frontend Verification
```bash
cd frontend

# Code style and syntax linting (0 errors)
npm run lint

# TypeScript strict typechecking and production build (0 errors)
npm run build
```

---

## 11. RGCN Retraining Guide (Optional Reproduction)

To train the RGCN from scratch using the PyTorch tensors:
```bash
python -m ml.rgcn_train
```

What the script executes:
1. Loads PyG tensors from `dataset/` (`features.pt`, `edge_index.pt`, `edge_type.pt`, `labels_bot.pt`).
2. Creates an 80% train / 10% validation / 10% test stratified node split (seed = 42).
3. Instantiates `RGCNBotDetector` with 2 `RGCNConv` layers (hidden dimension 64, 4 bases).
4. Trains using Adam optimizer (lr=0.01, weight_decay=5e-4) with class-weighted cross-entropy loss.
5. Monitors validation ROC-AUC with early stopping (patience=30 epochs).
6. Persists the optimal checkpoint to `models/rgcn_best.pt` and metrics to `results/rgcn_results.json`.

*(Note: Do not retrain unless intentionally experimenting with new hyperparameters or architecture changes).*

---

## 12. Current Limitations & Future Work

1. **Full-Graph Transductive GNN Inference:** The current RGCN model is trained full-batch on the static graph tensor in CPU/GPU memory. Dynamic inference for unseen out-of-graph accounts currently relies on the HistGradientBoosting tabular endpoint. Future work includes inductive mini-batch neighborhood sampling (e.g., PyG `NeighborLoader`) for real-time streaming accounts.
2. **Tabular Feature Dependency:** The HistGradientBoosting model depends on precomputed SNA features from `results/ml_dataset.csv`. Serving brand-new accounts with zero graph history requires cold-start heuristics based purely on profile metadata.
3. **Coordination Heuristics:** Coordination detection evaluates multi-relational interaction density, mutual reciprocity, and shared URL/hashtag similarity. The MGTAB graph benchmark does not include high-resolution timestamped tweet bursts; temporal analysis is therefore not claimed.
4. **Research Disclaimer:** All risk classifications and coordination scores are academic indicators of structural anomaly. They should be verified through ground-truth validation before taking automated moderation actions.
