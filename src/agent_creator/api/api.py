# src/my_project/api/api.py
from fastapi import FastAPI
from .db_handler import init_db
from fastapi.middleware.cors import CORSMiddleware
from .routers import meta_agent, crews, flow
from .services.crew_service import load_all_crews_from_db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],    # critical to allow OPTIONS, POST, etc.
    allow_headers=["*"],
)

# Add a test endpoint directly at the root
@app.get("/")
def root():
    return {"message": "API root is working"}

@app.get("/test")
def test_endpoint():
    return {"status": "API is working"}

# Debug endpoint to confirm flow router is loaded
@app.get("/flow-test")
def flow_test():
    return {"status": "Flow module root endpoint"}

# More detailed debug endpoint
@app.get("/debug-info")
def debug_info():
    import sys
    import os
    
    router_info = {}
    # Explicitly try to import routers
    try:
        from .routers import flow
        router_info["flow"] = "imported successfully"
        if hasattr(flow, "router"):
            router_info["flow_router"] = "exists"
            if hasattr(flow.router, "routes"):
                router_info["flow_routes"] = [
                    {"path": route.path, "name": route.name} 
                    for route in flow.router.routes
                ]
    except Exception as e:
        router_info["flow_error"] = str(e)
        
    # Debug endpoints to see all registered routes
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods) if hasattr(route, "methods") else None
        })
        
    return {
        "routes": routes,
        "python_path": sys.path,
        "cwd": os.getcwd(),
        "router_info": router_info
    }

app.include_router(meta_agent.router, prefix="/meta-agent", tags=["meta-agent"])
app.include_router(crews.router, prefix="/crews", tags=["crews"])
app.include_router(flow.router, prefix="/flow", tags=["flow"])

@app.on_event("startup")
def startup_event():
    init_db()
    load_all_crews_from_db()
