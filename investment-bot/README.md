# ?? investment-bot

**Level 4 Automated Investment Decision System** — runs daily, fetches NASDAQ
data, evaluates portfolio rules, and pushes investment signals.

> No paid APIs needed. Uses [yfinance](https://github.com/ranaroussi/yfinance)
> with QQQ as the NASDAQ-100 proxy. Mock WeChat push works out of the box;
> swap in a real webhook when ready.

---

## ?? Investment Rules

| Rule | Condition | Action |
|------|-----------|--------|
| **DCA baseline** | Always | ?? 100 RMB/day into NASDAQ |
| **Defensive** | Drawdown > 20% from ATH | Continue DCA only — no extra equity exposure |
| **Rebalance** | NASDAQ allocation > 70% | Recommend increasing bond allocation |

---

## ?? Project Structure

```
investment-bot/
├── main.py                  # Orchestrator — single daily run
├── data_fetcher.py          # yfinance wrapper (QQQ, BND)
├── strategy.py              # Rule engine & decision dataclass
├── wechat.py                # Mock WeChat push (console + file)
├── requirements.txt         # Python dependencies
├── portfolio_state.json     # Auto-managed portfolio ledger
├── logs/                    # Signal history (auto-created)
├── .github/workflows/
│   └── daily.yml            # GitHub Actions — 9:00 AM UTC+8, Mon–Fri
└── README.md
```

---

## ?? Quick Start

```bash
# Clone & enter
git clone https://github.com/<your-username>/investment-bot.git
cd investment-bot

# Install dependencies
pip install -r requirements.txt

# Run once (dry-run: no state change)
python main.py --dry-run

# Run for real (updates portfolio_state.json)
python main.py
```

---

## ?? Automation

The GitHub Actions workflow (`daily.yml`) triggers:

- **Scheduled**: 9:00 AM Beijing time, Monday–Friday (`0 1 * * 1-5` UTC)
- **Manual**: `workflow_dispatch` button on the Actions tab
- **Push**: on every push to `main` that touches Python files

Each run:
1. Fetches QQQ & BND prices
2. Evaluates the decision rules
3. Logs the signal & pushes updated `portfolio_state.json` back to the repo

### Enabling the schedule

1. Push the repo to GitHub
2. Go to **Settings → Actions → General → Workflow permissions**
3. Set to **Read and write permissions**
4. The schedule activates automatically

---

## ?? Switching to Real WeChat Push

In `wechat.py`, uncomment the `requests.post(...)` block and
set your webhook URL via environment variable:

```bash
export WECHAT_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
```

Then modify `main.py` to pass `os.environ["WECHAT_WEBHOOK_URL"]` to
`send_wechat_message()`.

Alternative push channels (easy to swap in):
- [ServerChan ??](https://sct.ftqq.com/)
- [PushPlus](https://www.pushplus.plus/)
- Telegram Bot / Slack webhook

---

## ?? License

MIT — use it, fork it, deploy it. Trade at your own risk; this is not financial advice.
