from datetime import date, timedelta


class HomeService:
    def __init__(self, market_client, alpha_client, analytics_service):
        self.market_client = market_client
        self.alpha_client = alpha_client
        self.analytics = analytics_service
        
    def get_stock_summary(self, ticker):
        end_date = date.today()
        start_date = end_date - timedelta(days=365)

        history = self.market_client.get_historical_prices(
            ticker,
            start_date.isoformat(),
            end_date.isoformat()
        )

        quote = self.market_client.get_current_quote(ticker)
        income_statement = self.alpha_client.get_income_statement(ticker)
        analytics = self.analytics.analyze(history, income_statement)

        return {
            "ticker": ticker,
            "current_price": quote["last"][0],
            **analytics,
            "price_history": history["c"][-30:]
        }
