"""
Minimal API example to test the endpoint routing
"""

from fastapi import FastAPI, Body
from typing import Dict, Any
import uvicorn

app = FastAPI()

@app.get("/test")
def test_endpoint():
    return {"status": "API is working"}

@app.post("/flow/create")
def create_flow(
    data: Dict[str, Any] = Body(...)
):
    return {
        "status": "success", 
        "message": "Flow endpoint working",
        "received": data
    }

if __name__ == "__main__":
    print("Starting minimal API server on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)