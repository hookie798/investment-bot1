"""
Mock WeChat push module.
Replace `send_wechat_message` with real WeChat Work / ServerChan / PushPlus
API calls in production. The current implementation logs to console and a local
file so the daily automation is fully functional out of the box.
"""

import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "investment_signals.log")


def _ensure_log_dir() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)


def send_wechat_message(message: str, webhook_url: str = "") -> bool:
    """
    Send (or mock-send) an investment signal via WeChat.

    Parameters
    ----------
    message     : Plain-text or Markdown message body.
    webhook_url : WeChat Work bot webhook URL. Leave empty to use mock.

    Returns
    -------
    True if the message was "sent" (or logged) successfully.
    """
    _ensure_log_dir()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── Mock implementation ────────────────────────────────────────────
    if not webhook_url:
        # Log to console (visible in GitHub Actions logs)
        print("─" * 50)
        print(f"[WeChat Mock Push] {timestamp}")
        print("─" * 50)
        print(message)
        print("─" * 50)

        # Append to local log file
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"[{timestamp}]\n")
            f.write(message)
            f.write(f"{'='*60}\n")

        return True

    # ── Real WeChat Work webhook (uncomment & configure in production) ──
    #
    # import requests
    # payload = {
    #     "msgtype": "markdown",
    #     "markdown": {"content": message},
    # }
    # try:
    #     resp = requests.post(webhook_url, json=payload, timeout=10)
    #     return resp.status_code == 200 and resp.json().get("errcode") == 0
    # except Exception as exc:
    #     print(f"[ERROR] WeChat push failed: {exc}")
    #     return False

    print(f"[WARN] webhook_url provided but real push is not enabled. Falling back to mock.")
    return send_wechat_message(message, webhook_url="")


# ── Quick test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    send_wechat_message("?? Test signal: DCA_BUY — everything is normal.")
