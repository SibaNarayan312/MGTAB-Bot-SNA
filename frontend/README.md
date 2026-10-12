# SNA Sentry — Research Intelligence Frontend

> **SNA-Based Detection of Coordinated Misinformation and Bot-Like Behaviour**  
> Built for the **MGTAB (Multi-relational Graph-based Twitter Account Detection Benchmark)**

---

## 📌 Project Overview

This dashboard is the interactive frontend interface for a Social Network Analysis (SNA) and Graph Neural Network (GNN) detection platform. It enables researchers, professors, and cybersecurity evaluators to:

* **Explore Global Network Topology:** Telemetry on 10,199 users and 147,820 multi-relational edges (`FOLLOW`, `FRIEND`, `RETWEET`, `MENTION`, `REPLY`).
* **Investigate Individual Accounts:** GNN classification probabilities, local ego-network subgraphs, and feature importances.
* **Visualize Multi-Relational Networks:** High-performance interactive **Cytoscape.js** graph with multi-edge coloring, layout algorithms (COSE, Concentric, BFS, Grid), zooming, and side inspectors.
* **Analyze Graph Communities:** Modularity clustering, bot-heavy cluster identification, conductance, and density metrics.
* **Detect Coordinated Behavioral Patterns:** Temporal synchronization bursts, shared URL patterns, and hashtag hijacking.
* **Evaluate ML & GNN Models:** RGCN test accuracy (85.78%), F1-score (0.7724), ROC-AUC (0.9415), HistGradientBoosting baseline accuracy (93.77%), 2x2 confusion matrix, and model comparison table.

---

## 🛠️ Technology Stack

* **Framework:** React 19 + TypeScript (Strict Mode)
* **Build Tool:** Vite
* **Styling:** Vanilla CSS + Tailwind CSS (Dark Research Theme)
* **Graph Engine:** Cytoscape.js (Direct canvas rendering with customized multi-relational stylesheets)
* **Charts & Telemetry:** Recharts
* **Icons:** Lucide React
* **Routing:** React Router v7
* **API Client:** Axios with centralized services and mock adapter fallback

---

## 👥 Team Responsibility Boundaries

| Member | Focus Area | Responsibilities |
| :--- | :--- | :--- |
| **Member 1** | Machine Learning / GNN | EDA, preprocessing, GNN model training (RGCN), evaluation metrics, feature explainability |
| **Member 2** | SNA / Backend | Graph construction, centrality measures, community detection, FastAPI backend endpoints |
| **Member 3 (You)** | **Frontend / Dashboard** | **React dashboard, Cytoscape graph, UX, API integration, responsive layouts, documentation** |

---

## 🚀 Quick Start

### 1. Clone & Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Default variables:
```ini
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK=false
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🗺️ Application Routes

* `/dashboard` — High-level telemetry, KPI cards, bot vs human donut chart, and network insights.
* `/users` & `/users/:id` — Account investigation, GNN explainability, centrality metrics, and ego-graph preview.
* `/network` — Full Cytoscape.js multi-relational network explorer with layout switchers and filters.
* `/communities` & `/communities/:id` — Louvain partitions, risk status badges, and member inspection.
* `/coordination` — Coordinated behavioral signals, shared hashtags/URLs, and academic research disclaimers.
* `/model-performance` — 2x2 confusion matrix, ROC-AUC curve, metadata, and baseline comparisons.

---

## 📖 Documentation

* [`docs/API_CONTRACT.md`](./docs/API_CONTRACT.md) — Comprehensive request and response schemas for FastAPI integration.
* [`docs/INTEGRATION.md`](./docs/INTEGRATION.md) — CORS configuration and integration workflow.

---

## 🛡️ Academic Research Disclaimer

> Detection results indicate potentially coordinated behavioural patterns and topological anomalies. These exploratory research indicators should not be interpreted as definitive proof of malicious intent or verified disinformation campaigns without ground-truth validation.
