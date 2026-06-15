"""
Strategy module — portfolio allocation and daily investment decision engine.

Rules (Level 4):
    • NASDAQ DCA = 100 RMB / day — never stops
    • If NASDAQ allocation > 70% → recommend increasing bonds
    • If drawdown > 20%        → continue DCA only (no extra)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ── Constants ──────────────────────────────────────────────────────────────
DCA_AMOUNT_RMB = 100                      # Fixed daily DCA in RMB
ALLOCATION_THRESHOLD = 0.70               # 70 % NASDAQ → rebalance warning
DRAWDOWN_THRESHOLD = -0.20                # -20 % drawdown → defensive


@dataclass
class Decision:
    """Single daily investment decision."""
    date: str
    dca_amount_rmb: float = DCA_AMOUNT_RMB
    action: str = "DCA_BUY"               # DCA_BUY | DCA_ONLY | REBALANCE_WARN
    nasdaq_price: float = 0.0
    nasdaq_drawdown_pct: float = 0.0
    nasdaq_allocation_pct: float = 0.0
    message: str = ""
    extra_details: dict = field(default_factory=dict)


def evaluate(
    *,
    nasdaq_price: float,
    nasdaq_drawdown_pct: float,
    nasdaq_current_value: float,
    bond_current_value: float,
    ytd_return_pct: Optional[float] = None,
    extra: Optional[dict] = None,
) -> Decision:
    """
    Evaluate the daily investment decision given current portfolio state.

    Parameters
    ----------
    nasdaq_price          : Current NASDAQ proxy price (QQQ).
    nasdaq_drawdown_pct   : Drawdown from ATH (negative number, e.g. -15.2).
    nasdaq_current_value  : Current value held in NASDAQ assets (RMB).
    bond_current_value    : Current value held in bond assets (RMB).
    ytd_return_pct        : Optional YTD return for context.
    extra                 : Optional extra metadata to attach.

    Returns
    -------
    Decision dataclass.
    """
    total_value = nasdaq_current_value + bond_current_value
    nasdaq_allocation = (nasdaq_current_value / total_value) if total_value > 0 else 0.0
    nasdaq_allocation_pct = round(nasdaq_allocation * 100, 1)

    # ── Rule 1: Never stop DCA ─────────────────────────────────────────
    dca_amount = DCA_AMOUNT_RMB
    signals = []

    # ── Rule 2: Drawdown > 20% → DCA only ──────────────────────────────
    if nasdaq_drawdown_pct <= DRAWDOWN_THRESHOLD * 100:
        action = "DCA_ONLY"
        signals.append(
            f"?? Drawdown {nasdaq_drawdown_pct}% exceeds {DRAWDOWN_THRESHOLD*100:.0f}% threshold."
            f" Continue DCA only — no additional equity exposure."
        )
    # ── Rule 3: NASDAQ allocation > 70% → recommend bonds ──────────────
    elif nasdaq_allocation > ALLOCATION_THRESHOLD:
        action = "REBALANCE_WARN"
        signals.append(
            f"?? NASDAQ allocation {nasdaq_allocation_pct}% exceeds {ALLOCATION_THRESHOLD*100:.0f}%."
            f" Recommend increasing bond allocation to rebalance."
        )
    else:
        action = "DCA_BUY"
        signals.append(
            f"? Normal conditions. Continue DCA ??{DCA_AMOUNT_RMB} RMB into NASDAQ."
        )

    # ── Build message ───────────────────────────────────────────────────
    message = (
        f"?? Daily Investment Signal | {datetime.now().strftime('%Y-%m-%d')}\n"
        f"{'='*50}\n"
        f"?? NASDAQ Price (QQQ)    : ${nasdaq_price:,.2f}\n"
        f"?? Drawdown from ATH     : {nasdaq_drawdown_pct}%\n"
        f"?? NASDAQ Allocation     : {nasdaq_allocation_pct}%\n"
        f"?? YTD Return            : {ytd_return_pct if ytd_return_pct is not None else 'N/A'}%\n"
        f"{'─'*50}\n"
        f"?? Action                : {action}\n"
        f"?? Daily DCA             : ??{dca_amount} RMB\n"
        f"⚠  {''.join(signals)}\n"
        f"{'='*50}\n"
    )

    return Decision(
        date=datetime.now().strftime("%Y-%m-%d"),
        dca_amount_rmb=dca_amount,
        action=action,
        nasdaq_price=nasdaq_price,
        nasdaq_drawdown_pct=nasdaq_drawdown_pct,
        nasdaq_allocation_pct=nasdaq_allocation_pct,
        message=message,
        extra_details=extra or {},
    )


# ── Quick test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Simulate a moderate-drawdown scenario
    d = evaluate(
        nasdaq_price=420.0,
        nasdaq_drawdown_pct=-15.0,
        nasdaq_current_value=50000,
        bond_current_value=30000,
        ytd_return_pct=8.5,
    )
    print(d.message)
