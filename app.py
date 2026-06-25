"""
Flask web server — serves the dashboard at http://localhost:3002
and provides JSON API endpoints consumed by the frontend.

Computation (data download + tournament + backtest) runs in a background
thread on first request so the browser gets an immediate response with a
loading screen while numbers crunch.
"""

import json
import logging
import threading

from flask import Flask, jsonify, render_template, request

from config import PORT, BACKTEST_START, TOP_N_VALUES, BENCHMARK
from data_manager import fetch_prices
from tournament import compute_rankings, get_current_rankings
from backtest import run_backtest, build_summary, equity_to_json

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ── Shared computation state ──────────────────────────────────────────────────

_state = {
    "status": "idle",       # idle | loading | ready | error
    "progress": 0,
    "message": "",
    "rankings": [],
    "metrics": [],
    "equity_json": {},
    "n_etfs": 0,
    "last_updated": "",
}
_lock = threading.Lock()


def _set(key, value):
    with _lock:
        _state[key] = value


def _progress(pct: int, msg: str = ""):
    with _lock:
        _state["progress"] = pct
        if msg:
            _state["message"] = msg


def _run_computation():
    from datetime import datetime
    _set("status", "loading")
    _progress(0, "Downloading price data for all ETFs…")
    try:
        prices = fetch_prices(progress_callback=lambda p: _progress(p, "Downloading price data…"))

        _progress(92, "Running round-robin tournament…")
        scores = compute_rankings(prices)
        rankings = get_current_rankings(scores, prices, top_n=30)

        _progress(95, "Running daily-rebalancing backtest…")
        backtest_res = run_backtest(prices)

        metrics = build_summary(backtest_res)
        equity_json = equity_to_json(backtest_res)

        with _lock:
            _state["rankings"] = rankings
            _state["metrics"] = metrics
            _state["equity_json"] = equity_json
            _state["n_etfs"] = prices.shape[1]
            _state["last_updated"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            _state["progress"] = 100
            _state["message"] = "Done"
            _state["status"] = "ready"

        logger.info("Computation complete.")
    except Exception as exc:
        logger.exception("Computation failed")
        with _lock:
            _state["status"] = "error"
            _state["message"] = str(exc)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html",
                           top_n_values=TOP_N_VALUES,
                           benchmark=BENCHMARK,
                           backtest_start=BACKTEST_START)


@app.route("/api/status")
def api_status():
    with _lock:
        return jsonify({k: _state[k] for k in ("status", "progress", "message",
                                                "n_etfs", "last_updated")})


@app.route("/api/rankings")
def api_rankings():
    with _lock:
        return jsonify(_state["rankings"])


@app.route("/api/metrics")
def api_metrics():
    with _lock:
        return jsonify(_state["metrics"])


@app.route("/api/equity")
def api_equity():
    with _lock:
        return jsonify(_state["equity_json"])


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """Force a data refresh (clears cache and reruns)."""
    import os
    from config import CACHE_DIR
    meta = os.path.join(CACHE_DIR, "meta.json")
    if os.path.exists(meta):
        os.remove(meta)
    if _state["status"] not in ("loading",):
        _set("status", "idle")
        t = threading.Thread(target=_run_computation, daemon=True)
        t.start()
    return jsonify({"ok": True})


# ── Boot ──────────────────────────────────────────────────────────────────────

def start_background():
    t = threading.Thread(target=_run_computation, daemon=True)
    t.start()


if __name__ == "__main__":
    start_background()
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
