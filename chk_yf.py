import yfinance as yf
data = yf.download("QQQ", period="1y")
print(data.tail())
