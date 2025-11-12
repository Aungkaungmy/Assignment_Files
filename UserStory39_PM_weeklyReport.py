# ================================================
# User Story #39 – Platform Management: Generate Weekly Report (BCE)
# Live data from categories.json, users.json, requests.json
# ================================================

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Any

# ---------- Config ----------
BASE_DIR = Path(__file__).resolve().parent
CATEGORIES_FILE = BASE_DIR / "categories.json"
USERS_FILE      = BASE_DIR / "users.json"
REQUESTS_FILE   = BASE_DIR / "requests.json"


# ---------- Small helpers ----------
def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        raw = path.read_text(encoding="utf-8").strip()
        return json.loads(raw) if raw else default
    except Exception:
        return default


def _parse_iso_date(s: str | None) -> datetime | None:
    if not s:
        return None
    # Accept "YYYY-MM-DD" or full ISO
    try:
        if len(s) == 10 and s[4] == "-" and s[7] == "-":
            return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        pass
    try:
        # Handle '...Z' or with timezone stripped
        s2 = s.replace("Z", "")
        try:
            return datetime.fromisoformat(s2)
        except Exception:
            # fallback common shape "YYYY-MM-DDTHH:MM:SS"
            return datetime.strptime(s.split("Z")[0].split(".")[0], "%Y-%m-%dT%H:%M:%S")
    except Exception:
        return None


def _now_utc_date() -> datetime:
    # We only compare dates; keep naive UTC
    return datetime.utcnow()


def _in_last_7_days(iso_str: str | None, today: datetime) -> bool:
    """Inclusive range: today-6 .. today (by date)."""
    d = _parse_iso_date(iso_str)
    if not d:
        return False
    start = (today - timedelta(days=6)).date()
    end = today.date()
    return start <= d.date() <= end


def _norm_status(raw: str | None) -> str:
    """
    Normalize request status into one of:
      Pending | Assigned | Completed
    - 'in progress' is considered 'Assigned'
    - accepts any case
    """
    s = (raw or "").strip().lower()
    if s in ("completed", "complete"):
        return "Completed"
    if s in ("in progress", "in_progress", "inprogress", "assigned", "in prog"):
        return "Assigned"
    return "Pending"


# --- Boundary ---
class GenerateReportPage:
    def __init__(self):
        self.controller = GenerateReportController()

    def submitGenerateReport(self, dateOption: str = "weekly") -> str:
        if (dateOption or "").strip().lower() != "weekly":
            return "Error: Only 'weekly' date option is supported in this flow."
        return self.controller.generateReport(dateOption)

    def run(self):
        print("\n=== Platform Management - Generate Weekly Report ===")
        while True:
            print("\n1) Generate Weekly Report")
            print("2) Exit")
            choice = input("Enter your choice (1/2): ").strip()
            if choice == "1":
                print(self.submitGenerateReport("weekly"))
            elif choice == "2":
                print("Goodbye.")
                break
            else:
                print("Please choose 1 or 2.")


# --- Controller ---
class GenerateReportController:
    def __init__(self):
        self.category = Category()
        self.userProfile = UserProfile()
        self.request = Request()

    def generateReport(self, dateOption: str) -> str:
        # Live pulls
        cats = self.category.generateReport()
        users = self.userProfile.generateReport()
        req_summary = self.request.generateReport(dateOption)  # dict of lists

        pending = len(req_summary["Pending"])
        assigned = len(req_summary["Assigned"])
        completed = len(req_summary["Completed"])

        return (
            "Report (weekly)\n"
            f"Categories: {len(cats)}\n"
            f"UserProfiles: {len(users)}\n"
            f"Requests Pending: {pending}\n"
            f"Requests Assigned: {assigned}\n"
            f"Requests Completed: {completed}"
        )


# --- Entity: Category ---
class Category:
    def generateReport(self) -> List[Dict[str, Any]]:
        """
        Returns a list of categories from categories.json.
        Expected shape per item (any extra fields are fine):
          { "id": "CAT-001", "name": "Transportation", "desc": "...", ... }
        """
        cats = _load_json(CATEGORIES_FILE, [])
        # Normalize to a tiny list the BCE can display if needed
        out = []
        for c in cats:
            out.append({
                "categoryID": c.get("id") or c.get("categoryID"),
                "categoryName": c.get("name") or c.get("categoryName") or "—",
                "createdAt": c.get("createdAt"),
                "updatedAt": c.get("updatedAt"),
            })
        return out


# --- Entity: UserProfile ---
class UserProfile:
    def generateReport(self) -> List[Dict[str, Any]]:
        """
        Flattens users.json buckets (admin/csr/pin/platform) into a list.
        Normalizes status to Active/Inactive for consistency with UI.
        """
        data = _load_json(USERS_FILE, {})
        flat = []
        for role_bucket, users in (data or {}).items():
            for uname, rec in (users or {}).items():
                flat.append({
                    "userProfileID": rec.get("id"),
                    "userProfileName": rec.get("fullName") or uname,
                    "userRole": (rec.get("role") or role_bucket or "").strip().title(),  # Admin|Csr|Pin|Platform
                    "userProfileStatus": "Active" if (rec.get("status", "Active").lower() == "active") else "Inactive",
                    "createdAt": rec.get("createdAt"),
                    "updatedAt": rec.get("updatedAt"),
                })
        # Keep stable ordering
        flat.sort(key=lambda r: (r.get("userRole") or "", int(r.get("userProfileID") or 0)))
        return flat


# --- Entity: Request ---
class Request:
    def generateReport(self, dateOption: str = "weekly") -> Dict[str, List[Dict[str, Any]]]:
        """
        Reads requests.json and returns weekly buckets:
          { "Pending": [...], "Assigned": [...], "Completed": [...] }
        A request is included if ANY of these timestamps falls in the last 7 days:
          - updatedAt
          - createdAt
          - (fallback) 'date' (YYYY-MM-DD)
        """
        today = _now_utc_date()
        reqs = _load_json(REQUESTS_FILE, [])
        out = {"Pending": [], "Assigned": [], "Completed": []}

        for r in reqs:
            # Pick the most relevant timestamp (updatedAt > createdAt > date)
            ts = r.get("updatedAt") or r.get("createdAt") or r.get("date")
            if not _in_last_7_days(ts, today):
                continue

            bucket = _norm_status(r.get("status"))
            # minimal info for the BCE output
            out[bucket].append({
                "requestID": r.get("id"),
                "requestDate": (_parse_iso_date(ts) or today).date().isoformat(),
                "requestStatus": bucket,
                "requestTitle": r.get("title") or r.get("categoryName") or "Assistance",
                "requestCategory": r.get("categoryName") or r.get("categoryId"),
                "requestLocation": r.get("location") or "",
            })

        return out


# --- Run ---
if __name__ == "__main__":
    GenerateReportPage().run()
