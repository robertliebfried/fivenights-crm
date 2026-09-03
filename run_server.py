import uvicorn
import os
import sys

if __name__ == "__main__":
    print("=" * 60)
    print("   OUTREACH & EMAIL DISPATCH SERVER (Cold Email Platform)")
    print("=" * 60)
    print(" * Server Address: http://localhost:8000")
    print(" * Leads Database: ONE_BIG_WORLDWIDE_LICENSED_LEADS_2026-08-28.xlsx")
    print(" * SQLite Storage: outreach.db")
    print("=" * 60)
    uvicorn.run("email_server.app:app", host="0.0.0.0", port=8000, reload=False)
