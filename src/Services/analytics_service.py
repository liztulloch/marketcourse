import math
import statistics


class AnalyticsService:
    def get_return(self, history):
        closes = history["c"]

        if len(closes) < 2:
            return None

        return ((closes[-1] - closes[0]) / closes[0]) * 100

    def get_moving_average(self, history, days):
        closes = history["c"]

        if len(closes) < days:
            return None

        return sum(closes[-days:]) / days

    def get_volatility(self, history):
        closes = history["c"]

        if len(closes) < 2:
            return None

        daily_returns = [
            (closes[i] - closes[i - 1]) / closes[i - 1]
            for i in range(1, len(closes))
        ]

        return statistics.stdev(daily_returns) * math.sqrt(252) * 100
    def analyze(self, history, income_statement):
        return {
            "return_percent": self.get_return(history),
            "sma_50": self.get_moving_average(history, 50),
            "sma_200": self.get_moving_average(history, 200),
            "annualized_volatility": self.get_volatility(history),
            "revenue_growth": self.get_revenue_growth(income_statement)
        }

    def get_revenue_growth(self, income_statement):
        reports = income_statement.get("annualReports", [])

        if len(reports) < 2:
            return None

        current_revenue = float(reports[0]["totalRevenue"])
        previous_revenue = float(reports[1]["totalRevenue"])

        if previous_revenue == 0:
            return None

        return ((current_revenue - previous_revenue) / previous_revenue) * 100