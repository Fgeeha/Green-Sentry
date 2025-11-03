from fastapi import APIRouter

router = APIRouter()

@app.get("/metrics")
async def metrics():
    return {"status": "ok"}