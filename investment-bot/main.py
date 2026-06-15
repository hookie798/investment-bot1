#!/usr/bin/env python3
"""
investment-bot — Level 4 Automated Investment Decision System

Runs daily, fetches NASDAQ data, evaluates portfolio allocation rules,
and pushes an investment signal via mock WeChat.

Usage:
    python main.py                     # single run
    python main.py --dry-run           # print decision without logging to file
"""

import json
import os
import sys
from datetime import datetime

from data_fetcher import fetch_nasdaq_data, fetch_bond_data
from strategy import DCA_AMOUNT_RMB, evaluate
from wechat import send_wechat_message


# ── Portfolio state file ───────────────────────────────────────────────────
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portfolio_state.json")

DEFAULT_STATE = {
    "nasdaq_value_rmb": 50000.0,   # default seed values
    "bond_value_rmb": 30000.0,
    "last_updated": "",
}


def load_portfolio() -> dict:
    """Load portfolio state from JSON; create with defaults if missing."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            # Ensure required keys exist
            for key, default in DEFAULT_STATE.items():
                state.setdefault(key, default)
            return state
        except (json.JSONDecodeError, IOError):
            print("[WARN] Corrupted state file — using defaults.")
    return dict(DEFAULT_STATE)


def save_portfolio(state: dict) -> None:
    """Persist portfolio state to JSON."""
    state["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def run(dry_run: bool = False) -> int:
    """
    Execute one daily investment-decision cycle.

    Returns 0 on success, 1 on failure.
    """
    print("=" * 55)
    print("  ??  investment-bot — Daily Investment Signal")
    print("=" * 55)

    # ── Step 1: Fetch market data ───────────────────────────────────────
    print("\n[1/4] Fetching NASDAQ market data ...")
    nasdaq = fetch_nasdaq_data()
    if nasdaq is None:
        error_msg = "?? Failed to fetch NASDAQ data. Aborting."
        print(error_msg)
        if not dry_run:
            send_wechat_message(error_msg)
        return 1

    print(f"      QQQ @ ${nasdaq['current_price']:,.2f}  |  "
          f"Drawdown: {nasdaq['drawdown_pct']}%  |  "
          f"YTD: {nasdaq['ytd_return_pct']}%")

    bond = fetch_bond_data()

    # ── Step 2: Load portfolio state ────────────────────────────────────
    print("\n[2/4] Loading portfolio state ...")
    portfolio = load_portfolio()
    nasdaq_val = portfolio["nasdaq_value_rmb"]
    bond_val = portfolio["bond_value_rmb"]
    print(f"      NASDAQ: ??{nasdaq_val:,.0f}  |  Bonds: ??{bond_val:,.0f}  |  "
          f"Total: ??{nasdaq_val + bond_val:,.0f}")

    # ── Step 3: Evaluate strategy ───────────────────────────────────────
    print("\n[3/4] Evaluating investment decision ...")
    decision = evaluate(
        nasdaq_price=nasdaq["current_price"],
        nasdaq_drawdown_pct=nasdaq["drawdown_pct"],
        nasdaq_current_value=nasdaq_val,
        bond_current_value=bond_val,
        ytd_return_pct=nasdaq["ytd_return_pct"],
        extra={
            "ath_price": nasdaq["ath_price"],
            "ath_date": nasdaq["ath_date"],
            "bond_price": bond["current_price"] if bond else None,
        },
    )

    print(f"      Action: {decision.action}  |  DCA: ??{decision.dca_amount_rmb}")

    # ── Update portfolio (simulate DCA execution) ───────────────────────
    if not dry_run:
        portfolio["nasdaq_value_rmb"] = round(nasdaq_val + DCA_AMOUNT_RMB, 2)
        save_portfolio(portfolio)
        print(f"      Portfolio updated: NASDAQ ??{portfolio['nasdaq_value_rmb']:,.0f}")

    # ── Step 4: Push signal ─────────────────────────────────────────────
    print("\n[4/4] Pushing investment signal ...")
    if not dry_run:
        send_wechat_message(decision.message)
    else:
        print(decision.message)

    print("\n?? Done.\n")
    return 0


# ── CLI Entrypoint ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    sys.exit(run(dry_run=dry))
