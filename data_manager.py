"""
Downloads and caches historical adjusted-close prices via yfinance.
Canadian ETF prices are converted to USD using the CAD/USD FX rate.
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf
from tqdm import tqdm

from config import CACHE_DIR, BATCH_SIZE, CADUSD_TICKER, MIN_HISTORY_DAYS, BACKTEST_START
from universe import get_all_etfs, is_canadian

logger = logging.getLogger(__name__)
os.makedirs(CACHE_DIR, exist_ok=True)

PRICES_FILE = os.path.join(CACHE_DIR, "prices.parquet")
META_FILE = os.path.join(CACHE_DIR, "meta.json")
CACHE_TTL_HOURS = 12


def _cache_is_fresh() -> bool:
    if not os.path.exists(META_FILE) or not os.path.exists(PRICES_FILE):
        return False
    with open(META_FILE) as f:
        meta = json.load(f)
    fetched = datetime.fromisoformat(meta.get("fetched_at", "2000-01-01"))
    return datetime.utcnow() - fetched < timedelta(hours=CACHE_TTL_HOURS)


def _download_batch(tickers: list[str], start: str, end: str | None) -> pd.DataFrame:
    """Download a batch of tickers; return Close prices DataFrame."""
    kwargs = dict(start=start, auto_adjust=True, progress=False, threads=True)
    if end:
        kwargs["end"] = end
    for attempt in range(3):
        try:
            raw = yf.download(tickers, **kwargs)
            if raw.empty:
                return pd.DataFrame()
            # yf returns MultiIndex when >1 ticker
            if isinstance(raw.columns, pd.MultiIndex):
                close = raw["Close"]
            else:
                close = raw[["Close"]].rename(columns={"Close": tickers[0]})
            return close
        except Exception as exc:
            logger.warning(f"Batch download attempt {attempt+1} failed: {exc}")
            time.sleep(2 ** attempt)
    return pd.DataFrame()


def fetch_prices(
    start: str = BACKTEST_START,
    end: str | None = None,
    progress_callback=None,
) -> pd.DataFrame:
    """
    Return a DataFrame of daily USD-adjusted close prices indexed by date,
    one column per ETF.  Loads from cache when fresh.
    """
    if _cache_is_fresh():
        logger.info("Loading prices from cache.")
        return pd.read_parquet(PRICES_FILE)

    tickers = get_all_etfs()
    all_frames: list[pd.DataFrame] = []
    batches = [tickers[i : i + BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]

    # Download CAD/USD FX rate first (needed for currency conversion)
    logger.info("Downloading CAD/USD FX rate…")
    fx_raw = _download_batch([CADUSD_TICKER], start, end)
    cadusd: pd.Series | None = None
    if not fx_raw.empty:
        col = CADUSD_TICKER if CADUSD_TICKER in fx_raw.columns else fx_raw.columns[0]
        cadusd = fx_raw[col].ffill().bfill()

    logger.info(f"Downloading {len(tickers)} ETFs in {len(batches)} batches…")
    for i, batch in enumerate(tqdm(batches, desc="Downloading ETFs")):
        frame = _download_batch(batch, start, end)
        if not frame.empty:
            all_frames.append(frame)
        if progress_callback:
            progress_callback(int((i + 1) / len(batches) * 90))
        time.sleep(0.3)  # gentle rate limiting

    if not all_frames:
        raise RuntimeError("No price data downloaded.")

    prices = pd.concat(all_frames, axis=1)
    prices = prices.loc[:, ~prices.columns.duplicated()]
    prices.sort_index(inplace=True)

    # Convert Canadian ETF prices from CAD → USD
    if cadusd is not None:
        cadusd = cadusd.reindex(prices.index).ffill().bfill()
        ca_cols = [c for c in prices.columns if is_canadian(c)]
        if ca_cols:
            prices[ca_cols] = prices[ca_cols].multiply(cadusd, axis=0)

    # Drop columns with fewer than MIN_HISTORY_DAYS of non-NaN data
    prices = prices.loc[:, prices.notna().sum() >= MIN_HISTORY_DAYS]

    prices.to_parquet(PRICES_FILE)
    with open(META_FILE, "w") as f:
        json.dump({"fetched_at": datetime.utcnow().isoformat(), "n_etfs": prices.shape[1]}, f)

    logger.info(f"Saved {prices.shape[1]} ETFs × {prices.shape[0]} days to cache.")
    if progress_callback:
        progress_callback(100)
    return prices
