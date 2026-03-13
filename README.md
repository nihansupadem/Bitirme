---
title: OpTrade Pro — BIST30 AI Forecasting
emoji: 🚀
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: LSTM + HMM + Monte Carlo stock forecasting for BIST30
---

# OpTrade Pro — BIST30 AI Stock Forecasting

AI-powered forecasting tool for Istanbul Stock Exchange (BIST30) stocks, combining:
- **LSTM** neural network for price prediction
- **Hidden Markov Model (HMM)** for market regime detection
- **Monte Carlo simulation** for volatility features
- **Technical indicators** (RSI, EMA, Log Returns)

## Features
- Real-time data from Borsa Istanbul + Yahoo Finance (with 12-hour cache)
- 80/20 train/test split — honest out-of-sample metrics
- BUY / SELL / HOLD signal with strength score
- Key trading levels: Entry Zone, Price Target, Stop Loss
- Plain-English explanations for beginners
- 3 interactive charts with dark theme
- User accounts with tracked stock alerts

## ⚠️ Disclaimer
This is an educational AI research tool — **not financial advice**.
Predictions can be wrong. Always do your own research and consult a
licensed financial adviser before investing real money.

## Tech Stack
Python · TensorFlow · hmmlearn · yfinance · curl_cffi · PHP 8.1 · Apache · SQLite · matplotlib · scikit-learn
