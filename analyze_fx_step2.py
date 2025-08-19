import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tools.sm_exceptions import ConvergenceWarning
import warnings

warnings.simplefilter("ignore", ConvergenceWarning)

# 1) load series
s = pd.read_csv("data/phpjpy_monthly.csv", header=[0,1], index_col=0, parse_dates=True)
col = ('Ticker','PHPJPY=X') if ('Ticker','PHPJPY=X') in s.columns else s.columns[0]
s = s[col].rename("phpjpy").asfreq("MS").dropna()

# 2) (optional) log transform for stability
y = np.log(s)

# 3) train/test split (last 12 months as test)
h = 12
y_train, y_test = y.iloc[:-h], y.iloc[-h:]

# 4) simple grid search by AIC
candidates = list(product(range(0,4), range(0,3), range(0,4)))  # p=0..3, d=0..2, q=0..3
best = (None, np.inf)
for p,d,q in candidates:
    try:
        res = ARIMA(y_train, order=(p,d,q)).fit()
        if res.aic < best[1]:
            best = ((p,d,q), res.aic)
    except Exception:
        pass

best_order, best_aic = best
print("Best (p,d,q):", best_order, "AIC:", round(best_aic,2))

# 5) refit on full sample and forecast h steps
final = ARIMA(y, order=best_order).fit()
print(final.summary())

fc = final.get_forecast(steps=h)
pred_mean_log = fc.predicted_mean
pred_ci_log = fc.conf_int()

# back-transform from log to level
pred_mean = np.exp(pred_mean_log)
pred_ci = np.exp(pred_ci_log)
pred_mean.name = "forecast"

# 6) plot
plt.figure()
s.plot(label="observed")
pred_index = pd.date_range(s.index[-1] + pd.offsets.MonthBegin(1), periods=h, freq="MS")
pred_mean.index = pred_index
pred_ci.index = pred_index
pred_mean.plot(label="forecast")
plt.fill_between(pred_ci.index, pred_ci.iloc[:,0], pred_ci.iloc[:,1], alpha=0.2)
plt.title(f"PHP/JPY ARIMA{best_order} forecast ({h} months)")
plt.xlabel("Date"); plt.ylabel("JPY per 1 PHP")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
