from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="FinMind Agent Service")
app.include_router(router)
