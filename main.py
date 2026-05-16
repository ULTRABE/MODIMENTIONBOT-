import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import psutil
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
LOG_DIR = DATA_DIR / "logs"
STATE_FILE = DATA_DIR / "state.json"

for p in (DATA_DIR, UPLOAD_DIR, LOG_DIR):
    p.mkdir(parents=True, exist_ok=True)

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_IDS = {int(x.strip()) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip()}
ADMIN_IDS = {int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()}
DEFAULT_PLAN = os.getenv("DEFAULT_PLAN", "free")
MAX_RAM_MB = int(os.getenv("MAX_RAM_MB", "1024"))

PLAN_LIMITS = {
    "free": int(os.getenv("PLAN_FREE_LIMIT", "1")),
    "plus": int(os.getenv("PLAN_PLUS_LIMIT", "3")),
    "pro": int(os.getenv("PLAN_PRO_LIMIT", "6")),
}

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise RuntimeError("Missing API_ID, API_HASH or BOT_TOKEN")

app = Client("private_hosting_bot", api_id=int(API_ID), api_hash=API_HASH, bot_token=BOT_TOKEN)

STATE: dict[str, Any] = {"jobs": {}, "plans": {}}


def load_state() -> None:
    global STATE
    if STATE_FILE.exists():
        try:
            STATE = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            STATE = {"jobs": {}, "plans": {}}
            save_state()
    else:
        save_state()


def save_state() -> None:
    STATE_FILE.write_text(json.dumps(STATE, indent=2), encoding="utf-8")


def is_admin(user_id: int) -> bool:
    return user_id in OWNER_IDS or user_id in ADMIN_IDS


def get_plan(user_id: int) -> str:
    if user_id in OWNER_IDS:
        return "owner"
    return STATE["plans"].get(str(user_id), DEFAULT_PLAN)


def user_limit(user_id: int) -> int:
    if user_id in OWNER_IDS:
        return 10**9
    return PLAN_LIMITS.get(get_plan(user_id), PLAN_LIMITS["free"])


def sanitize_name(name: str) -> str:
    return "".join(ch for ch in name if ch.isalnum() or ch in "._-")


def file_path(owner_id: int, file_name: str) -> Path:
    safe = sanitize_name(file_name)
    return UPLOAD_DIR / f"{owner_id}_{safe}"


def log_paths(job_id: str) -> tuple[Path, Path]:
    safe = job_id.replace(":", "_")
    return LOG_DIR / f"{safe}.out.log", LOG_DIR / f"{safe}.err.log"


def make_job_id(owner_id: int, file_name: str) -> str:
    return f"{owner_id}:{sanitize_name(file_name)}"


def is_running(pid: int | None) -> bool:
    if not pid:
        return False
    return psutil.pid_exists(pid)


def launch_cmd(language: str, path: Path) -> list[str]:
    if language == "python":
        return ["python3", str(path)]
    return ["node", f"--max-old-space-size={MAX_RAM_MB}", str(path)]


def stop_job(job_id: str) -> str:
    job = STATE["jobs"].get(job_id)
    if not job:
        return "missing"
    pid = job.get("pid")
    if not is_running(pid):
        job["status"] = "offline"
        job["pid"] = None
        save_state()
        return "already_offline"
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        time.sleep(1)
        if is_running(pid):
            os.killpg(os.getpgid(pid), signal.SIGKILL)
    except Exception:
        pass
    job["status"] = "offline"
    job["pid"] = None
    save_state()
    return "stopped"


def start_job(job_id: str) -> str:
    job = STATE["jobs"].get(job_id)
    if not job:
        return "missing"
    p = file_path(job["owner_id"], job["file_name"])
    if not p.exists():
        return "file_missing"
    if is_running(job.get("pid")):
        job["status"] = "online"
        return "already_running"

    out_log, err_log = log_paths(job_id)
    out_fp = open(out_log, "ab")
    err_fp = open(err_log, "ab")
    cmd = launch_cmd(job["language"], p)
    proc = subprocess.Popen(cmd, stdout=out_fp, stderr=err_fp, preexec_fn=os.setsid)
    job["pid"] = proc.pid
    job["status"] = "online"
    job["updated_at"] = int(time.time())
    save_state()
    return "started"


def refresh_status(job: dict[str, Any]) -> None:
    if job.get("status") == "online" and not is_running(job.get("pid")):
        job["status"] = "offline"
        job["pid"] = None


def job_card(job_id: str) -> str:
    job = STATE["jobs"][job_id]
    refresh_status(job)
    save_state()
    emoji = "🟢" if job["status"] == "online" else "🔴"
    return (
        f"{emoji} **{job['file_name']}**\n"
        f"🧠 Runtime: `{job['language']}`\n"
        f"📦 Plan: `{job['plan']}`\n"
        f"📶 Status: `{job['status']}`\n"
        f"🆔 PID: `{job.get('pid')}`\n"
        f"⏱ Updated: `{job.get('updated_at', job.get('created_at'))}`"
    )


def list_user_jobs(user_id: int) -> list[str]:
    if is_admin(user_id):
        return list(STATE["jobs"].keys())
    return [k for k, v in STATE["jobs"].items() if v["owner_id"] == user_id]


def parse_import_error(text: str) -> str | None:
    for line in text.splitlines()[-30:]:
        if "ModuleNotFoundError" in line or "Cannot find module" in line:
            return line.strip()
    return None


def tail_logs(job_id: str, limit: int = 25) -> str:
    out_log, err_log = log_paths(job_id)
    parts = []
    for path, tag in ((err_log, "ERR"), (out_log, "OUT")):
        if path.exists():
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit:]
            if lines:
                parts.append(f"[{tag}]\n" + "\n".join(lines))
    return "\n\n".join(parts)[:3500] or "No logs yet."


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Updates Channel", url="https://t.me")],
        [InlineKeyboardButton("📤 Upload File", callback_data="menu_upload"), InlineKeyboardButton("🗂 Check Files", callback_data="menu_files")],
        [InlineKeyboardButton("⚡ Bot Speed", callback_data="menu_speed"), InlineKeyboardButton("📊 Statistics", callback_data="menu_stats")],
        [InlineKeyboardButton("📞 Contact Owner", callback_data="menu_contact"), InlineKeyboardButton("🧩 Manual Install", callback_data="menu_install")],
        [InlineKeyboardButton("❓ Help", callback_data="menu_help")],
    ])


def file_menu(job_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Status", callback_data=f"status|{job_id}"), InlineKeyboardButton("📜 Logs", callback_data=f"logs|{job_id}")],
        [InlineKeyboardButton("🔄 Restart", callback_data=f"restart|{job_id}"), InlineKeyboardButton("⏸ Stop", callback_data=f"stop|{job_id}")],
        [InlineKeyboardButton("🗑 Delete", callback_data=f"delete|{job_id}")],
    ])


@app.on_message(filters.command("start") & filters.private)
async def start(_, m: Message):
    user = m.from_user
    uid = user.id
    plan = get_plan(uid)
    uploaded = len([x for x in STATE["jobs"].values() if x["owner_id"] == uid])
    limit = "∞" if uid in OWNER_IDS else str(user_limit(uid))

    text = (
        f"**Welcome, — {user.first_name}!**\n\n"
        f"👤 **User Information**\n"
        f"• Your User ID: `{uid}`\n"
        f"• Your Status: `{plan.title()} User`\n"
        f"• Files Uploaded: `{uploaded} / {limit}`\n\n"
        f"☁️ **Service Description**\n"
        f"• Host & run Python (.py) or JS (.js) scripts\n"
        f"• Upload single scripts\n"
        f"• Manual module installation guidance\n\n"
        f"🧭 **Usage Instruction**\n"
        f"Use buttons or type commands."
    )
    await m.reply(text, reply_markup=main_menu())


@app.on_message(filters.command("setplan") & filters.private)
async def setplan(_, m: Message):
    if not is_admin(m.from_user.id):
        return await m.reply("⛔ Admin only command.")
    parts = m.text.split()
    if len(parts) != 3 or parts[2] not in PLAN_LIMITS:
        return await m.reply("Usage: /setplan <user_id> <free|plus|pro>")
    STATE["plans"][parts[1]] = parts[2]
    save_state()
    await m.reply(f"✅ Plan set for `{parts[1]}` -> `{parts[2]}`")


@app.on_message(filters.command(["myfiles", "files"]) & filters.private)
async def myfiles(_, m: Message):
    jobs = list_user_jobs(m.from_user.id)
    if not jobs:
        return await m.reply("📭 No uploaded files yet.")
    for jid in jobs:
        await m.reply(job_card(jid), reply_markup=file_menu(jid))


@app.on_message(filters.private & filters.document)
async def upload(_, m: Message):
    user_id = m.from_user.id
    doc = m.document
    if not doc or not doc.file_name:
        return
    if not doc.file_name.endswith((".py", ".js")):
        return await m.reply("❌ Only `.py` and `.js` files are supported.")

    if len([j for j in STATE["jobs"].values() if j["owner_id"] == user_id]) >= user_limit(user_id):
        return await m.reply("🚫 Upload limit reached for your plan.")

    lang = "python" if doc.file_name.endswith(".py") else "node"
    safe_name = sanitize_name(doc.file_name)
    if not safe_name:
        return await m.reply("❌ Invalid filename.")

    path = file_path(user_id, safe_name)
    await m.download(file_name=str(path))
    job_id = make_job_id(user_id, safe_name)

    STATE["jobs"][job_id] = {
        "owner_id": user_id,
        "file_name": safe_name,
        "language": lang,
        "plan": get_plan(user_id),
        "status": "offline",
        "pid": None,
        "created_at": int(time.time()),
        "updated_at": int(time.time()),
    }
    save_state()

    result = start_job(job_id)
    await asyncio.sleep(2)
    refresh_status(STATE["jobs"][job_id])
    save_state()

    if STATE["jobs"][job_id]["status"] != "online":
        log = tail_logs(job_id, 20)
        module_hint = parse_import_error(log)
        stop_job(job_id)
        del STATE["jobs"][job_id]
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass
        save_state()
        msg = f"❌ Upload failed while starting `{safe_name}`.\n\n```\n{log}\n```"
        if module_hint:
            msg += f"\n\n💡 Possible dependency issue: `{module_hint}`"
        return await m.reply(msg)

    await m.reply(f"✅ Uploaded and running: `{safe_name}`", reply_markup=file_menu(job_id))


@app.on_callback_query()
async def callbacks(_, cq):
    data = cq.data
    uid = cq.from_user.id

    if data.startswith("menu_"):
        mapping = {
            "menu_upload": "📤 Send a `.py` or `.js` file directly in this chat.",
            "menu_files": "🗂 Use /myfiles to view and manage uploaded files.",
            "menu_speed": "⚡ Running on your VPS performance. Check process uptime/status in file cards.",
            "menu_stats": f"📊 Total files hosted: {len(STATE['jobs'])}",
            "menu_contact": "📞 Contact owner via your configured support channel.",
            "menu_install": "🧩 If module missing error appears, install dependencies on VPS and re-upload.",
            "menu_help": "❓ Commands: /start /myfiles /setplan",
        }
        return await cq.answer(mapping.get(data, "OK"), show_alert=True)

    if "|" not in data:
        return await cq.answer("Invalid action", show_alert=True)

    action, job_id = data.split("|", 1)
    if job_id not in STATE["jobs"]:
        return await cq.answer("Job not found", show_alert=True)

    job = STATE["jobs"][job_id]
    if uid != job["owner_id"] and not is_admin(uid):
        return await cq.answer("Not allowed", show_alert=True)

    if action == "status":
        await cq.message.edit_text(job_card(job_id), reply_markup=file_menu(job_id))
        return await cq.answer("Refreshed")

    if action == "logs":
        logs = tail_logs(job_id, 30)
        return await cq.answer("Latest logs sent") if await cq.message.reply(f"📜 Logs for `{job['file_name']}`\n```\n{logs}\n```") else None

    if action == "restart":
        stop_job(job_id)
        res = start_job(job_id)
        await cq.message.edit_text(job_card(job_id), reply_markup=file_menu(job_id))
        return await cq.answer(f"Restart: {res}")

    if action == "stop":
        res = stop_job(job_id)
        await cq.message.edit_text(job_card(job_id), reply_markup=file_menu(job_id))
        return await cq.answer(res)

    if action == "delete":
        stop_job(job_id)
        fp = file_path(job["owner_id"], job["file_name"])
        try:
            fp.unlink(missing_ok=True)
        except Exception:
            pass
        del STATE["jobs"][job_id]
        save_state()
        await cq.message.edit_text("🗑 File deleted.")
        return await cq.answer("Deleted")


if __name__ == "__main__":
    load_state()
    print("Bot starting...")
    app.run()
