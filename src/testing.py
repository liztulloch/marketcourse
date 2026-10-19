from Clients.MarketData import MarketDataClient
from Clients.Alpha import AlphaVantageClient
from Services.analytics_service import AnalyticsService

market_client = MarketDataClient()
alpha_client = AlphaVantageClient()
analytics = AnalyticsService()

history = market_client.get_historical_prices(
    "AAPL",
    "2025-10-19",
    "2026-10-19"
)

income_statement = alpha_client.get_income_statement("AAPL")

results = analytics.analyze(history, income_statement)

print(results)