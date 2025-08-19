import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from itertools import product

import statsmodels.api as sm
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tools.sm_exceptions import ConvergenceWarning
import warnings
warnings.simplefilter("ignore", ConvergenceWarning)

# --- load monthly PHP/JPY series ---
raw = pd.read_csv("data/phpjpy_monthly.csv", header=[0,1], index_col=0, parse_dates=True)
col = ('Ticker','PHPJPY=X') if ('Ticker','PHPJPY=X') in raw.columns else raw.columns[0]
s = raw[col].rename("phpjpy").asfreq("MS").dropna()

# log-transform for variance stability
y = np.log(s)

# --- small SARIMA grid search by AIC (seasonal=12) ---
p = d = q = range(0, 3)  # keep compact
P = D = Q = range(0, 2)
m = 12
best = (None, np.inf, None)
for (pi, di, qi) in product(p, d, q):
    for (Pi, Di, Qi) in product(P, D, Q):
        try:
            mod = SARIMAX(y, order=(pi, di, qi), seasonal_order=(Pi, Di, Qi, m), enforce_stationarity=False, enforce_invertibility=False)
            res = mod.fit(disp=False)
            if res.aic < best[1]:
                best = ((pi,di,qi,Pi,Di,Qi), res.aic, res)
        except Exception:
            pass

(order) , best_aic, final = best
(p_,d_,q_, P_,D_,Q_) = order
print(f"Best SARIMA({p_},{d_},{q_}) x ({P_},{D_},{Q_},{m}), AIC = {best_aic:.2f}")
print(final.summary())

# --- make output dir ---
out = Path("output")
out.mkdir(exist_ok=True)

# --- forecast next 12 months (back-transform from log) ---
h = 12
fc = final.get_forecast(steps=h)
pred_mean_log = fc.predicted_mean
pred_ci_log = fc.conf_int()
pred_mean = np.exp(pred_mean_log).rename("forecast")
pred_ci = np.exp(pred_ci_log)
pred_ci.columns = ["lower","upper"]

pred_idx = pd.date_range(s.index[-1] + pd.offsets.MonthBegin(1), periods=h, freq="MS")
pred_mean.index = pred_idx
pred_ci.index = pred_idx

# --- save forecast table & plot ---
forecast_df = pd.concat([pred_mean, pred_ci], axis=1)
forecast_df.to_csv(out / "sarima_forecast_12m.csv", float_format="%.6f")

plt.figure()
s.plot(label="observed")
pred_mean.plot(label="forecast")
plt.fill_between(pred_ci.index, pred_ci["lower"], pred_ci["upper"], alpha=0.2)
plt.title(f"SARIMA({p_},{d_},{q_})x({P_},{D_},{Q_},{m}) forecast (12 months)")
plt.xlabel("Date"); plt.ylabel("JPY per 1 PHP")
plt.grid(True); plt.legend(); plt.tight_layout()
plt.savefig(out / "sarima_forecast_12m.png", dpi=160)
plt.close()

# --- residual diagnostics ---
resid = final.resid.dropna().rename("resid")
resid.to_csv(out / "sarima_residuals.csv", float_format="%.6f")

# ACF / PACF
fig = plt.figure()
plot_acf(resid, lags=24)
plt.title("Residuals ACF")
plt.tight_layout()
plt.savefig(out / "diag_resid_acf.png", dpi=160)
plt.close()

fig = plt.figure()
plot_pacf(resid, lags=24, method="ywm")
plt.title("Residuals PACF")
plt.tight_layout()
plt.savefig(out / "diag_resid_pacf.png", dpi=160)
plt.close()

# Ljung-Box (up to lag 12 and 24)
lb12 = acorr_ljungbox(resid, lags=[12], return_df=True)
lb24 = acorr_ljungbox(resid, lags=[24], return_df=True)
lb = pd.concat([lb12.add_suffix("_lag12"), lb24.add_suffix("_lag24")], axis=1)
lb.to_csv(out / "diag_ljungbox.csv", float_format="%.6f")

# QQ plot
fig = plt.figure()
sm.qqplot(resid, line="s")
plt.title("Residuals QQ Plot")
plt.tight_layout()
plt.savefig(out / "diag_resid_qq.png", dpi=160)
plt.close()

print("Saved outputs to:", out.resolve())
