from fastapi import FastAPI

app = FastAPI(title="AI Education Assistant Test")

@app.get("/")
async def root():
    return {"message": "AI Education Assistant is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

