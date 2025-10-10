from fastapi import FastAPI

app = FastAPI(title="AI Education Assistant", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "AI Education Assistant is running!", "status": "success"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "AI Education Assistant"}

@app.get("/api/v1/status")
async def api_status():
    return {
        "service": "AI Education Assistant",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "api_status": "/api/v1/status",
            "docs": "/docs"
        }
    }

