import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import product
from pathlib import Path
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tools.sm_exceptions import ConvergenceWarning
import warnings

warnings.simplefilter("ignore", ConvergenceWarning)

# --- load monthly PHP/JPY ---
s = pd.read_csv("data/phpjpy_monthly.csv", header=[0,1], index_col=0, parse_dates=True)
col = ('Ticker','PHPJPY=X') if ('Ticker','PHPJPY=X') in s.columns else s.columns[0]
s = s[col].rename("phpjpy").asfreq("MS").dropna()

# --- log-transform for stability ---
y = np.log(s)

# --- small grid search by AIC ---
cands = [(p,d,q) for p in range(0,4) for d in range(0,3) for q in range(0,4)]
best = (None, np.inf, None)
for p,d,q in cands:
    try:
        res = ARIMA(y, order=(p,d,q)).fit()
        if res.aic < best[1]:
            best = ((p,d,q), res.aic, res)
    except Exception:
        pass

best_order, best_aic, final = best
print("Best (p,d,q):", best_order, "AIC:", round(best_aic,2))

# --- forecast next 12 months ---
h = 12
fc = final.get_forecast(steps=h)
pred_mean_log = fc.predicted_mean
pred_ci_log = fc.conf_int()

# back-transform to levels
pred_mean = np.exp(pred_mean_log).rename("forecast")
pred_ci = np.exp(pred_ci_log)
pred_ci.columns = ["lower","upper"]

pred_index = pd.date_range(s.index[-1] + pd.offsets.MonthBegin(1), periods=h, freq="MS")
pred_mean.index = pred_index
pred_ci.index = pred_index

# --- outputs folder ---
outdir = Path("output")
outdir.mkdir(exist_ok=True)

# 1) forecast table
forecast_df = pd.concat([pred_mean, pred_ci], axis=1)
forecast_df.to_csv(outdir / "forecast_12m.csv", float_format="%.6f")

# 2) residuals
resid = final.resid.rename("resid")
resid.to_csv(outdir / "residuals.csv", float_format="%.6f")

# 3) model summary
with open(outdir / "model_summary.txt", "w") as f:
    f.write(final.summary().as_text())

# 4) plot & save PNG
plt.figure()
s.plot(label="observed")
pred_mean.plot(label="forecast")
plt.fill_between(forecast_df.index, forecast_df["lower"], forecast_df["upper"], alpha=0.2)
plt.title(f"PHP/JPY ARIMA{best_order} forecast ({h} months)")
plt.xlabel("Date"); plt.ylabel("JPY per 1 PHP")
plt.grid(True); plt.legend(); plt.tight_layout()
plt.savefig(outdir / "forecast_12m.png", dpi=160)
plt.close()

print("Saved:",
      outdir / "forecast_12m.csv",
      outdir / "residuals.csv",
      outdir / "model_summary.txt",
      outdir / "forecast_12m.png", sep="\n- ")
