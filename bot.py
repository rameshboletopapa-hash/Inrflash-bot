#!/usr/bin/env python3
"""
INRFlash Task Monitor Bot  ⚡
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Monitors wallet.inrflash.com/offer_tasks.php for task changes.

Features:
  • Account-based login  — stores mobile+password, auto-refreshes session
  • Multi-account pool   — rotate accounts when one session expires
  • User-agent rotation  — randomised UA pool, never sends same device twice in a row
  • Multi-user access    — owner can grant task-view access by Telegram ID
  • Colorful buttons     — requires python-telegram-bot ≥ 22.7 (Bot API 9.4 style=)
  • Futuristic UI        — blockquote, <code>, <b>, <s>, dividers, inline keyboards
"""

import os
import re
import json
import random
import logging
import functools
from datetime import datetime
from html import escape
from typing import Optional

import requests
from bs4 import BeautifulSoup
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode

# ═══════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════
BOT_TOKEN        = "8919356714:AAEkoj65sVVE-VtTy24z2jQq3tz2Rw8jw2U"
OWNER_ID         = 8414537711
OWNER_USERNAME   = "@itzraj_kumar"
TASK_URL         = "https://wallet.inrflash.com/offer_tasks.php"
LOGIN_URL        = "https://wallet.inrflash.com/auth/login_api.php"
BASE_URL         = "https://wallet.inrflash.com"
JOB_NAME         = "inrflash_monitor"
DEFAULT_INTERVAL = 1

# ═══════════════════════════════════════════════════════════════════════════════
#  FIREBASE REALTIME DATABASE  (replaces local tasks_state.json / bot_config.json)
#  All persistent state now lives in the RTDB — no local files are written.
#  Optional auth: set env var FIREBASE_DB_SECRET (DB secret or ID token) if your
#  database security rules require authentication. Leave unset for open rules.
# ═══════════════════════════════════════════════════════════════════════════════
FIREBASE_DB_URL  = "https://inrflash-data-default-rtdb.firebaseio.com/"
STATE_NODE       = "tasks_state"   # RTDB node that mirrors the old tasks_state.json
CONFIG_NODE      = "bot_config"    # RTDB node that mirrors the old bot_config.json


def _fb_url(node: str) -> str:
    """Build the REST endpoint for a top-level RTDB node, adding auth if provided."""
    url = f"{FIREBASE_DB_URL.rstrip('/')}/{node}.json"
    secret = os.environ.get("FIREBASE_DB_SECRET")
    if secret:
        url += f"?auth={secret}"
    return url


def firebase_get(node: str):
    """GET a node's JSON. Returns parsed data, or None on error / missing node."""
    try:
        resp = requests.get(_fb_url(node), timeout=15)
        resp.raise_for_status()
        return resp.json()   # None if the node does not exist yet
    except Exception as e:
        logging.getLogger(__name__).error(f"Firebase GET '{node}' failed: {e}")
        return None


def firebase_put(node: str, data) -> bool:
    """PUT (overwrite) a node with the given JSON-serialisable data."""
    try:
        resp = requests.put(
            _fb_url(node),
            data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Firebase PUT '{node}' failed: {e}")
        return False

# ═══════════════════════════════════════════════════════════
#  USER-AGENT POOL
#  Varied mix — Android Chrome, iOS Safari, Windows Chrome,
#  Mac Safari, Firefox on Linux — rotated randomly each request.
# ═══════════════════════════════════════════════════════════
_UA_POOL = [
    # Android Chrome (various builds)
    {
        "user-agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Build/AD1A.240905.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.104 Mobile Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "x-requested-with": "com.android.chrome",
    },
    {
        "user-agent": "Mozilla/5.0 (Linux; Android 13; SM-G991B Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36",
        "sec-ch-ua": '"Chromium";v="129", "Google Chrome";v="129", "Not=A?Brand";v="8"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "x-requested-with": "com.android.chrome",
    },
    {
        "user-agent": "Mozilla/5.0 (Linux; Android 12; Redmi Note 11 Build/SKQ1.211006.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.88 Mobile Safari/537.36",
        "sec-ch-ua": '"Chromium";v="128", "Google Chrome";v="128", "Not;A=Brand";v="24"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "x-requested-with": "com.android.chrome",
    },
    # iOS Safari
    {
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
        "sec-ch-ua": "",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"iOS"',
        "x-requested-with": "",
    },
    {
        "user-agent": "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "sec-ch-ua": "",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"iPadOS"',
        "x-requested-with": "",
    },
    # Windows Chrome
    {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "x-requested-with": "",
    },
    {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "sec-ch-ua": '"Microsoft Edge";v="130", "Chromium";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "x-requested-with": "",
    },
    # Mac Safari
    {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
        "sec-ch-ua": "",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "x-requested-with": "",
    },
    # Firefox Linux
    {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
        "sec-ch-ua": "",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "x-requested-with": "",
    },
    # Mac Chrome
    {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "x-requested-with": "",
    },
]

_ACCEPT_LANG_POOL = [
    "en-IN,en-US;q=0.9,en;q=0.8",
    "en-US,en;q=0.9",
    "en-GB,en;q=0.9,en-US;q=0.8",
    "en-US,en;q=0.8,hi;q=0.6",
    "en-IN,hi;q=0.9,en;q=0.8",
]

_last_ua_index: int = -1


def _pick_ua() -> dict:
    """Pick a UA entry, never the same index twice in a row."""
    global _last_ua_index
    pool = list(range(len(_UA_POOL)))
    if _last_ua_index in pool and len(pool) > 1:
        pool.remove(_last_ua_index)
    idx = random.choice(pool)
    _last_ua_index = idx
    return _UA_POOL[idx]


# ═══════════════════════════════════════════════════════════
#  PERSISTENT CONFIG
#  accounts → list of:
#    { "label": str, "mobile": str, "password": str,
#      "remember_token": str|null, "phpsessid": str|null,
#      "status": "active"|"expired"|"unknown",
#      "last_login": str|null }
#  users    → list of {"id": int, "label": str, "notify": bool}
# ═══════════════════════════════════════════════════════════
_DEFAULTS: dict = {
    "interval":             DEFAULT_INTERVAL,
    "monitoring":           True,
    "active_account_index": 0,
    "accounts":             [],
    "users":                [],
}


def load_config() -> dict:
    """Load bot config from the Firebase RTDB, merged over defaults."""
    stored = firebase_get(CONFIG_NODE)
    merged = dict(_DEFAULTS)
    if isinstance(stored, dict):
        merged.update(stored)
    return merged


def save_config(cfg: dict) -> None:
    """Persist bot config to the Firebase RTDB (overwrites the bot_config node)."""
    firebase_put(CONFIG_NODE, cfg)


config = load_config()

# ═══════════════════════════════════════════════════════════
#  LOGGING
# ═══════════════════════════════════════════════════════════
logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),   # console only — no bot.log file is written
    ],
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
#  RUNTIME STATE
# ═══════════════════════════════════════════════════════════
runtime: dict = {
    "last_check":           None,
    "check_count":          0,
    "consecutive_failures": 0,
    "pending":              {},   # uid → pending context string
}

# ═══════════════════════════════════════════════════════════
#  TASK STATE
# ═══════════════════════════════════════════════════════════
def load_state() -> dict:
    """
    Load task state from the Firebase RTDB.
    Returns { task_name: {"reward": ..., "link": ...} }.

    Stored as a list under the "tasks" key so arbitrary task names (which may
    contain '.', '#', '$', '[', ']', '/' — all illegal as RTDB keys) are kept
    inside values rather than used as keys.
    """
    data = firebase_get(STATE_NODE)
    if not isinstance(data, dict):
        return {}
    tasks: dict = {}
    for item in data.get("tasks", []) or []:
        if isinstance(item, dict) and item.get("name") is not None:
            tasks[item["name"]] = {
                "reward": item.get("reward", "N/A"),
                "link":   item.get("link", "#"),
            }
    return tasks


def save_state(tasks: dict) -> None:
    """Persist task state to the Firebase RTDB (overwrites the tasks_state node)."""
    payload = {
        "tasks": [
            {"name": name, "reward": info.get("reward", "N/A"), "link": info.get("link", "#")}
            for name, info in tasks.items()
        ],
        "updated_at": _fb_timestamp(),
        "count": len(tasks),
    }
    firebase_put(STATE_NODE, payload)


def _fb_timestamp() -> str:
    """ISO timestamp for state metadata (best-effort, never raises)."""
    try:
        return datetime.now().astimezone().isoformat()
    except Exception:
        return ""


# ═══════════════════════════════════════════════════════════
#  ACCOUNT / SESSION HELPERS
# ═══════════════════════════════════════════════════════════
def get_active_account() -> Optional[dict]:
    accounts = config.get("accounts", [])
    if not accounts:
        return None
    idx = config.get("active_account_index", 0)
    if idx >= len(accounts):
        idx = 0
        config["active_account_index"] = 0
    return accounts[idx]


def _save_account(idx: int, account: dict) -> None:
    config["accounts"][idx] = account
    save_config(config)


def rotate_to_next_account() -> bool:
    """Move active_account_index to the next non-expired account. Returns True if rotated."""
    accounts = config.get("accounts", [])
    if not accounts:
        return False
    current = config.get("active_account_index", 0)
    for offset in range(1, len(accounts)):
        candidate = (current + offset) % len(accounts)
        if accounts[candidate].get("status") != "expired":
            config["active_account_index"] = candidate
            save_config(config)
            logger.info(f"Rotated to account #{candidate}: {accounts[candidate]['label']}")
            return True
    return False


def _cookie_str(account: dict) -> Optional[str]:
    """Build cookie header string from stored tokens."""
    token = account.get("remember_token", "")
    sessid = account.get("phpsessid", "")
    if not token and not sessid:
        return None
    parts = []
    if token:
        parts.append(f"remember_token={token}")
    if sessid:
        parts.append(f"PHPSESSID={sessid}")
    return "; ".join(parts)


def _build_fetch_headers(cookie_str: str) -> dict:
    ua = _pick_ua()
    headers = {
        "Host":                   "wallet.inrflash.com",
        "cache-control":          "max-age=0",
        "upgrade-insecure-requests": "1",
        "accept":                 "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "dnt":                    "1",
        "sec-fetch-site":         "none",
        "sec-fetch-mode":         "navigate",
        "sec-fetch-user":         "?1",
        "sec-fetch-dest":         "document",
        "accept-encoding":        "gzip, deflate, br, zstd",
        "accept-language":        random.choice(_ACCEPT_LANG_POOL),
        "cookie":                 cookie_str,
        "priority":               "u=0, i",
        "user-agent":             ua["user-agent"],
        "sec-ch-ua":              ua["sec-ch-ua"],
        "sec-ch-ua-mobile":       ua["sec-ch-ua-mobile"],
        "sec-ch-ua-platform":     ua["sec-ch-ua-platform"],
    }
    if ua["x-requested-with"]:
        headers["x-requested-with"] = ua["x-requested-with"]
    return headers


def _build_login_headers(phpsessid: str) -> dict:
    ua = _pick_ua()
    headers = {
        "Host":              "wallet.inrflash.com",
        "origin":            BASE_URL,
        "referer":           f"{BASE_URL}/index.php",
        "accept":            "*/*",
        "accept-encoding":   "gzip, deflate, br, zstd",
        "accept-language":   random.choice(_ACCEPT_LANG_POOL),
        "sec-fetch-site":    "same-origin",
        "sec-fetch-mode":    "cors",
        "sec-fetch-dest":    "empty",
        "dnt":               "1",
        "priority":          "u=1, i",
        "cookie":            f"PHPSESSID={phpsessid}",
        "user-agent":        ua["user-agent"],
        "sec-ch-ua":         ua["sec-ch-ua"],
        "sec-ch-ua-mobile":  ua["sec-ch-ua-mobile"],
        "sec-ch-ua-platform": ua["sec-ch-ua-platform"],
    }
    if ua["x-requested-with"]:
        headers["x-requested-with"] = ua["x-requested-with"]
    return headers


# ═══════════════════════════════════════════════════════════
#  LOGIN FUNCTION
# ═══════════════════════════════════════════════════════════
def do_login(account_idx: int) -> tuple[bool, str]:
    """
    Log in using stored credentials for accounts[account_idx].
    Returns (success: bool, message: str).
    On success, updates remember_token + phpsessid + status in config.
    """
    accounts = config.get("accounts", [])
    if account_idx >= len(accounts):
        return False, "Account index out of range."

    acct = accounts[account_idx]
    mobile   = acct.get("mobile", "")
    password = acct.get("password", "")
    label    = acct.get("label", f"Account #{account_idx + 1}")

    if not mobile or not password:
        return False, f"Account '{label}' has no credentials stored."

    try:
        # Step 1: GET the login page to obtain a fresh PHPSESSID
        session = requests.Session()
        init = session.get(f"{BASE_URL}/index.php", timeout=15)
        phpsessid = ""
        for c in session.cookies:
            if c.name == "PHPSESSID":
                phpsessid = c.value
                break
        if not phpsessid:
            # Try to parse from Set-Cookie header directly
            sc = init.headers.get("set-cookie", "")
            m = re.search(r"PHPSESSID=([^;]+)", sc)
            if m:
                phpsessid = m.group(1)

        if not phpsessid:
            logger.warning(f"Login [{label}]: No PHPSESSID from init request, proceeding anyway.")
            phpsessid = "session" + str(random.randint(100000, 999999))

        # Step 2: POST login credentials as multipart/form-data
        login_headers = _build_login_headers(phpsessid)
        form_data = {
            "mobile":      (None, mobile),
            "password":    (None, password),
            "remember-me": (None, "on"),
        }
        resp = session.post(
            LOGIN_URL,
            files=form_data,
            headers=login_headers,
            timeout=20,
            allow_redirects=True,
        )
        resp.raise_for_status()

        # Step 3: Extract remember_token from Set-Cookie
        remember_token = ""
        new_phpsessid  = phpsessid

        # Check all Set-Cookie headers in response
        all_sc = resp.headers.get("set-cookie", "")
        m_rt = re.search(r"remember_token=([a-f0-9]{64})", all_sc)
        if m_rt:
            remember_token = m_rt.group(1)

        # Also check session cookies
        for c in session.cookies:
            if c.name == "remember_token" and c.value:
                remember_token = c.value
            if c.name == "PHPSESSID" and c.value:
                new_phpsessid = c.value

        # Step 4: Parse JSON response for errors
        try:
            body = resp.json()
            if isinstance(body, dict):
                # Some APIs return {"status": "error", "message": "..."}
                if body.get("status") == "error" or body.get("error"):
                    msg = body.get("message") or body.get("error") or "Login rejected by server."
                    acct["status"] = "expired"
                    _save_account(account_idx, acct)
                    return False, f"Login failed: {msg}"
        except Exception:
            pass  # Response isn't JSON — that's fine for HTML-based sites

        if not remember_token:
            # If no token in cookies, login likely failed (wrong password / redirect to error)
            if "login" in resp.url.lower() or "error" in resp.text.lower():
                acct["status"] = "expired"
                _save_account(account_idx, acct)
                return False, "Login failed — wrong credentials or site returned an error page."
            # No token but no error either — treat as partial success
            logger.warning(f"Login [{label}]: No remember_token found, but no error detected.")
            acct["phpsessid"]     = new_phpsessid
            acct["remember_token"] = ""
            acct["status"]        = "unknown"
            acct["last_login"]    = _now()
            _save_account(account_idx, acct)
            return True, "Logged in but no remember_token received — session may be short-lived."

        acct["remember_token"] = remember_token
        acct["phpsessid"]      = new_phpsessid
        acct["status"]         = "active"
        acct["last_login"]     = _now()
        _save_account(account_idx, acct)
        logger.info(f"Login [{label}]: Success — token={remember_token[:12]}…")
        return True, "Login successful."

    except requests.exceptions.ConnectionError:
        return False, "Connection error during login."
    except requests.exceptions.Timeout:
        return False, "Login request timed out."
    except requests.exceptions.HTTPError as e:
        return False, f"HTTP error during login: {e}"
    except Exception as e:
        logger.error(f"Login [{label}]: Unexpected error: {e}", exc_info=True)
        return False, f"Unexpected error: {e}"


def auto_login_active() -> tuple[bool, str]:
    """Try to login with the currently active account."""
    accounts = config.get("accounts", [])
    if not accounts:
        return False, "No accounts configured. Add an account in Settings → Accounts."
    idx = config.get("active_account_index", 0)
    return do_login(idx)


# ═══════════════════════════════════════════════════════════
#  SCRAPER
# ═══════════════════════════════════════════════════════════
def fetch_tasks() -> Optional[dict]:
    """
    Fetch and parse the offer_tasks page using the active account's session.
    Returns:
        dict  → { task_name: {"reward": "₹X", "link": "..."} }
        None  → network/auth error
        {}    → page loaded but no tasks
    """
    acct = get_active_account()
    if not acct:
        logger.error("No accounts configured — cannot fetch.")
        return None

    cookie_str = _cookie_str(acct)
    if not cookie_str:
        logger.warning(f"Account '{acct.get('label')}' has no session tokens — need to login first.")
        return None

    try:
        resp = requests.get(TASK_URL, headers=_build_fetch_headers(cookie_str), timeout=20)
        resp.raise_for_status()

        if "login" in resp.url.lower() or "auth/login" in resp.url.lower():
            logger.warning("Redirected to login — session expired!")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        task_items = soup.find_all("li", class_="tr-task")

        if not task_items:
            logger.warning("0 task items found — possible auth issue or genuinely empty list.")
            return {}

        tasks: dict = {}
        for item in task_items:
            name_el   = item.find(class_="tr-task-name")
            reward_el = item.find(class_="tr-task-reward-line")
            link_el   = item.find("a", class_="tr-cta")

            name   = name_el.get_text(strip=True)                                             if name_el                            else "Unknown"
            reward = reward_el.find("b").get_text(strip=True) if reward_el and reward_el.find("b") else "N/A"
            link   = link_el.get("href", "#")                                                  if link_el                            else "#"

            tasks[name] = {"reward": reward, "link": link}

        logger.info(f"Fetched {len(tasks)} task(s).")
        return tasks

    except requests.exceptions.ConnectionError:
        logger.error("Connection error.")
    except requests.exceptions.Timeout:
        logger.error("Request timed out (20 s).")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")
    except Exception as e:
        logger.error(f"Unexpected fetch error: {e}", exc_info=True)
    return None


# ═══════════════════════════════════════════════════════════
#  COMPARISON
# ═══════════════════════════════════════════════════════════
def compare_tasks(old: dict, new: dict) -> tuple[list, list, list]:
    old_keys = set(old.keys())
    new_keys = set(new.keys())
    added   = [{"name": k, **new[k]} for k in new_keys - old_keys]
    removed = [{"name": k, **old[k]} for k in old_keys - new_keys]
    changed = [
        {"name": k, "old_reward": old[k]["reward"], "new_reward": new[k]["reward"], "link": new[k]["link"]}
        for k in old_keys & new_keys
        if old[k]["reward"] != new[k]["reward"]
    ]
    return added, removed, changed


# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════
def _now() -> str:
    return datetime.now().strftime("%d %b %Y · %I:%M %p")


def _div() -> str:
    return "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄"


def _sec(icon: str, title: str) -> str:
    return f"{icon} <b>{title}</b>"


# ═══════════════════════════════════════════════════════════
#  USER HELPERS
# ═══════════════════════════════════════════════════════════
def get_allowed_ids() -> set:
    ids = {OWNER_ID}
    for u in config.get("users", []):
        ids.add(int(u["id"]))
    return ids


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


def get_notify_ids() -> list:
    ids = [OWNER_ID]
    for u in config.get("users", []):
        if u.get("notify", True):
            ids.append(int(u["id"]))
    return ids


# ═══════════════════════════════════════════════════════════
#  KEYBOARDS
# ═══════════════════════════════════════════════════════════
def main_menu_keyboard(for_owner: bool = True) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("📋  Tasks",       callback_data="btn_tasks",  style="primary"),
            InlineKeyboardButton("📡  Status",      callback_data="btn_status", style="primary"),
        ],
        [
            InlineKeyboardButton("🔍  Force Check", callback_data="btn_check",  style="success"),
        ],
    ]
    if for_owner:
        rows += [
            [
                InlineKeyboardButton("⏸  Pause",    callback_data="btn_pause",  style="danger"),
                InlineKeyboardButton("▶️  Resume",   callback_data="btn_resume", style="success"),
            ],
            [
                InlineKeyboardButton("⚙️  Settings", callback_data="btn_settings", style="primary"),
            ],
        ]
    return InlineKeyboardMarkup(rows)


def back_keyboard(dest: str = "btn_menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("← Back", callback_data=dest, style="primary"),
    ]])


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👥  Users",     callback_data="btn_users",    style="primary"),
            InlineKeyboardButton("🔐  Accounts",  callback_data="btn_accounts", style="primary"),
        ],
        [
            InlineKeyboardButton("⏱  Set Interval", callback_data="btn_setinterval_help", style="primary"),
        ],
        [InlineKeyboardButton("← Back", callback_data="btn_menu", style="primary")],
    ])


def users_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕  Add User",    callback_data="btn_adduser",          style="success"),
            InlineKeyboardButton("➖  Remove User", callback_data="btn_removeuser_list",  style="danger"),
        ],
        [
            InlineKeyboardButton("👁  View Users",  callback_data="btn_listusers",        style="primary"),
        ],
        [InlineKeyboardButton("← Back", callback_data="btn_settings", style="primary")],
    ])


def accounts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕  Add Account",    callback_data="btn_addaccount",         style="success"),
            InlineKeyboardButton("➖  Remove Account", callback_data="btn_removeaccount_list", style="danger"),
        ],
        [
            InlineKeyboardButton("🔄  Login All",      callback_data="btn_loginall",           style="success"),
            InlineKeyboardButton("🔀  Switch Active",  callback_data="btn_switchaccount",      style="primary"),
        ],
        [
            InlineKeyboardButton("📋  View Accounts",  callback_data="btn_listaccounts",       style="primary"),
        ],
        [InlineKeyboardButton("← Back", callback_data="btn_settings", style="primary")],
    ])


def check_result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔁  Check Again", callback_data="btn_check",  style="success"),
            InlineKeyboardButton("📋  View Tasks",  callback_data="btn_tasks",  style="primary"),
        ],
        [InlineKeyboardButton("← Back", callback_data="btn_menu", style="primary")],
    ])


def remove_user_keyboard() -> InlineKeyboardMarkup:
    users = config.get("users", [])
    rows  = []
    for u in users:
        label = escape(u.get("label", str(u["id"])))
        rows.append([InlineKeyboardButton(
            f"🗑 {label}  (ID: {u['id']})",
            callback_data=f"btn_removeuser_{u['id']}",
            style="danger",
        )])
    rows.append([InlineKeyboardButton("← Back", callback_data="btn_users", style="primary")])
    return InlineKeyboardMarkup(rows)


def remove_account_keyboard() -> InlineKeyboardMarkup:
    accounts = config.get("accounts", [])
    rows     = []
    for i, a in enumerate(accounts):
        st = "🟢" if a.get("status") == "active" else ("🔴" if a.get("status") == "expired" else "⚪")
        rows.append([InlineKeyboardButton(
            f"🗑 {st} {escape(a['label'])}",
            callback_data=f"btn_removeaccount_{i}",
            style="danger",
        )])
    rows.append([InlineKeyboardButton("← Back", callback_data="btn_accounts", style="primary")])
    return InlineKeyboardMarkup(rows)


def switch_account_keyboard() -> InlineKeyboardMarkup:
    accounts = config.get("accounts", [])
    active   = config.get("active_account_index", 0)
    rows     = []
    for i, a in enumerate(accounts):
        st    = "🟢" if a.get("status") == "active" else ("🔴" if a.get("status") == "expired" else "⚪")
        check = "✓ " if i == active else ""
        rows.append([InlineKeyboardButton(
            f"{check}{st} {escape(a['label'])}",
            callback_data=f"btn_setactiveaccount_{i}",
            style="success" if i == active else "primary",
        )])
    rows.append([InlineKeyboardButton("← Back", callback_data="btn_accounts", style="primary")])
    return InlineKeyboardMarkup(rows)


# ═══════════════════════════════════════════════════════════
#  MESSAGE BUILDERS
# ═══════════════════════════════════════════════════════════
def build_welcome_msg(for_owner: bool = True) -> str:
    base = (
        f"<blockquote>⚡ <b>INRFlash Task Monitor</b>\n"
        f"Watching: <code>{TASK_URL}</code>\n"
        f"Interval: every <b>{config['interval']} min</b></blockquote>\n\n"
        f"👋 <b>Welcome back!</b>\n\n"
        f"<i>Tap a button below to get started.</i>"
    )
    if for_owner:
        base += (
            "\n\n<blockquote expandable>ℹ️ <b>Owner Tips</b>\n"
            "• <b>Settings → Accounts</b> — add your INRFlash login (mobile + password)\n"
            "• Bot auto-logs in when session expires — no manual cookie hunting!\n"
            "• <b>Settings → Users</b> — grant task-view access to other Telegram IDs\n"
            "• UA rotation is on by default — each request looks like a different device</blockquote>"
        )
    return base


def build_task_list(tasks: dict) -> str:
    if not tasks:
        return "<blockquote>⚠️ <b>No Tasks Available</b>\nThe list is currently empty.</blockquote>"
    lines = [f"<blockquote>📋 <b>Active Tasks</b>  ·  <i>{_now()}</i></blockquote>\n", f"{_div()}\n"]
    for i, (name, info) in enumerate(sorted(tasks.items()), 1):
        link_part = f'\n   <a href="{escape(info["link"])}">▶️ Start Task</a>' if info.get("link", "#") != "#" else ""
        lines.append(
            f"<b>{i}.</b> {escape(name)}\n"
            f"   💰 Reward: <code>{escape(info['reward'])}</code>{link_part}\n"
        )
    lines += [f"{_div()}", f"<i>📊 Total: <b>{len(tasks)}</b> task(s)</i>"]
    return "\n".join(lines)


def build_status_msg() -> str:
    saved = len(load_state())
    icon  = "🟢" if config["monitoring"] else "🔴"
    label = "Active ✓" if config["monitoring"] else "Paused ✗"

    acct    = get_active_account()
    ac_info = "<i>None — add an account in Settings</i>"
    if acct:
        st_icon = "🟢" if acct.get("status") == "active" else ("🔴" if acct.get("status") == "expired" else "⚪")
        last_lg = acct.get("last_login") or "Never"
        ac_info = (
            f"{st_icon} <b>{escape(acct['label'])}</b>\n"
            f"   Last login: <i>{last_lg}</i>"
        )

    return (
        f"<blockquote>📡 <b>Monitor Dashboard</b>  ·  <i>{_now()}</i></blockquote>\n\n"
        f"{_sec(icon, 'Monitoring')}\n"
        f"<blockquote>State       : <b>{label}</b>\n"
        f"Interval    : <code>{config['interval']} min</code>\n"
        f"Last Check  : <b>{runtime['last_check'] or 'Not yet'}</b>\n"
        f"Checks      : <b>{runtime['check_count']}</b>\n"
        f"Failures    : <b>{runtime['consecutive_failures']}</b>\n"
        f"Known Tasks : <b>{saved}</b></blockquote>\n\n"
        f"{_sec('🔐', 'Active Account')}\n"
        f"<blockquote>{ac_info}</blockquote>\n\n"
        f"{_sec('🌐', 'Target')}\n<code>{TASK_URL}</code>"
    )


def build_account_list_msg() -> str:
    accounts = config.get("accounts", [])
    active   = config.get("active_account_index", 0)
    if not accounts:
        return (
            "<blockquote>🔐 <b>No Accounts Configured</b>\n"
            "Add an account via ➕ Add Account.\n"
            "Your mobile number and password are stored locally.</blockquote>"
        )
    lines = [f"<blockquote>🔐 <b>Accounts Pool</b>  ({len(accounts)} account(s))</blockquote>\n", _div()]
    for i, a in enumerate(accounts):
        st    = "🟢 <b>Active</b>" if a.get("status") == "active" else ("🔴 <b>Expired</b>" if a.get("status") == "expired" else "⚪ <i>Unknown</i>")
        arrow = "  ◀ <i>current</i>" if i == active else ""
        token = a.get("remember_token", "")
        token_preview = f"<code>{token[:12]}…</code>" if token else "<i>No token yet</i>"
        last_lg = a.get("last_login") or "Never"
        lines.append(
            f"\n<b>#{i+1} — {escape(a['label'])}</b>{arrow}\n"
            f"Mobile    : <code>{escape(a.get('mobile','?'))}</code>\n"
            f"Status    : {st}\n"
            f"Token     : {token_preview}\n"
            f"Last Login: <i>{last_lg}</i>"
        )
    lines.append(f"\n{_div()}\n<i>Tap 🔄 Login All to refresh sessions for all accounts.</i>")
    return "\n".join(lines)


def build_user_list_msg() -> str:
    users = config.get("users", [])
    lines = [f"<blockquote>👥 <b>Authorised Users</b></blockquote>\n", _div()]
    lines.append(f"\n🔑 <b>{escape(OWNER_USERNAME)}</b>  <code>{OWNER_ID}</code>  — Owner (full access)\n")
    if not users:
        lines.append("\n<i>No additional users added yet.</i>")
    else:
        for u in users:
            notify = "🔔" if u.get("notify", True) else "🔕"
            lines.append(f"{notify} <b>{escape(u.get('label', 'User'))}</b>  <code>{u['id']}</code>  — Task View")
    lines.append(f"\n{_div()}\n<i>Added users can view tasks and receive change alerts.</i>")
    return "\n".join(lines)


def build_change_alert(added: list, removed: list, changed: list, current: dict) -> str:
    lines = [f"<blockquote>🔔 <b>Task Update Alert</b>  ·  <i>{_now()}</i></blockquote>\n", f"{_div()}\n"]
    if added:
        lines.append(_sec("✅", f"{len(added)} New Task(s) Added"))
        for t in added:
            lp = f'\n   <a href="{escape(t["link"])}">▶️ Start Task</a>' if t.get("link", "#") != "#" else ""
            lines.append(
                f"<blockquote>🆕 <b>{escape(t['name'])}</b>\n"
                f"   💰 Reward: <code>{escape(t['reward'])}</code>{lp}</blockquote>"
            )
    if removed:
        lines.append(f"\n{_sec('❌', f'{len(removed)} Task(s) Removed')}")
        for t in removed:
            lines.append(
                f"<blockquote>🗑 <s>{escape(t['name'])}</s>\n"
                f"   Was: <code>{escape(t['reward'])}</code></blockquote>"
            )
    if changed:
        lines.append(f"\n{_sec('💰', f'{len(changed)} Reward Change(s)')}")
        for t in changed:
            lp = f'\n   <a href="{escape(t["link"])}">▶️ Start</a>' if t.get("link", "#") != "#" else ""
            lines.append(
                f"<blockquote>🔄 <b>{escape(t['name'])}</b>\n"
                f"   <s>{escape(t['old_reward'])}</s> → <code>{escape(t['new_reward'])}</code>{lp}</blockquote>"
            )
    lines += [f"\n{_div()}", f"<i>📊 Active tasks now: <b>{len(current)}</b></i>"]
    return "\n".join(lines)


def build_startup_msg(tasks: dict) -> str:
    header = (
        f"<blockquote>🚀 <b>INRFlash Monitor — Online!</b>\n"
        f"Found <b>{len(tasks)}</b> task(s) on first scan.\n"
        f"Checking every <b>{config['interval']} min</b>.</blockquote>\n\n"
    )
    return header + build_task_list(tasks)


# ═══════════════════════════════════════════════════════════
#  AUTH GUARDS
# ═══════════════════════════════════════════════════════════
def allowed_only(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user or user.id not in get_allowed_ids():
            msg = (
                f"<blockquote>⛔ <b>Access Denied</b>\nThis is a private bot.</blockquote>\n\n"
                f"Contact the owner: <b>{escape(OWNER_USERNAME)}</b>"
            )
            if update.message:
                await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
            elif update.callback_query:
                await update.callback_query.answer("⛔ Access Denied.", show_alert=True)
            logger.warning(f"Blocked: user {user.id if user else '?'}")
            return
        return await func(update, context)
    return wrapper


def owner_only(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user or not is_owner(user.id):
            if update.callback_query:
                await update.callback_query.answer("⛔ Owner only.", show_alert=True)
            elif update.message:
                await update.message.reply_text(
                    "<blockquote>⛔ <b>Owner Only</b></blockquote>",
                    parse_mode=ParseMode.HTML,
                )
            return
        return await func(update, context)
    return wrapper


# ═══════════════════════════════════════════════════════════
#  COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════
@allowed_only
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    own = is_owner(uid)
    await update.message.reply_text(
        build_welcome_msg(own),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=main_menu_keyboard(own),
    )


@allowed_only
async def tasks_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("⏳ <i>Fetching…</i>", parse_mode=ParseMode.HTML)
    tasks = fetch_tasks()
    if tasks is None:
        await msg.edit_text(
            "<blockquote>❌ <b>Fetch Failed</b>\nSession may be expired.\nGo to Settings → Accounts → Login All.</blockquote>",
            parse_mode=ParseMode.HTML, reply_markup=back_keyboard(),
        )
        return
    await msg.edit_text(
        build_task_list(tasks), parse_mode=ParseMode.HTML,
        disable_web_page_preview=True, reply_markup=back_keyboard(),
    )


@owner_only
async def setinterval_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            f"<blockquote>⚙️ <b>Set Interval</b></blockquote>\n\nUsage:\n<code>/setinterval &lt;minutes&gt;</code>\n\nCurrent: <code>{config['interval']} min</code>",
            parse_mode=ParseMode.HTML, reply_markup=back_keyboard(),
        )
        return
    try:
        mins = int(context.args[0])
        if mins < 1:
            raise ValueError
        config["interval"] = mins
        save_config(config)
        for job in context.job_queue.get_jobs_by_name(JOB_NAME):
            job.schedule_removal()
        context.job_queue.run_repeating(monitor_job, interval=mins * 60, first=mins * 60, name=JOB_NAME)
        await update.message.reply_text(
            f"<blockquote>✅ <b>Interval Updated</b>\nChecking every <code>{mins} min</code>.</blockquote>",
            parse_mode=ParseMode.HTML, reply_markup=back_keyboard(),
        )
    except (ValueError, IndexError):
        await update.message.reply_text(
            "<blockquote>❌ Invalid — must be a whole number ≥ 1.</blockquote>",
            parse_mode=ParseMode.HTML,
        )


@allowed_only
async def unknown_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid     = update.effective_user.id
    own     = is_owner(uid)
    pending = runtime["pending"].get(uid)
    if pending:
        await _handle_pending_text(update, context, pending)
        return
    await update.message.reply_text(
        "<blockquote>❓ <b>Unknown Command</b>\nUse the menu below.</blockquote>",
        parse_mode=ParseMode.HTML, reply_markup=main_menu_keyboard(own),
    )


# ═══════════════════════════════════════════════════════════
#  PENDING-TEXT INPUT ROUTER
# ═══════════════════════════════════════════════════════════
async def _handle_pending_text(update: Update, context: ContextTypes.DEFAULT_TYPE, pending: str) -> None:
    uid  = update.effective_user.id
    text = (update.message.text or "").strip()
    runtime["pending"].pop(uid, None)

    # ── Add user ──────────────────────────────────────────
    if pending == "await_adduser":
        parts = text.split(None, 1)
        if not parts or not parts[0].lstrip("-").isdigit():
            await update.message.reply_text(
                "<blockquote>❌ <b>Invalid Input</b>\nSend: <code>&lt;telegram_id&gt; [optional label]</code></blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_users"),
            )
            return
        new_id    = int(parts[0])
        new_label = parts[1].strip() if len(parts) > 1 else f"User {new_id}"
        users = config.setdefault("users", [])
        if any(int(u["id"]) == new_id for u in users):
            await update.message.reply_text(
                f"<blockquote>⚠️ User <code>{new_id}</code> is already authorised.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_users"),
            )
            return
        if new_id == OWNER_ID:
            await update.message.reply_text(
                "<blockquote>⚠️ That's your own ID — you already have full access.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_users"),
            )
            return
        users.append({"id": new_id, "label": new_label, "notify": True})
        save_config(config)
        await update.message.reply_text(
            f"<blockquote>✅ <b>User Added</b>\n"
            f"<b>{escape(new_label)}</b>  <code>{new_id}</code>\n"
            f"They can now view tasks and receive notifications.</blockquote>",
            parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_users"),
        )

    # ── Add account (step 1: label|mobile|password) ───────
    elif pending == "await_addaccount":
        # Format: Label | mobile | password
        # OR just: mobile | password   (label auto-generated)
        parts = [p.strip() for p in text.split("|")]
        if len(parts) == 3:
            label, mobile, password = parts
        elif len(parts) == 2:
            mobile, password = parts
            label = f"Account #{len(config.get('accounts', [])) + 1}"
        else:
            await update.message.reply_text(
                "<blockquote>❌ <b>Wrong Format</b>\n\n"
                "Send in this format:\n"
                "<code>Label | 9876543210 | yourpassword</code>\n\n"
                "Or without a label:\n"
                "<code>9876543210 | yourpassword</code></blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_accounts"),
            )
            return

        if not mobile or not password:
            await update.message.reply_text(
                "<blockquote>❌ Mobile and password cannot be empty.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_accounts"),
            )
            return

        # Save account first with unknown status
        new_account = {
            "label":          label,
            "mobile":         mobile,
            "password":       password,
            "remember_token": "",
            "phpsessid":      "",
            "status":         "unknown",
            "last_login":     None,
        }
        accounts = config.setdefault("accounts", [])
        new_idx  = len(accounts)
        accounts.append(new_account)
        save_config(config)

        wait = await update.message.reply_text(
            f"<blockquote>🔐 <b>Account saved!</b>\nLogging in as <b>{escape(label)}</b>…</blockquote>",
            parse_mode=ParseMode.HTML,
        )
        success, msg = do_login(new_idx)
        if success:
            await wait.edit_text(
                f"<blockquote>✅ <b>Account Added &amp; Logged In!</b>\n"
                f"<b>{escape(label)}</b>  (<code>{escape(mobile)}</code>)\n"
                f"Session is active and ready.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_accounts"),
            )
        else:
            await wait.edit_text(
                f"<blockquote>⚠️ <b>Account Saved — Login Failed</b>\n"
                f"<b>{escape(label)}</b>  (<code>{escape(mobile)}</code>)\n\n"
                f"Reason: <i>{escape(msg)}</i>\n\n"
                f"Check credentials. Tap 🔄 Login All to retry.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_accounts"),
            )

    # ── Set interval ──────────────────────────────────────
    elif pending.startswith("await_setinterval"):
        try:
            mins = int(text)
            if mins < 1:
                raise ValueError
            config["interval"] = mins
            save_config(config)
            for job in context.job_queue.get_jobs_by_name(JOB_NAME):
                job.schedule_removal()
            context.job_queue.run_repeating(monitor_job, interval=mins * 60, first=mins * 60, name=JOB_NAME)
            await update.message.reply_text(
                f"<blockquote>✅ <b>Interval Updated</b>\nChecking every <code>{mins} min</code>.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_settings"),
            )
        except ValueError:
            await update.message.reply_text(
                "<blockquote>❌ Invalid — must be a whole number ≥ 1.</blockquote>",
                parse_mode=ParseMode.HTML,
            )
    else:
        runtime["pending"].pop(uid, None)


# ═══════════════════════════════════════════════════════════
#  PLAIN-MESSAGE HANDLER
# ═══════════════════════════════════════════════════════════
@allowed_only
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid     = update.effective_user.id
    pending = runtime["pending"].get(uid)
    if pending:
        await _handle_pending_text(update, context, pending)


# ═══════════════════════════════════════════════════════════
#  CALLBACK QUERY HANDLER
# ═══════════════════════════════════════════════════════════
@allowed_only
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data  = query.data
    uid   = query.from_user.id
    own   = is_owner(uid)
    await query.answer()

    # ── Owner-only guard ──────────────────────────────────
    _owner_only_buttons = {
        "btn_pause", "btn_resume", "btn_settings",
        "btn_users", "btn_accounts",
        "btn_adduser", "btn_removeuser_list", "btn_listusers",
        "btn_addaccount", "btn_removeaccount_list", "btn_loginall",
        "btn_switchaccount", "btn_listaccounts",
        "btn_setinterval_help",
    }
    if data in _owner_only_buttons or data.startswith(
        ("btn_removeuser_", "btn_removeaccount_", "btn_setactiveaccount_")
    ):
        if not own:
            await query.answer("⛔ Owner only.", show_alert=True)
            return

    # ════════════════ NAVIGATION ═════════════════════════

    if data == "btn_menu":
        await query.edit_message_text(
            build_welcome_msg(own), parse_mode=ParseMode.HTML,
            disable_web_page_preview=True, reply_markup=main_menu_keyboard(own),
        )

    elif data == "btn_settings":
        await query.edit_message_text(
            "<blockquote>⚙️ <b>Settings</b></blockquote>\n\nChoose a category:",
            parse_mode=ParseMode.HTML, reply_markup=settings_keyboard(),
        )

    # ════════════════ TASKS & STATUS ══════════════════════

    elif data == "btn_tasks":
        await query.edit_message_text("⏳ <i>Fetching tasks…</i>", parse_mode=ParseMode.HTML)
        tasks = fetch_tasks()
        if tasks is None:
            await query.edit_message_text(
                "<blockquote>❌ <b>Fetch Failed</b>\nSession expired or no account configured.\n"
                "Go to Settings → Accounts → Login All.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard(),
            )
        else:
            await query.edit_message_text(
                build_task_list(tasks), parse_mode=ParseMode.HTML,
                disable_web_page_preview=True, reply_markup=back_keyboard(),
            )

    elif data == "btn_status":
        await query.edit_message_text(
            build_status_msg(), parse_mode=ParseMode.HTML,
            disable_web_page_preview=True, reply_markup=back_keyboard(),
        )

    elif data == "btn_check":
        await query.edit_message_text("🔍 <i>Running manual check…</i>", parse_mode=ParseMode.HTML)
        result = await _do_check(context.bot)
        if result is None:
            txt = "<blockquote>❌ <b>Check Failed</b>\nFetch error — see Status for details.</blockquote>"
        elif result:
            txt = "<blockquote>✅ <b>Done!</b> Changes found — notification sent ☝️</blockquote>"
        else:
            txt = "<blockquote>✅ <b>Done!</b> No task changes detected.</blockquote>"
        await query.edit_message_text(txt, parse_mode=ParseMode.HTML, reply_markup=check_result_keyboard())

    elif data == "btn_pause":
        config["monitoring"] = False
        save_config(config)
        await query.edit_message_text(
            "<blockquote>⏸ <b>Monitoring Paused</b>\nTap ▶️ Resume to restart.</blockquote>",
            parse_mode=ParseMode.HTML, reply_markup=back_keyboard(),
        )

    elif data == "btn_resume":
        config["monitoring"] = True
        save_config(config)
        await query.edit_message_text(
            f"<blockquote>▶️ <b>Monitoring Resumed</b>\nChecking every <code>{config['interval']} min</code>.</blockquote>",
            parse_mode=ParseMode.HTML, reply_markup=back_keyboard(),
        )

    # ════════════════ USER MANAGEMENT ════════════════════

    elif data == "btn_users":
        await query.edit_message_text(
            "<blockquote>👥 <b>User Management</b></blockquote>\n\n"
            "Added users can view tasks and receive notifications.\n"
            "<i>Only their Telegram ID is needed.</i>",
            parse_mode=ParseMode.HTML, reply_markup=users_keyboard(),
        )

    elif data == "btn_listusers":
        await query.edit_message_text(
            build_user_list_msg(), parse_mode=ParseMode.HTML,
            reply_markup=back_keyboard("btn_users"),
        )

    elif data == "btn_adduser":
        runtime["pending"][uid] = "await_adduser"
        await query.edit_message_text(
            "<blockquote>➕ <b>Add User</b></blockquote>\n\n"
            "Send the user's <b>Telegram ID</b> (optional: add a label after a space):\n\n"
            "<code>123456789</code>\n"
            "<code>123456789 My Friend</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖ Cancel", callback_data="btn_users", style="danger")
            ]]),
        )

    elif data == "btn_removeuser_list":
        users = config.get("users", [])
        if not users:
            await query.edit_message_text(
                "<blockquote>ℹ️ No additional users to remove.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_users"),
            )
        else:
            await query.edit_message_text(
                "<blockquote>➖ <b>Remove User</b></blockquote>\n\nTap a user to remove:",
                parse_mode=ParseMode.HTML, reply_markup=remove_user_keyboard(),
            )

    elif data.startswith("btn_removeuser_"):
        target_id = int(data.split("_")[-1])
        users     = config.get("users", [])
        before    = len(users)
        config["users"] = [u for u in users if int(u["id"]) != target_id]
        save_config(config)
        if len(config["users"]) < before:
            await query.edit_message_text(
                f"<blockquote>✅ User <code>{target_id}</code> removed.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_users"),
            )
        else:
            await query.edit_message_text(
                "<blockquote>⚠️ User not found.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_users"),
            )

    # ════════════════ ACCOUNT MANAGEMENT ══════════════════

    elif data == "btn_accounts":
        await query.edit_message_text(
            build_account_list_msg(), parse_mode=ParseMode.HTML,
            reply_markup=accounts_keyboard(),
        )

    elif data == "btn_listaccounts":
        await query.edit_message_text(
            build_account_list_msg(), parse_mode=ParseMode.HTML,
            reply_markup=back_keyboard("btn_accounts"),
        )

    elif data == "btn_addaccount":
        runtime["pending"][uid] = "await_addaccount"
        await query.edit_message_text(
            "<blockquote>➕ <b>Add Account</b></blockquote>\n\n"
            "Send your INRFlash login details in this format:\n\n"
            "<b>With label:</b>\n"
            "<code>My Account | 9876543210 | yourpassword</code>\n\n"
            "<b>Without label:</b>\n"
            "<code>9876543210 | yourpassword</code>\n\n"
            "<i>The bot will log in immediately after saving and store the session token.\n"
            "It auto re-logs in whenever the session expires — no more manual cookies!</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖ Cancel", callback_data="btn_accounts", style="danger")
            ]]),
        )

    elif data == "btn_removeaccount_list":
        accounts = config.get("accounts", [])
        if not accounts:
            await query.edit_message_text(
                "<blockquote>ℹ️ No accounts to remove.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_accounts"),
            )
        else:
            await query.edit_message_text(
                "<blockquote>➖ <b>Remove Account</b></blockquote>\n\nTap an account to remove it:",
                parse_mode=ParseMode.HTML, reply_markup=remove_account_keyboard(),
            )

    elif data.startswith("btn_removeaccount_"):
        idx      = int(data.split("_")[-1])
        accounts = config.get("accounts", [])
        if 0 <= idx < len(accounts):
            removed_label = accounts[idx]["label"]
            config["accounts"] = [a for i, a in enumerate(accounts) if i != idx]
            ai = config.get("active_account_index", 0)
            if ai >= len(config["accounts"]):
                config["active_account_index"] = max(0, len(config["accounts"]) - 1)
            save_config(config)
            await query.edit_message_text(
                f"<blockquote>✅ Account <b>{escape(removed_label)}</b> removed.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_accounts"),
            )
        else:
            await query.edit_message_text(
                "<blockquote>⚠️ Account not found.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_accounts"),
            )

    elif data == "btn_loginall":
        accounts = config.get("accounts", [])
        if not accounts:
            await query.edit_message_text(
                "<blockquote>⚠️ No accounts configured.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_accounts"),
            )
            return
        await query.edit_message_text(
            f"<blockquote>🔄 <b>Logging in to {len(accounts)} account(s)…</b></blockquote>",
            parse_mode=ParseMode.HTML,
        )
        results = []
        for i, a in enumerate(accounts):
            success, msg = do_login(i)
            icon = "✅" if success else "❌"
            results.append(f"{icon} <b>{escape(a['label'])}</b> — <i>{escape(msg)}</i>")
        body = "\n".join(results)
        await query.edit_message_text(
            f"<blockquote>🔄 <b>Login Results</b></blockquote>\n\n{body}",
            parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_accounts"),
        )

    elif data == "btn_switchaccount":
        accounts = config.get("accounts", [])
        if not accounts:
            await query.edit_message_text(
                "<blockquote>⚠️ No accounts stored.</blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_accounts"),
            )
        else:
            await query.edit_message_text(
                "<blockquote>🔀 <b>Switch Active Account</b></blockquote>\n\nSelect which account to use:",
                parse_mode=ParseMode.HTML, reply_markup=switch_account_keyboard(),
            )

    elif data.startswith("btn_setactiveaccount_"):
        idx      = int(data.split("_")[-1])
        accounts = config.get("accounts", [])
        if 0 <= idx < len(accounts):
            config["active_account_index"] = idx
            save_config(config)
            a = accounts[idx]
            await query.edit_message_text(
                f"<blockquote>✅ <b>Active Account Switched</b>\n"
                f"Now using: <b>{escape(a['label'])}</b>\n"
                f"Mobile: <code>{escape(a.get('mobile','?'))}</code></blockquote>",
                parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_accounts"),
            )

    elif data == "btn_setinterval_help":
        runtime["pending"][uid] = "await_setinterval"
        await query.edit_message_text(
            f"<blockquote>⏱ <b>Set Check Interval</b></blockquote>\n\n"
            f"Current: <code>{config['interval']} min</code>\n\n"
            f"Send a number (minutes ≥ 1):\n"
            f"<code>1</code>  <code>5</code>  <code>10</code>  <code>30</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖ Cancel", callback_data="btn_settings", style="danger")
            ]]),
        )


# ═══════════════════════════════════════════════════════════
#  CORE MONITORING LOGIC
# ═══════════════════════════════════════════════════════════
async def _do_check(bot: Bot) -> Optional[bool]:
    if not config["monitoring"]:
        return False

    runtime["check_count"] += 1
    runtime["last_check"]  = _now()

    old_state = load_state()
    new_tasks = fetch_tasks()

    # ── Fetch error — try auto-login ──────────────────────
    if new_tasks is None:
        runtime["consecutive_failures"] += 1
        logger.warning(f"Fetch failed (streak: {runtime['consecutive_failures']}) — attempting auto re-login.")

        # Try re-login with active account
        acct_idx = config.get("active_account_index", 0)
        accounts = config.get("accounts", [])

        if accounts:
            success, login_msg = do_login(acct_idx)
            if success:
                logger.info("Auto re-login succeeded — retrying fetch.")
                new_tasks = fetch_tasks()
                if new_tasks is not None:
                    runtime["consecutive_failures"] = 0
                    # Fall through to normal diff logic below
                else:
                    logger.error("Fetch still failed after re-login.")
            else:
                logger.warning(f"Auto re-login failed: {login_msg}")
                # Mark expired and rotate
                if acct_idx < len(accounts):
                    accounts[acct_idx]["status"] = "expired"
                    config["accounts"] = accounts
                    save_config(config)
                rotated = rotate_to_next_account()
                if rotated:
                    new_acct_idx = config.get("active_account_index", 0)
                    s2, m2 = do_login(new_acct_idx)
                    if s2:
                        new_tasks = fetch_tasks()
                        if new_tasks is not None:
                            runtime["consecutive_failures"] = 0

        if new_tasks is None:
            if runtime["consecutive_failures"] >= 3:
                acct_info = f"<b>{escape(accounts[acct_idx]['label'])}</b>" if accounts else "no accounts"
                await bot.send_message(
                    chat_id=OWNER_ID,
                    text=(
                        "<blockquote>⚠️ <b>3 Consecutive Failures!</b></blockquote>\n\n"
                        "Auto re-login also failed. Possible causes:\n"
                        "<blockquote>🔑 Wrong credentials — check Settings → Accounts\n"
                        "🌐 Site is down\n"
                        "📶 Network issue</blockquote>\n\n"
                        f"Current account: {acct_info}"
                    ),
                    parse_mode=ParseMode.HTML,
                    reply_markup=back_keyboard("btn_accounts"),
                )
                runtime["consecutive_failures"] = 0
            return None

    runtime["consecutive_failures"] = 0

    # Mark active account as active on successful fetch
    acct_idx = config.get("active_account_index", 0)
    accounts = config.get("accounts", [])
    if accounts and acct_idx < len(accounts):
        accounts[acct_idx]["status"] = "active"
        config["accounts"] = accounts
        save_config(config)

    # ── First run ────────────────────────────────────────────
    if not old_state:
        save_state(new_tasks)
        logger.info(f"First run — saved {len(new_tasks)} task(s).")
        await bot.send_message(
            chat_id=OWNER_ID, text=build_startup_msg(new_tasks),
            parse_mode=ParseMode.HTML, disable_web_page_preview=True,
            reply_markup=main_menu_keyboard(True),
        )
        return False

    # ── Suspicious empty ─────────────────────────────────────
    if not new_tasks and old_state:
        logger.warning("Empty task list while state has tasks.")
        await bot.send_message(
            chat_id=OWNER_ID,
            text=(
                "<blockquote>⚠️ <b>Warning: Task List Empty!</b></blockquote>\n\n"
                f"Previously saw <b>{len(old_state)}</b> task(s), now 0.\n"
                "Session may have expired.\n<i>Old state preserved.</i>"
            ),
            parse_mode=ParseMode.HTML, reply_markup=back_keyboard("btn_accounts"),
        )
        return None

    # ── Diff and notify ──────────────────────────────────────
    added, removed, changed = compare_tasks(old_state, new_tasks)
    if added or removed or changed:
        alert_text = build_change_alert(added, removed, changed, new_tasks)
        for user_id in get_notify_ids():
            try:
                await bot.send_message(
                    chat_id=user_id, text=alert_text,
                    parse_mode=ParseMode.HTML, disable_web_page_preview=True,
                    reply_markup=main_menu_keyboard(is_owner(user_id)),
                )
            except Exception as e:
                logger.warning(f"Could not notify user {user_id}: {e}")
        save_state(new_tasks)
        logger.info(f"Changes — +{len(added)} | -{len(removed)} | ~{len(changed)}")
        return True

    logger.info("No task changes.")
    return False


async def monitor_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    await _do_check(context.bot)


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",       start_cmd))
    app.add_handler(CommandHandler("help",        start_cmd))
    app.add_handler(CommandHandler("tasks",       tasks_cmd))
    app.add_handler(CommandHandler("setinterval", setinterval_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_cmd))

    app.job_queue.run_repeating(
        monitor_job,
        interval=config["interval"] * 60,
        first=15,
        name=JOB_NAME,
    )

    logger.info(f"⚡ INRFlash Monitor started | interval={config['interval']}min | owner={OWNER_ID}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()