import yfinance as yf
data = yf.download("QQQ", period="1y")
close = data['Close']['QQQ']
vol = data['Volume']['QQQ']

sma5 = close.rolling(5).mean()
sma20 = close.rolling(20).mean()
sma50 = close.rolling(50).mean()
sma200 = close.rolling(200).mean()
v_sma20 = vol.rolling(20).mean()
v_sma50 = vol.rolling(50).mean()

d = "2026-08-11"
px = close.loc[d]
v = vol.loc[d]

# 5D dist:
dist5 = (px - sma5.loc[d])/sma5.loc[d] * 100
dist20 = (px - sma20.loc[d])/sma20.loc[d] * 100
dist50 = (px - sma50.loc[d])/sma50.loc[d] * 100
dist200 = (px - sma200.loc[d])/sma200.loc[d] * 100

def perf(days):
    return (px - close.iloc[close.index.get_loc(d) - days]) / close.iloc[close.index.get_loc(d) - days] * 100

print("Perf 5D:", perf(5))
print("Perf 20D:", perf(20))
print("Perf 50D:", perf(50))
print("Perf 200D:", perf(200))

print("Dist 5D:", dist5)
print("Dist 20D:", dist20)
print("Dist 50D:", dist50)
print("Dist 200D:", dist200)

print("V:", v)
print("VSM20:", v_sma20.loc[d])
print("VSM50:", v_sma50.loc[d])
print("RV20?:", (v / v_sma20.loc[d] ) * 100)
print("RV50?:", (v / v_sma50.loc[d] ) * 100)
print("RV20 alt:", (v - v_sma20.loc[d])/v_sma20.loc[d] * 100)
print("RV50 alt:", (v - v_sma50.loc[d])/v_sma50.loc[d] * 100)

