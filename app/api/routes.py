from fastapi import APIRouter
from app.services.fund_analysis_service import analyze_funds

router = APIRouter()


@router.get("/")
def root():
    """Root endpoint."""
    return {"message": "OK"}


@router.get("/top5smallcap")
def get_top5_smallcap():
    """Get top 5 small cap funds with analysis."""
    return analyze_funds()
