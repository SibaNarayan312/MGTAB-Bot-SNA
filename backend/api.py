import logging
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import (
    HealthResponse,
    GraphStatisticsResponse,
    UserResponse,
    UserNetworkResponse,
    CommunitiesResponse,
    CommunityDetailResponse,
    PredictionRequest,
    PredictionResponse,
)
from backend.services import SNAService

logger = logging.getLogger("backend.api")

# Singleton Service Instance
sna_service = SNAService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI startup and shutdown events."""
    logger.info("Initializing SNA Backend Services...")
    try:
        sna_service.initialize()
        logger.info("SNA Backend API is ready to serve requests.")
    except Exception as e:
        logger.error(f"Failed to initialize SNA Backend Services: {e}")
        raise e
    yield
    logger.info("Shutting down SNA Backend API...")

app = FastAPI(
    title="MGTAB Social Network Analysis Backend API",
    description=(
        "Production-quality SNA & Coordination Analysis backend for the "
        "Multi-relational Graph-based Twitter Account Detection Benchmark (MGTAB)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware Setup for React Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["System"])
async def root():
    """Root endpoint providing API overview and documentation links."""
    return {
        "message": "Welcome to MGTAB Social Network Analysis Backend API",
        "version": "1.0.0",
        "documentation": "http://127.0.0.1:8000/docs",
        "health_check": "http://127.0.0.1:8000/health",
        "statistics": "http://127.0.0.1:8000/statistics",
        "communities": "http://127.0.0.1:8000/communities"
    }

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def get_health():
    """Health check endpoint confirming API status and dataset graph state."""
    is_loaded = sna_service.loader is not None and sna_service.loader.graph is not None
    return HealthResponse(
        status="healthy",
        graph_loaded=is_loaded,
        num_nodes=sna_service.loader.num_nodes if is_loaded else 0,
        num_edges=sna_service.loader.num_edges if is_loaded else 0,
    )

@app.get("/statistics", response_model=GraphStatisticsResponse, tags=["Graph Analytics"])
async def get_statistics():
    """Returns global network statistics, relation distributions, and community count."""
    try:
        stats = sna_service.get_global_statistics()
        return GraphStatisticsResponse(**stats)
    except Exception as e:
        logger.error(f"Error fetching global statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}", response_model=UserResponse, tags=["User Analytics"])
async def get_user_analytics(user_id: int = Path(..., ge=0, description="Node user ID")):
    """Returns comprehensive SNA metrics, PageRank, community assignment, and coordination scores for a user."""
    try:
        data = sna_service.get_user_details(user_id)
        return UserResponse(**data)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching user {user_id} analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/network", response_model=UserNetworkResponse, tags=["User Analytics"])
async def get_user_network(
    user_id: int = Path(..., ge=0, description="Node user ID"),
    depth: int = Query(1, ge=1, le=3, description="Subnetwork traversal depth (hops)"),
    max_nodes: int = Query(50, ge=5, le=200, description="Maximum nodes returned in visualization payload"),
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type (followers, friends, mentions, replies, quotes, urls, hashtags)")
):
    """Returns user ego-network graph formatted for frontend visualization (Cytoscape / D3)."""
    try:
        net_data = sna_service.get_user_network(
            user_id=user_id,
            depth=depth,
            max_nodes=max_nodes,
            relationship_type=relationship_type
        )
        return UserNetworkResponse(**net_data)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching user {user_id} network graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/communities", response_model=CommunitiesResponse, tags=["Community Detection"])
async def get_communities(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    min_size: int = Query(1, ge=1, description="Minimum community size filter")
):
    """Returns paginated community summaries detected via Louvain graph projection."""
    try:
        res = sna_service.get_communities(page=page, page_size=page_size, min_size=min_size)
        return CommunitiesResponse(**res)
    except Exception as e:
        logger.error(f"Error fetching communities list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/community/{community_id}", response_model=CommunityDetailResponse, tags=["Community Detection"])
async def get_community_detail(community_id: int = Path(..., ge=0, description="Community ID")):
    """Returns detailed statistics, top nodes, relation distribution, and coordination analysis for a community."""
    try:
        detail = sna_service.get_community_detail(community_id)
        return CommunityDetailResponse(**detail)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching community {community_id} detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/coordination", tags=["Coordination Analysis"])
async def get_coordination_summary():
    """Returns global coordination summary and group metrics for frontend coordination dashboard."""
    try:
        return sna_service.get_coordination_summary()
    except Exception as e:
        logger.error(f"Error fetching coordination summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/network", response_model=UserNetworkResponse, tags=["Graph Analytics"])
async def get_general_network(
    max_nodes: int = Query(100, ge=5, le=500),
    relationship_type: Optional[str] = Query(None),
    min_degree: int = Query(0, ge=0)
):
    """Returns top-connected network visualization graph payload for frontend Network page."""
    try:
        return UserNetworkResponse(**sna_service.get_network_graph(
            max_nodes=max_nodes,
            relationship_type=relationship_type,
            min_degree=min_degree
        ))
    except Exception as e:
        logger.error(f"Error fetching network graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/network/subgraph", response_model=UserNetworkResponse, tags=["Graph Analytics"])
async def get_network_subgraph(
    seed_user_id: int = Query(0, ge=0),
    depth: int = Query(1, ge=1, le=3)
):
    """Returns subgraph for a seed user ID."""
    try:
        net_data = sna_service.get_user_network(user_id=seed_user_id, depth=depth)
        return UserNetworkResponse(**net_data)
    except Exception as e:
        logger.error(f"Error fetching network subgraph for seed {seed_user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model-performance", tags=["Machine Learning Integration"])
async def get_model_performance():
    """Returns model performance metrics and ROC curve data for Model Performance page."""
    try:
        return sna_service.get_model_performance()
    except Exception as e:
        logger.error(f"Error fetching model performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict", response_model=PredictionResponse, tags=["Machine Learning Integration"])
async def predict_bot(request: PredictionRequest):
    """
    ML Prediction Endpoint (Plug-in contract for Data Science team member).
    Returns graceful status if model.pkl is not yet trained/mounted.
    """
    try:
        res = sna_service.predict_user_bot(user_id=request.user_id, features=request.features)
        return PredictionResponse(**res)
    except Exception as e:
        logger.error(f"Error executing prediction for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
