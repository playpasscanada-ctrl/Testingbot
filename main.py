import os
import time
import threading
import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

from flask import Flask, jsonify
import requests

from supabase import create_client, Client

# =======================
# ENV
# =======================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

OWNER_ID_RAW = os.getenv("OWNER_ID")
if not OWNER_ID_RAW:
    raise Exception("OWNER_ID missing")
OWNER_ID = int(OWNER_ID_RAW)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

RENDER_URL = os.getenv("RENDER_URL")  # https://xxxx.onrender.com

# =======================
# SUPABASE
# =======================

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =======================
# DISCORD BOT
# =======================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# =======================
# EMBED HELPER
# =======================

def make_embed(title, desc, color=0x00ff00):
    e = discord.Embed(
        title=title,
        description=desc,
        color=color,
        timestamp=datetime.now(timezone.utc)
    )
    return e

async def safe_reply(interaction: discord.Interaction, embed):
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed)
    else:
        await interaction.response.send_message(embed=embed)

def is_owner(interaction: discord.Interaction):
    return interaction.user.id == OWNER_ID

# =======================
# FLASK API
# =======================

app = Flask(__name__)

@app.route("/")
def home():
    return "BOT ALIVE"

@app.route("/ping")
def ping():
    return jsonify({"status": "ok"})

@app.route("/check/<user_id>")
def check_user(user_id):
    # maintenance
    m = supabase.table("bot_settings").select("value").eq("key", "maintenance").execute()
    if m.data and m.data[0]["value"] == "true":
        return jsonify({"allowed": False, "reason": "MAINTENANCE"})

    # ban check
    b = supabase.table("banned_users").select("*").eq("user_id", user_id).execute()
    if b.data:
        return jsonify({"allowed": False, "reason": b.data[0]["reason"]})

    # access system
    a = supabase.table("bot_settings").select("value").eq("key", "access_enabled").execute()
    if a.data and a.data[0]["value"] == "true":
        r = supabase.table("access_users").select("user_id").eq("user_id", user_id).execute()
        if not r.data:
            return jsonify({"allowed": False, "reason": "NO ACCESS"})

    return jsonify({"allowed": True})

@app.route("/kickcheck/<user_id>")
def kick_check(user_id):
    r = supabase.table("kick_logs").select("*").eq("user_id", user_id).execute()
    if r.data:
        supabase.table("kick_logs").delete().eq("user_id", user_id).execute()
        return jsonify({"kick": True, "reason": r.data[0]["reason"]})
    return jsonify({"kick": False})

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# =======================
# BACKGROUND TASKS
# =======================

def auto_ping():
    while True:
        try:
            if RENDER_URL:
                requests.get(RENDER_URL + "/ping", timeout=10)
        except:
            pass
        time.sleep(300)  # 5 min

async def tempban_expiry_loop():
    while True:
        now = datetime.now(timezone.utc)
        data = supabase.table("banned_users").select("*").execute().data or []
        for u in data:
            if u.get("expires_at"):
                exp = datetime.fromisoformat(u["expires_at"])
                if now >= exp:
                    supabase.table("banned_users").delete().eq("user_id", u["user_id"]).execute()
        await asyncio.sleep(60)

# =======================
# EVENTS
# =======================

@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.loop.create_task(tempban_expiry_loop())
    print("BOT READY")

# =======================
# ACCESS COMMANDS
# =======================

@bot.tree.command(name="access_add")
async def access_add(i: discord.Interaction, user_id: str, username: str, display_name: str):
    if not is_owner(i):
        await safe_reply(i, make_embed("❌ OWNER ONLY", ""))
        return

    supabase.table("access_users").upsert({
        "user_id": user_id,
        "username": username,
        "display_name": display_name
    }).execute()

    await safe_reply(i, make_embed("🔐 ACCESS ADDED", f"{username} ({display_name})"))

@bot.tree.command(name="access_remove")
async def access_remove(i: discord.Interaction, user_id: str):
    if not is_owner(i):
        await safe_reply(i, make_embed("❌ OWNER ONLY", ""))
        return

    supabase.table("access_users").delete().eq("user_id", user_id).execute()
    await safe_reply(i, make_embed("🔐 ACCESS REMOVED", user_id))

@bot.tree.command(name="access_list")
async def access_list(i: discord.Interaction):
    data = supabase.table("access_users").select("*").execute().data or []
    if not data:
        await safe_reply(i, make_embed("ACCESS LIST", "Empty"))
        return

    msg = ""
    for u in data:
        msg += f"`{u['user_id']}` | {u['username']} ({u['display_name']})\n"

    await safe_reply(i, make_embed("ACCESS USERS", msg))

@bot.tree.command(name="access_toggle")
async def access_toggle(i: discord.Interaction, state: str):
    if not is_owner(i):
        await safe_reply(i, make_embed("❌ OWNER ONLY", ""))
        return

    val = "true" if state.lower() == "on" else "false"
    supabase.table("bot_settings").update({"value": val}).eq("key", "access_enabled").execute()
    await safe_reply(i, make_embed("ACCESS SYSTEM", val.upper()))

# =======================
# BAN / TEMPBAN / UNBAN
# =======================

@bot.tree.command(name="ban")
async def ban(i: discord.Interaction, user_id: str, reason: str):
    if not is_owner(i):
        await safe_reply(i, make_embed("❌ OWNER ONLY", ""))
        return

    supabase.table("banned_users").upsert({
        "user_id": user_id,
        "reason": reason,
        "expires_at": None
    }).execute()

    await safe_reply(i, make_embed("🔨 PERM BAN", f"{user_id}\n{reason}"))

@bot.tree.command(name="tempban")
async def tempban(i: discord.Interaction, user_id: str, minutes: int, reason: str):
    if not is_owner(i):
        await safe_reply(i, make_embed("❌ OWNER ONLY", ""))
        return

    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes)

    supabase.table("banned_users").upsert({
        "user_id": user_id,
        "reason": reason,
        "expires_at": exp.isoformat()
    }).execute()

    await safe_reply(i, make_embed("⏳ TEMP BAN", f"{user_id}\n{minutes} min\n{reason}"))

@bot.tree.command(name="unban")
async def unban(i: discord.Interaction, user_id: str):
    if not is_owner(i):
        await safe_reply(i, make_embed("❌ OWNER ONLY", ""))
        return

    supabase.table("banned_users").delete().eq("user_id", user_id).execute()
    await safe_reply(i, make_embed("✅ UNBANNED", user_id))

@bot.tree.command(name="list")
async def ban_list(i: discord.Interaction):
    data = supabase.table("banned_users").select("*").execute().data or []
    if not data:
        await safe_reply(i, make_embed("BAN LIST", "Empty"))
        return

    msg = ""
    for u in data:
        exp = u["expires_at"] or "PERMANENT"
        msg += f"`{u['user_id']}` | {u['reason']} | {exp}\n"

    await safe_reply(i, make_embed("BANNED USERS", msg))

# =======================
# KICK
# =======================

@bot.tree.command(name="kick")
async def kick(i: discord.Interaction, user_id: str, reason: str):
    if not is_owner(i):
        await safe_reply(i, make_embed("❌ OWNER ONLY", ""))
        return

    supabase.table("kick_logs").insert({
        "user_id": user_id,
        "reason": reason
    }).execute()

    await safe_reply(i, make_embed("👢 KICKED (ONE TIME)", f"{user_id}\n{reason}"))

# =======================
# MAINTENANCE
# =======================

@bot.tree.command(name="maintenance")
async def maintenance(i: discord.Interaction, state: str):
    if not is_owner(i):
        await safe_reply(i, make_embed("❌ OWNER ONLY", ""))
        return

    val = "true" if state.lower() == "on" else "false"
    supabase.table("bot_settings").update({"value": val}).eq("key", "maintenance").execute()

    await safe_reply(i, make_embed("🛠 MAINTENANCE", val.upper()))

# =======================
# START
# =======================

threading.Thread(target=run_flask, daemon=True).start()
threading.Thread(target=auto_ping, daemon=True).start()

bot.run(DISCORD_TOKEN)
