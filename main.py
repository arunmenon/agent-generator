# src/agent_creator/main.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run("agent_creator.api.api:app", host="0.0.0.0", port=8000, reload=True)
