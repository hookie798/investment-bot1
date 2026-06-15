"""
Data fetcher module — fetches NASDAQ market data using yfinance.
Uses QQQ (Invesco QQQ Trust) as the NASDAQ proxy ETF.
No paid API keys required.
"""

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf


# ── Configuration ──────────────────────────────────────────────────────────
NASDAQ_TICKER = "QQQ"            # NASDAQ-100 proxy ETF
LOOKBACK_DAYS = 365 * 3          # 3 years for drawdown calculation
RISK_FREE_TICKER = "BND"         # Aggregate bond ETF (for allocation context)


def fetch_nasdaq_data() -> Optional[dict]:
    """
    Fetch current NASDAQ data via yfinance.

    Returns dict with keys:
        ticker, current_price, previous_close, change_pct,
        drawdown_pct, ath_price, ath_date, fetch_time
    Returns None on failure.
    """
    try:
        qqq = yf.Ticker(NASDAQ_TICKER)
        end = datetime.now()
        start = end - timedelta(days=LOOKBACK_DAYS)

        hist = qqq.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
        if hist.empty:
            print("[ERROR] NASDAQ history is empty — ticker may be delisted or network issue.")
            return None

        close_prices = hist["Close"]

        current_price = round(float(close_prices.iloc[-1]), 2)
        previous_close = round(float(close_prices.iloc[-2]), 2) if len(close_prices) >= 2 else current_price
        change_pct = round((current_price - previous_close) / previous_close * 100, 2)

        # ATH and drawdown
        ath_price = round(float(close_prices.max()), 2)
        ath_idx = close_prices.idxmax()
        ath_date = ath_idx.strftime("%Y-%m-%d") if hasattr(ath_idx, "strftime") else str(ath_idx)[:10]
        drawdown_pct = round((current_price - ath_price) / ath_price * 100, 2)

        # YTD return
        ytd_start = datetime(end.year, 1, 1)
        ytd_data = close_prices[close_prices.index >= ytd_start]
        ytd_return = None
        if not ytd_data.empty:
            ytd_return = round((current_price - float(ytd_data.iloc[0])) / float(ytd_data.iloc[0]) * 100, 2)

        return {
            "ticker": NASDAQ_TICKER,
            "current_price": current_price,
            "previous_close": previous_close,
            "change_pct": change_pct,
            "drawdown_pct": drawdown_pct,
            "ath_price": ath_price,
            "ath_date": ath_date,
            "ytd_return_pct": ytd_return,
            "fetch_time": end.strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception as exc:
        print(f"[ERROR] Failed to fetch NASDAQ data: {exc}")
        return None


def fetch_bond_data() -> Optional[dict]:
    """Fetch bond ETF data for allocation context."""
    try:
        bnd = yf.Ticker(RISK_FREE_TICKER)
        end = datetime.now()
        start = end - timedelta(days=90)

        hist = bnd.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
        if hist.empty:
            return None

        current = round(float(hist["Close"].iloc[-1]), 2)
        return {"ticker": RISK_FREE_TICKER, "current_price": current}
    except Exception as exc:
        print(f"[WARN] Bond data fetch failed: {exc}")
        return None


# ── Quick test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    data = fetch_nasdaq_data()
    if data:
        for k, v in data.items():
            print(f"  {k}: {v}")
    else:
        print("Failed to fetch NASDAQ data.")
