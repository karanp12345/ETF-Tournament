"""
Round-robin tournament ranking.

For each trading day:
  - For each lookback window L in LOOKBACK_WINDOWS, compute each ETF's L-day return.
  - An ETF scores 1 win for every other ETF it beats on that window.
  - Composite score = sum of wins across all windows.
  - Rank ETFs descending by composite score.

Because wins(i) = rank_position(i) - 1 for a single metric, the round-robin
is mathematically equivalent to ranking by return for a single window.
The multi-window composite adds meaningful signal when windows disagree.
"""

import numpy as np
import pandas as pd

from config import LOOKBACK_WINDOWS


def compute_rankings(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame of composite tournament scores with the same
    index as `prices` and one column per ETF.
    Higher score → stronger uptrend relative to peers.
    """
    max_window = max(LOOKBACK_WINDOWS)
    scores = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)

    for window in LOOKBACK_WINDOWS:
        # L-day return: price today / price L days ago − 1
        returns = prices / prices.shift(window) - 1
        # For each row, rank non-NaN columns (higher return = more wins)
        # rank() with method='average' gives ties equal weight
        wins = returns.rank(axis=1, method="average", na_option="keep")
        # Normalise so each window contributes equally regardless of universe size
        valid_counts = wins.notna().sum(axis=1)
        wins = wins.div(valid_counts, axis=0)
        scores += wins.fillna(0)

    # Zero out rows before we have enough history
    scores.iloc[:max_window] = np.nan
    return scores


def get_daily_top_n(scores: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    Return a boolean DataFrame (same shape as scores) where True means
    this ETF is in the top-n on that day.
    """
    ranks = scores.rank(axis=1, ascending=False, method="first", na_option="keep")
    return ranks <= n


def get_current_rankings(scores: pd.DataFrame, prices: pd.DataFrame, top_n: int = 20) -> list[dict]:
    """
    Return today's top_n ETFs as a list of dicts for the API.
    """
    last_scores = scores.iloc[-1].dropna().sort_values(ascending=False)
    top = last_scores.head(top_n)

    result = []
    for rank, (ticker, score) in enumerate(top.items(), 1):
        row: dict = {"rank": rank, "ticker": ticker, "score": round(score, 4)}
        # Add return metrics for display
        for label, window in [("ret_20d", 20), ("ret_60d", 60), ("ret_120d", 120)]:
            try:
                p_now = prices[ticker].iloc[-1]
                p_then = prices[ticker].iloc[-window - 1]
                row[label] = round((p_now / p_then - 1) * 100, 2)
            except Exception:
                row[label] = None
        result.append(row)
    return result
