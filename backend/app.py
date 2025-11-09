from fastapi import FastAPI
from api.routes import router as routes_router

app = FastAPI()
app.include_router(routes_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok"}