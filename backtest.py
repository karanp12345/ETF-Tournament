"""
Daily-rebalancing backtest engine — runs both original and improved strategies.

Original:  raw momentum, windows [10,20,40,60,120], rebalance every day
Improved:  vol-adjusted momentum, windows [60,120,252], rebalance every 5 days

Assumptions:
  - Execution at next-day close (shift(1) on signals avoids look-ahead bias).
  - Zero commission (Wealthsimple), no slippage.
  - Dividends captured via yfinance auto_adjust=True.
"""
from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from config import INITIAL_CAPITAL, TOP_N_VALUES, BENCHMARK, MIN_HOLDING_DAYS
from tournament import (
    compute_rankings,
    compute_rankings_improved,
    get_daily_top_n,
    apply_min_holding,
)


def _portfolio_equity(prices: pd.DataFrame, top_mask: pd.DataFrame) -> tuple:
    daily_returns = prices.pct_change(fill_method=None)
    shifted = top_mask.shift(1)
    port_ret = daily_returns[shifted].mean(axis=1).fillna(0)
    equity = (1 + port_ret).cumprod() * INITIAL_CAPITAL
    return equity, port_ret


def run_backtest(prices: pd.DataFrame) -> Dict:
    results: Dict = {}

    # ── Original strategies ───────────────────────────────────────────────────
    scores_orig = compute_rankings(prices)
    for n in TOP_N_VALUES:
        mask = get_daily_top_n(scores_orig, n)
        equity, ret = _portfolio_equity(prices, mask)
        equity.name = f"Top {n}"
        results[f"top_{n}"] = {"equity": equity, "returns": ret}

    # ── Improved strategies ───────────────────────────────────────────────────
    scores_imp = compute_rankings_improved(prices)
    for n in TOP_N_VALUES:
        raw_mask = get_daily_top_n(scores_imp, n)
        held_mask = apply_min_holding(raw_mask, min_holding_days=MIN_HOLDING_DAYS)
        equity, ret = _portfolio_equity(prices, held_mask)
        equity.name = f"Top {n} (Improved)"
        results[f"top_{n}_improved"] = {"equity": equity, "returns": ret}

    # ── Benchmark ─────────────────────────────────────────────────────────────
    if BENCHMARK in prices.columns:
        bm_ret = prices[BENCHMARK].pct_change(fill_method=None).fillna(0)
        bm_equity = (1 + bm_ret).cumprod() * INITIAL_CAPITAL
        bm_equity.name = BENCHMARK
        results["benchmark"] = {"equity": bm_equity, "returns": bm_ret}

    return results


def compute_metrics(equity: pd.Series, returns: pd.Series) -> dict:
    years = len(returns) / 252
    total_return = (equity.iloc[-1] / INITIAL_CAPITAL - 1) * 100
    cagr = ((equity.iloc[-1] / INITIAL_CAPITAL) ** (1 / max(years, 1e-9)) - 1) * 100
    daily_std = returns.std()
    sharpe = (returns.mean() / daily_std * np.sqrt(252)) if daily_std > 0 else 0.0
    rolling_max = equity.cummax()
    max_dd = ((equity - rolling_max) / rolling_max).min() * 100
    win_rate = (returns > 0).sum() / max((returns != 0).sum(), 1) * 100
    return {
        "total_return": round(total_return, 2),
        "cagr": round(cagr, 2),
        "sharpe": round(sharpe, 3),
        "max_drawdown": round(max_dd, 2),
        "win_rate": round(win_rate, 2),
    }


def build_summary(backtest_results: Dict) -> list:
    rows = []
    for key, data in backtest_results.items():
        m = compute_metrics(data["equity"], data["returns"])
        rows.append({"strategy": data["equity"].name, "key": key, **m})
    return sorted(rows, key=lambda r: r["cagr"], reverse=True)


def equity_to_json(backtest_results: Dict) -> dict:
    out = {}
    for key, data in backtest_results.items():
        eq = data["equity"].dropna()
        out[key] = {
            "name": data["equity"].name,
            "dates": eq.index.strftime("%Y-%m-%d").tolist(),
            "values": [round(v, 2) for v in eq.values.tolist()],
            "improved": "improved" in key,
        }
    return out
