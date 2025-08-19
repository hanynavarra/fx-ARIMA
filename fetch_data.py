import yfinance as yf
import pandas as pd
from pathlib import Path

# make data folder
Path("data").mkdir(exist_ok=True)

# download daily PHP/JPY (JPY per 1 PHP)
df = yf.download("PHPJPY=X", start="2010-01-01")
close = df["Close"].dropna()

# resample to month-start average
monthly = close.resample("MS").mean()
monthly.name = "phpjpy"

# save
out = "data/phpjpy_monthly.csv"
monthly.to_csv(out, header=True)
print(f"Saved {len(monthly)} rows to {out}")
print("Head:\n", monthly.head(), "\nTail:\n", monthly.tail())
