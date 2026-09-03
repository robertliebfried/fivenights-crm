import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(BASE_DIR, "outreach.db")
EXCEL_PATH = os.path.join(BASE_DIR, "ONE_BIG_WORLDWIDE_LICENSED_LEADS_2026-08-28.xlsx")

# Default SMTP settings (initial placeholders)
DEFAULT_SETTINGS = {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "",
    "smtp_password": "",
    "smtp_use_tls": True,
    "smtp_use_ssl": False,
    "sender_name": "Web Solutions Agency",
    "sender_email": "",
    "reply_to": "",
    "daily_limit": 50,
    "delay_min": 10,
    "delay_max": 25,
    "dry_run_mode": True  # Default to dry-run safe mode!
}
