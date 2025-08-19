# PHP/JPY ARIMA Forecast (Monthly)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Statsmodels](https://img.shields.io/badge/statsmodels-ARIMA-orange.svg)](https://www.statsmodels.org/)

## 📑 Table of Contents
1. Overview
2. How to Run
3. Project Structure
4. Forecast Preview
5. Notes

## Overview
This project downloads PHP/JPY exchange rate data from Yahoo Finance, aggregates it to monthly averages, fits an ARIMA model (via statsmodels), and exports a 12‑month forecast.

## How to Run
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python fetch_data.py
    python analyze_fx_step1.py      # quick plot
    python analyze_fx_step2.py      # model + forecast chart
    python analyze_fx_export.py     # saves outputs

## Project Structure
    data/                 # downloaded CSVs
    output/               # forecast_12m.csv, residuals.csv, model_summary.txt
    assets/forecast_12m.png
    fetch_data.py
    analyze_fx_step1.py
    analyze_fx_step2.py
    analyze_fx_export.py
    README.md
    requirements.txt
    LICENSE

## Forecast Preview
![Forecast Chart](assets/forecast_12m.png)

## Notes
- The pipeline picked ARIMA(1,1,0) by AIC on log‑levels.
- Forecasts are shown in levels (JPY per PHP). Bands are model prediction intervals.
