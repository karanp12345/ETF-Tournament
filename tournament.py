"""
Round-robin tournament ranking — two variants:

Original:  raw L-day returns, windows [10, 20, 40, 60, 120]
Improved:  volatility-adjusted (Sharpe-like) returns, windows [60, 120, 252]
           + 5-day minimum holding period applied in backtest.py

Volatility adjustment: score = L-day_return / rolling_std(L days)
This penalises ETFs that spike violently (commodities, leveraged thematic)
and rewards ones with smooth, persistent uptrends.
"""
from __future__ import annotations

from typing import List, Dict

import numpy as np
import pandas as pd

from config import LOOKBACK_WINDOWS, IMPROVED_WINDOWS, VOL_SCREEN_THRESHOLD, TREND_FILTER_WINDOW


def _rank_scores(raw_scores: pd.DataFrame, max_window: int) -> pd.DataFrame:
    """Normalise and combine raw per-window scores into a composite."""
    scores = pd.DataFrame(0.0, index=raw_scores.index, columns=raw_scores.columns)
    # raw_scores already has scores summed; just NaN the warmup rows
    scores = raw_scores.copy()
    scores.iloc[:max_window] = np.nan
    return scores


def compute_rankings(prices: pd.DataFrame) -> pd.DataFrame:
    """Original tournament: raw momentum, short + long windows."""
    max_window = max(LOOKBACK_WINDOWS)
    scores = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)

    for window in LOOKBACK_WINDOWS:
        returns = prices / prices.shift(window) - 1
        wins = returns.rank(axis=1, method="average", na_option="keep")
        valid_counts = wins.notna().sum(axis=1)
        wins = wins.div(valid_counts, axis=0)
        scores += wins.fillna(0)

    scores.iloc[:max_window] = np.nan
    return scores


def compute_rankings_improved(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Improved tournament: raw momentum on longer windows, plus two filters:

    1. Volatility screen  — exclude any ETF whose 20-day daily return std
       exceeds VOL_SCREEN_THRESHOLD (≈28% annualised). This removes commodity
       ETFs (UNG, USO, SLV) and volatile thematic ETFs (ARKK, TAN, REMX) that
       spike into #1 on the raw tournament and then crash.

    2. Trend filter — exclude any ETF trading below its TREND_FILTER_WINDOW-day
       moving average. Ensures we only hold assets in confirmed uptrends, not
       dead-cat bounces.

    3. Minimum holding period (applied in backtest.py via apply_min_holding).
    """
    daily_ret = prices.pct_change(fill_method=None)
    warmup = max(max(IMPROVED_WINDOWS), TREND_FILTER_WINDOW)
    scores = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)

    for window in IMPROVED_WINDOWS:
        returns = prices / prices.shift(window) - 1
        wins = returns.rank(axis=1, method="average", na_option="keep")
        valid_counts = wins.notna().sum(axis=1)
        wins = wins.div(valid_counts, axis=0)
        scores += wins.fillna(0)

    # ── Filter 1: volatility screen ───────────────────────────────────────────
    rolling_vol_20 = daily_ret.rolling(20).std()
    too_volatile = rolling_vol_20 > VOL_SCREEN_THRESHOLD
    scores = scores.where(~too_volatile, other=np.nan)

    # ── Filter 2: trend filter (must be above 200-day MA) ────────────────────
    ma = prices.rolling(TREND_FILTER_WINDOW).mean()
    below_trend = prices < ma
    scores = scores.where(~below_trend, other=np.nan)

    scores.iloc[:warmup] = np.nan
    return scores


def get_daily_top_n(scores: pd.DataFrame, n: int) -> pd.DataFrame:
    """Boolean DataFrame: True where ETF is in top-n that day."""
    ranks = scores.rank(axis=1, ascending=False, method="first", na_option="keep")
    return ranks <= n


def apply_min_holding(mask: pd.DataFrame, min_holding_days: int = 5) -> pd.DataFrame:
    """
    Enforce a minimum holding period: only rebalance every min_holding_days.
    Rebalances are aligned to every N-th trading day from the start.
    """
    result = mask.copy()
    last_row = mask.iloc[0].copy()

    for i in range(len(mask)):
        if i % min_holding_days == 0:
            last_row = mask.iloc[i].copy()
        result.iloc[i] = last_row

    return result


def get_current_rankings(scores: pd.DataFrame, prices: pd.DataFrame, top_n: int = 20) -> List[Dict]:
    """Return today's top_n ETFs as a list of dicts for the API."""
    last_scores = scores.iloc[-1].dropna().sort_values(ascending=False)
    top = last_scores.head(top_n)

    result = []
    for rank, (ticker, score) in enumerate(top.items(), 1):
        row: Dict = {"rank": rank, "ticker": ticker, "score": round(score, 4)}
        for label, window in [("ret_20d", 20), ("ret_60d", 60), ("ret_120d", 120)]:
            try:
                p_now = prices[ticker].iloc[-1]
                p_then = prices[ticker].iloc[-window - 1]
                row[label] = round((p_now / p_then - 1) * 100, 2)
            except Exception:
                row[label] = None
        result.append(row)
    return result
