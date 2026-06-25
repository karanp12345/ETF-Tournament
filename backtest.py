"""
Daily-rebalancing backtest engine.

Each day:
  1. Identify top-N ETFs from yesterday's tournament scores.
  2. Allocate capital equally across all top-N ETFs that have a valid price.
  3. Compute next-day portfolio return (close-to-close, zero commission —
     Wealthsimple has no trading commissions).
  4. Track equity curve and record holdings.

Assumptions:
  - Execution at next day's open is approximated by the next day's close
    (conservative; avoids look-ahead bias within the same session).
  - No slippage, no bid/ask spread.
  - Dividends are captured in adjusted close prices (yfinance auto_adjust=True).
"""

import numpy as np
import pandas as pd

from config import INITIAL_CAPITAL, TOP_N_VALUES, BENCHMARK, BACKTEST_START
from tournament import compute_rankings, get_daily_top_n


def run_backtest(prices: pd.DataFrame) -> dict:
    """
    Run the full backtest for all TOP_N_VALUES strategies and the benchmark.
    Returns a dict with equity curves and performance metrics.
    """
    scores = compute_rankings(prices)
    daily_returns = prices.pct_change()

    results: dict = {}

    for n in TOP_N_VALUES:
        top_mask = get_daily_top_n(scores, n)  # bool DataFrame

        # Portfolio daily return = equal-weight average of top-N ETF returns
        # Shift top_mask by 1: signals from day t → invest on day t+1
        shifted_mask = top_mask.shift(1)
        portfolio_returns = (
            daily_returns[shifted_mask]
            .mean(axis=1)
            .fillna(0)
        )

        equity = (1 + portfolio_returns).cumprod() * INITIAL_CAPITAL
        equity.name = f"Top {n}"
        results[f"top_{n}"] = {
            "equity": equity,
            "returns": portfolio_returns,
        }

    # Benchmark
    if BENCHMARK in prices.columns:
        bm_ret = prices[BENCHMARK].pct_change().fillna(0)
        bm_equity = (1 + bm_ret).cumprod() * INITIAL_CAPITAL
        bm_equity.name = BENCHMARK
        results["benchmark"] = {"equity": bm_equity, "returns": bm_ret}

    return results


def compute_metrics(equity: pd.Series, returns: pd.Series) -> dict:
    """Compute annualised performance metrics for one strategy."""
    total_days = len(returns)
    years = total_days / 252

    total_return = (equity.iloc[-1] / INITIAL_CAPITAL - 1) * 100
    cagr = ((equity.iloc[-1] / INITIAL_CAPITAL) ** (1 / max(years, 1e-9)) - 1) * 100

    # Sharpe (annualised, risk-free rate ≈ 0 for simplicity)
    daily_std = returns.std()
    sharpe = (returns.mean() / daily_std * np.sqrt(252)) if daily_std > 0 else 0.0

    # Maximum drawdown
    rolling_max = equity.cummax()
    drawdown = (equity - rolling_max) / rolling_max
    max_dd = drawdown.min() * 100

    # Win rate
    win_rate = (returns > 0).sum() / max((returns != 0).sum(), 1) * 100

    return {
        "total_return": round(total_return, 2),
        "cagr": round(cagr, 2),
        "sharpe": round(sharpe, 3),
        "max_drawdown": round(max_dd, 2),
        "win_rate": round(win_rate, 2),
    }


def build_summary(backtest_results: dict) -> list[dict]:
    """Return metrics for all strategies as a list of dicts for the API."""
    rows = []
    for key, data in backtest_results.items():
        m = compute_metrics(data["equity"], data["returns"])
        label = data["equity"].name
        rows.append({"strategy": label, **m})
    return sorted(rows, key=lambda r: r["cagr"], reverse=True)


def equity_to_json(backtest_results: dict) -> dict:
    """
    Serialise equity curves to {strategy: {dates: [...], values: [...]}}
    for Plotly in the frontend.
    """
    out = {}
    for key, data in backtest_results.items():
        eq = data["equity"].dropna()
        out[key] = {
            "name": data["equity"].name,
            "dates": eq.index.strftime("%Y-%m-%d").tolist(),
            "values": [round(v, 2) for v in eq.values.tolist()],
        }
    return out
