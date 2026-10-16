
from marketdata import MarketDataClient 

client = MarketDataClient()

data = client.get_current_quote(
    "AAPL",
  
)

print(data)