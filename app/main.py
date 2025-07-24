from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Small Cap Fund Advisor", version="1.1")

# Include the router
app.include_router(router)
