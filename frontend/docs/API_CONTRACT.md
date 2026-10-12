# Frontend API Contract Specification

**Project:** SNA-Based Detection of Coordinated Misinformation and Bot-Like Behaviour  
**Benchmark Dataset:** MGTAB (Multi-relational Graph Twitter Account Detection Benchmark)  
**Frontend Version:** 1.0.0  
**Backend Framework:** FastAPI (Python 3.10+)

This document defines the exact contracts, endpoints, request formats, and response schemas consumed by the React Frontend.

---

## 1. System Health & Telemetry

### `GET /health`
Used by the frontend header indicator to verify backend connectivity and round-trip latency.

* **Response Status:** `200 OK`
* **Response Body:**
```json
{
  "status": "healthy",
  "version": "FastAPI v0.1.0",
  "dataset": "MGTAB",
  "timestamp": "2026-08-27T12:00:00Z"
}
```

---

## 2. Overview Statistics

### `GET /statistics`
Provides global network counts, classification ratios, and social network analysis metrics.

* **Response Status:** `200 OK`
* **Response Body:**
```json
{
  "total_users": 10199,
  "total_relationships": 147820,
  "bot_count": 2768,
  "human_count": 7431,
  "bot_ratio": 0.2714,
  "community_count": 48,
  "flagged_groups_count": 7,
  "network": {
    "density": 0.00284,
    "average_degree": 28.98,
    "average_clustering": 0.231,
    "connected_components": 12,
    "diameter": 8,
    "modularity": 0.684,
    "transitivity": 0.187
  },
  "relationship_breakdown": [
    { "type": "FOLLOW", "count": 72410, "percentage": 48.98 },
    { "type": "FRIEND", "count": 41200, "percentage": 27.87 },
    { "type": "RETWEET", "count": 18450, "percentage": 12.48 },
    { "type": "MENTION", "count": 11200, "percentage": 7.58 },
    { "type": "REPLY", "count": 4560, "percentage": 3.09 }
  ],
  "community_size_distribution": [
    { "size_range": "1-25 members", "community_count": 14 },
    { "size_range": "26-100 members", "community_count": 19 },
    { "size_range": "101-500 members", "community_count": 11 },
    { "size_range": "500+ members", "community_count": 4 }
  ],
  "system_insights": [
    "Graph density of 0.00284 with 10,199 active nodes and 147,820 multi-relational edges.",
    "Identified 7 communities with elevated coordination scores (>0.75)."
  ]
}
```

---

## 3. User & Node Investigation

### `GET /user/{id}`
Returns profile details, GNN predictions, centrality metrics, and feature explainability for a user.

* **Path Parameter:** `id` (string/integer)
* **Response Status:** `200 OK` (or `404 Not Found`)
* **Response Body:**
```json
{
  "user_id": "123456789",
  "screen_name": "bot_alpha_node",
  "name": "Tech Trend Echo",
  "prediction": "BOT",
  "probability": 0.934,
  "confidence_score": 0.96,
  "community_id": "17",
  "features": {
    "followers_count": 320,
    "following_count": 4890,
    "statuses_count": 48200,
    "favourites_count": 12,
    "listed_count": 1,
    "created_at": "2023-11-04T12:00:00Z",
    "verified": false,
    "default_profile": true,
    "default_profile_image": true,
    "geo_enabled": false,
    "account_age_days": 280,
    "tweet_frequency_per_day": 172.1
  },
  "network": {
    "degree": 148,
    "in_degree": 14,
    "out_degree": 134,
    "pagerank": 0.00482,
    "betweenness": 0.0381,
    "clustering": 0.042,
    "eigenvector": 0.0019,
    "coreness": 8
  },
  "explanation": [
    {
      "feature": "Following/Follower Asymmetry",
      "importance": 0.88,
      "description": "Disproportionately high following-to-follower ratio",
      "direction": "positive"
    }
  ],
  "recent_activity": {
    "total_tweets_sampled": 500,
    "hashtags": ["#BreakingNews", "#CryptoAirdrop"],
    "mentioned_users": ["987654321", "456789123"],
    "urls_shared": ["https://t.co/short8923a"]
  }
}
```

### `GET /user/{id}/network`
Returns the 1-hop or 2-hop local ego-network around a user.

* **Response Status:** `200 OK`
* **Response Body:**
```json
{
  "nodes": [
    {
      "id": "123456789",
      "label": "Tech Trend Echo",
      "prediction": "BOT",
      "probability": 0.934,
      "community_id": "17",
      "degree": 148,
      "pagerank": 0.00482,
      "is_seed": true
    },
    {
      "id": "555123999",
      "label": "News Radar Bot",
      "prediction": "BOT",
      "probability": 0.892,
      "community_id": "17",
      "degree": 98,
      "pagerank": 0.0019
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "123456789",
      "target": "555123999",
      "relationship": "RETWEET",
      "weight": 4.5
    }
  ],
  "metadata": {
    "total_nodes": 2,
    "total_edges": 1,
    "seed_node": "123456789"
  }
}
```

---

## 4. Multi-Relational Network Visualization

### `GET /network`
Returns nodes and multi-relational edges with optional filtering.

* **Query Parameters:**
  * `prediction` (`ALL`, `BOT`, `HUMAN`)
  * `communityId` (`ALL` or ID)
  * `relationshipType` (`ALL`, `FOLLOW`, `FRIEND`, `RETWEET`, `MENTION`, `REPLY`)
  * `minDegree` (integer)
  * `searchQuery` (string)
  * `maxNodes` (integer, default 100)

* **Response Status:** `200 OK`
* **Response Body:**
```json
{
  "nodes": [ ... ],
  "edges": [ ... ],
  "metadata": {
    "total_nodes": 18,
    "total_edges": 29,
    "is_filtered": true
  }
}
```

---

## 5. Community Analysis

### `GET /communities`
Returns summary of all detected Louvain/Leiden communities.

* **Response Status:** `200 OK`
* **Response Body:**
```json
{
  "total_communities": 48,
  "overall_stats": {
    "largest_community_size": 1420,
    "average_community_size": 212.4,
    "flagged_communities_count": 7
  },
  "communities": [
    {
      "id": "17",
      "member_count": 43,
      "bot_count": 31,
      "human_count": 12,
      "bot_ratio": 0.7209,
      "coordination_score": 0.84,
      "status": "potentially_coordinated",
      "primary_topics": ["Trending Hashtags", "News Retweet Echo"],
      "density": 0.084,
      "average_degree": 18.4
    }
  ]
}
```

### `GET /community/{id}`
Returns in-depth details for a community partition.

* **Response Status:** `200 OK`
* **Response Body:**
```json
{
  "id": "17",
  "member_count": 43,
  "bot_count": 31,
  "human_count": 12,
  "bot_ratio": 0.7209,
  "coordination_score": 0.84,
  "status": "potentially_coordinated",
  "primary_topics": ["Trending Hashtags"],
  "density": 0.084,
  "average_degree": 18.4,
  "signals": [
    {
      "signal": "Synchronized Retweet Bursts",
      "score": 0.91,
      "description": "Multiple accounts retweeting seed accounts within a 5s window"
    }
  ],
  "network_statistics": {
    "internal_edges": 382,
    "external_edges": 49,
    "conductance": 0.113,
    "modularity_contribution": 0.089,
    "clustering_coefficient": 0.442,
    "density": 0.084
  },
  "members": [
    {
      "user_id": "123456789",
      "screen_name": "bot_alpha_node",
      "prediction": "BOT",
      "probability": 0.934,
      "degree": 148,
      "pagerank": 0.00482
    }
  ]
}
```

---

## 6. Coordinated Behavioral Analysis

### `GET /coordination`
Returns detected coordinated bot clusters, signals, and shared entities.

* **Response Status:** `200 OK`
* **Response Body:**
```json
{
  "total_flagged_groups": 7,
  "average_coordination_score": 0.824,
  "top_coordination_signals": [
    { "signal": "Synchronized Retweet Latency (<5s)", "frequency": 6 },
    { "signal": "Repeated Mention Flooding", "frequency": 5 }
  ],
  "groups": [
    {
      "group_id": "GRP-17",
      "community_id": "17",
      "member_count": 43,
      "bot_count": 31,
      "bot_ratio": 0.7209,
      "coordination_score": 0.84,
      "status": "Potentially Coordinated",
      "primary_topic": "Rapid Retweet Cascades",
      "temporal_burst_score": 0.89,
      "subgraph_density": 0.084,
      "signals": [
        {
          "signal": "Synchronous Temporal Action Timestamps",
          "score": 0.91,
          "description": "Standard deviation of retweet latency is under 4.2s"
        }
      ],
      "shared_entities": {
        "urls": [{ "url": "https://t.co/short8923a", "count": 184 }],
        "hashtags": [{ "tag": "#BreakingNews", "count": 320 }],
        "target_accounts": [{ "target": "@globalnews_live", "count": 78 }]
      }
    }
  ]
}
```

---

## 7. Model Performance

### `GET /model-performance`
Returns evaluation benchmarks for the Relational Graph Convolutional Network (RGCN).

* **Response Status:** `200 OK`
* **Response Body:**
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
    "architecture_type": "Relational Graph Convolutional Network",
    "dataset_name": "MGTAB Twitter Benchmark",
    "training_samples": 8159,
    "test_samples": 1020,
    "validation_split": "80/10/10 Stratified Node Split",
    "feature_count": 788,
    "graph_layers": 2,
    "embedding_dimension": 64,
    "epochs_trained": 24
  },
  "all_models": [
    { "model_name": "RGCN (2-layer RGCNConv)", "metrics": { "accuracy": 0.8578, "f1_score": 0.7724, "roc_auc": 0.9415 } },
    { "model_name": "HistGradientBoosting", "metrics": { "accuracy": 0.9377, "f1_score": 0.8863, "roc_auc": 0.9827 } }
  ]
}
```

---

## 8. Real-Time Prediction Endpoint

### `POST /predict`
Runs bot/human inference for a given user ID using the trained sklearn model.

* **Request Body:**
```json
{
  "user_id": 0,
  "features": null
}
```

* **Response Body:**
```json
{
  "status": "success",
  "message": "ML prediction executed successfully.",
  "user_id": 0,
  "prediction": 1,
  "prediction_label": "Bot",
  "probability": 0.934
}
```
