import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BACKTEST_START = "2018-01-01"
BACKTEST_END = None  # None = today
INITIAL_CAPITAL = 10_000.0  # USD
LOOKBACK_WINDOWS = [10, 20, 40, 60, 120]   # original strategy windows
IMPROVED_WINDOWS = [60, 120]               # noise-free windows (avoid 252-day warmup cost)
MIN_HOLDING_DAYS = 5                        # minimum days before rebalancing
VOL_SCREEN_THRESHOLD = 0.018               # exclude ETFs with 20-day daily vol > 1.8% (~28% ann.)
TREND_FILTER_WINDOW = 200                  # only hold ETFs trading above their 200-day MA
TOP_N_VALUES = [1, 2, 3, 4, 5]
BENCHMARK = "SPY"
CACHE_DIR = os.path.join(BASE_DIR, "cache")
MIN_HISTORY_DAYS = 252  # ETF must have >= 1 year of data to enter tournament
BATCH_SIZE = 50          # tickers per yfinance download call (rate-limit safety)
PORT = 3002

# yfinance ticker for USD per 1 CAD (used to convert Canadian ETF prices → USD)
CADUSD_TICKER = "CADUSD=X"
