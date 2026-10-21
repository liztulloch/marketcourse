from fastapi import APIRouter, HTTPException

from src.Clients.MarketData import MarketDataClient
from src.Clients.Alpha import AlphaVantageClient
from src.Services.analytics_service import AnalyticsService
from src.Services.Home_view import HomeService


router = APIRouter(
    prefix="/stocks",
    tags=["stocks"]
)


market_client = MarketDataClient()
alpha_client = AlphaVantageClient()
analytics_service = AnalyticsService()

home_service = HomeService(
    market_client,
    alpha_client,
    analytics_service
)


@router.get("/{ticker}/summary")
def get_stock_summary(ticker: str):
    try:
        ticker = ticker.upper()

        return home_service.get_stock_summary(ticker)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )