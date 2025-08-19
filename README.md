# PHP/JPY ARIMA Forecast (Monthly)

This project downloads PHP/JPY exchange rate data from Yahoo Finance, aggregates to monthly averages, fits an ARIMA model (via `statsmodels`), and exports a 12‑month forecast.

## How to run
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python fetch_data.py
    python analyze_fx_step1.py      # quick plot
    python analyze_fx_step2.py      # model + forecast chart
    python analyze_fx_export.py     # saves outputs

## Project structure
    data/                 # downloaded CSVs
    output/               # forecast_12m.csv, residuals.csv, model_summary.txt, forecast_12m.png
    fetch_data.py
    analyze_fx_step1.py
    analyze_fx_step2.py
    analyze_fx_export.py
    README.md
    requirements.txt

## Notes
- The pipeline picked ARIMA(1,1,0) by AIC on log‑levels.
- Forecasts are shown in levels (JPY per PHP). Bands are model prediction intervals.
 # add a newline
