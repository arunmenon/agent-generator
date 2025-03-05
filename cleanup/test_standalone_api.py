from fastapi import FastAPI, Body
from typing import Dict, Any
import uvicorn

app = FastAPI()

@app.get("/test")
async def test_endpoint():
    return {"status": "API is working"}

@app.post("/flow/create")
async def create_flow(request_data: Dict[str, Any] = Body(...)):
    return {
        "status": "success",
        "message": "Flow creation endpoint working",
        "received_data": request_data
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)