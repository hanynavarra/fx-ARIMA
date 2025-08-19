import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 1) load the monthly csv (handles both single- and multi-row headers)
path = Path("data/phpjpy_monthly.csv")

try:
    df = pd.read_csv(path, header=[0,1], index_col=0, parse_dates=True)
    # If it's a MultiIndex header, pick the PHPJPY=X column
    if isinstance(df.columns, pd.MultiIndex):
        # prefer ('Ticker','PHPJPY=X') if present; otherwise take the first column
        col = ('Ticker', 'PHPJPY=X') if ('Ticker','PHPJPY=X') in df.columns else df.columns[0]
        s = df[col].rename("phpjpy")
    else:
        s = df.iloc[:,0].rename("phpjpy")
except Exception:
    # fallback: simple header
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    s = df.iloc[:,0].rename("phpjpy")

# 2) basic info
print("Rows:", len(s), "Start:", s.index.min().date(), "End:", s.index.max().date())
print(s.head())

# 3) quick plot
plt.figure()
s.plot()
plt.title("PHP/JPY (Monthly Average)")
plt.xlabel("Date")
plt.ylabel("JPY per 1 PHP")
plt.grid(True)
plt.tight_layout()
plt.show()
