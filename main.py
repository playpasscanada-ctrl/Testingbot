import os
import time
import asyncio
import threading
from datetime import datetime, timedelta

import requests
import discord
from discord import app_commands
from discord.ext import commands

from flask import Flask, jsonify
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
RENDER_URL = os.getenv("RENDER_URL")

# ================= FILES =================
MAINT_FILE = "maintenance.json"

def load(f):
    try:
        with open(f,"r") as file:
            return json.load(file)
    except:
        return {}

def save(f,d):
    with open(f,"w") as file:
        json.dump(d,file)

MAINT = load(MAINT_FILE) or {"enabled":False}
WAITING = {}

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
# FLASK (PING + ROBLOX API)
# =======================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Alive"

@app.route("/ping")
def ping():
    return jsonify({"status": "ok"})

@app.route("/maintenance")
def maintenance_check():
    return "true" if MAINT.get("enabled") else "false"

@app.route("/check/<user_id>")
def check_access(user_id):
    # maintenance
    m = supabase.table("bot_settings").select("value").eq("key", "maintenance").execute()
    if m.data and m.data[0]["value"] == "true":
        return jsonify({"allowed": False, "reason": "MAINTENANCE"})

    # tempban
    tb = supabase.table("temp_bans").select("*").eq("user_id", user_id).execute()
    if tb.data:
        return jsonify({"allowed": False, "reason": "TEMP_BANNED"})

    # perm ban
    b = supabase.table("banned_users").select("*").eq("user_id", user_id).execute()
    if b.data:
        return jsonify({"allowed": False, "reason": "BANNED"})

    # access toggle
    a = supabase.table("bot_settings").select("value").eq("key", "access_enabled").execute()
    if a.data and a.data[0]["value"] == "false":
        return jsonify({"allowed": True})

    # access list
    r = supabase.table("access_users").select("user_id").eq("user_id", user_id).execute()
    return jsonify({"allowed": bool(r.data)})

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# =======================
# HELPERS
# =======================

def is_owner(uid: int):
    return uid == OWNER_ID

def embed(title, desc, color=0x00ff00):
    e = discord.Embed(title=title, description=desc, color=color)
    e.timestamp = datetime.utcnow()
    return e

def parse_time(t: str):
    try:
        unit = t[-1]
        val = int(t[:-1])
        if unit == "m":
            return timedelta(minutes=val)
        if unit == "h":
            return timedelta(hours=val)
        if unit == "d":
            return timedelta(days=val)
    except:
        return None

def roblox_user(user_id: str):
    try:
        r = requests.get(f"https://users.roblox.com/v1/users/{user_id}", timeout=10)
        if r.status_code == 200:
            j = r.json()
            return j["name"], j["displayName"]
    except:
        pass
    return "Unknown", "Unknown"

# =======================
# AUTO UNBAN LOOP
# =======================

async def auto_unban():
    await bot.wait_until_ready()
    while True:
        now = datetime.utcnow().isoformat()
        data = supabase.table("temp_bans").select("*").lte("unban_at", now).execute().data
        for u in data:
            supabase.table("temp_bans").delete().eq("user_id", u["user_id"]).execute()
        await asyncio.sleep(60)

# =======================
# SELF PING (RENDER)
# =======================

def self_ping():
    while True:
        try:
            if RENDER_URL:
                requests.get(RENDER_URL, timeout=10)
        except:
            pass
        time.sleep(300)

# =======================
# EVENTS
# =======================

@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.loop.create_task(auto_unban())
    print("Bot Ready")

# =======================
# ACCESS COMMANDS
# =======================

@bot.tree.command(name="access_add")
async def access_add(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message(embed=embed("❌ ERROR", "Owner only", 0xff0000))

    username, display = roblox_user(user_id)
    supabase.table("access_users").upsert({
        "user_id": user_id,
        "username": username,
        "display_name": display
    }).execute()

    await interaction.response.send_message(
        embed=embed("🔐 ACCESS ADDED", f"{display} (@{username})\n`{user_id}`")
    )

@bot.tree.command(name="access_remove")
async def access_remove(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message(embed=embed("❌ ERROR", "Owner only", 0xff0000))

    supabase.table("access_users").delete().eq("user_id", user_id).execute()
    await interaction.response.send_message(embed=embed("🗑️ ACCESS REMOVED", f"`{user_id}`"))

@bot.tree.command(name="access_list")
async def access_list(interaction: discord.Interaction):
    data = supabase.table("access_users").select("*").execute().data
    if not data:
        return await interaction.response.send_message(embed=embed("ACCESS", "Empty"))

    msg = ""
    for u in data:
        msg += f"- `{u['user_id']}` | {u['username']} ({u['display_name']})\n"

    await interaction.response.send_message(embed=embed("🔐 ACCESS LIST", msg))

# =======================
# BAN / TEMPBAN / KICK
# =======================

@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, user_id: str, reason: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message(embed=embed("❌ ERROR", "Owner only", 0xff0000))

    username, display = roblox_user(user_id)
    supabase.table("banned_users").upsert({
        "user_id": user_id,
        "username": username,
        "display_name": display,
        "reason": reason
    }).execute()

    await interaction.response.send_message(embed=embed("🔨 BANNED", f"{display} (@{username})\n{reason}", 0xff0000))

@bot.tree.command(name="list")
async def list_banned(interaction: discord.Interaction):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message(embed=embed("❌ ERROR", "Owner only", 0xff0000))

    data_perm = supabase.table("banned_users").select("*").execute().data
    data_temp = supabase.table("temp_bans").select("*").execute().data

    if not data_perm and not data_temp:
        return await interaction.response.send_message(embed=embed("BANNED LIST", "No banned users"))

    msg = "**PERM BANNED USERS:**\n"
    for u in data_perm:
        msg += f"- `{u['user_id']}` | {u['username']} ({u['display_name']}) | {u['reason']}\n"

    msg += "\n**TEMP BANNED USERS:**\n"
    for u in data_temp:
        unban_time = u["unban_at"]
        msg += f"- `{u['user_id']}` | {u['username']} ({u['display_name']}) | {u['reason']} | Unban: {unban_time}\n"

    await interaction.response.send_message(embed=embed("BANNED USERS", msg))

@bot.tree.command(name="tempban")
async def tempban(interaction: discord.Interaction, user_id: str, time: str, reason: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message(embed=embed("❌ ERROR", "Owner only", 0xff0000))

    delta = parse_time(time)
    if not delta:
        return await interaction.response.send_message(embed=embed("❌ ERROR", "Invalid time", 0xff0000))

    username, display = roblox_user(user_id)
    now = datetime.utcnow()
    unban = now + delta

    supabase.table("temp_bans").upsert({
        "user_id": user_id,
        "username": username,
        "display_name": display,
        "reason": reason,
        "banned_at": now.isoformat(),
        "unban_at": unban.isoformat()
    }).execute()

    await interaction.response.send_message(
        embed=embed("⏱️ TEMPBAN",
        f"{display} (@{username})\nReason: {reason}\nUnban: <t:{int(unban.timestamp())}:F>",
        0xff9900)
    )

@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, user_id: str, reason: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message(embed=embed("❌ ERROR", "Owner only", 0xff0000))

    username, display = roblox_user(user_id)
    supabase.table("kick_logs").insert({
        "user_id": user_id,
        "username": username,
        "display_name": display,
        "reason": reason
    }).execute()

    await interaction.response.send_message(embed=embed("👢 KICKED", f"{display}\n{reason}", 0xff8800))

@bot.tree.command(name="maintenance")
async def maintenance(interaction: discord.Interaction, mode: str):
    if not owner(interaction):
        return await interaction.response.send_message("No permission")

    MAINT["enabled"]=(mode=="on")
    save(MAINT_FILE,MAINT)
    await interaction.response.send_message(
        embed=embed("🛠 MAINTENANCE",f"Status: `{mode.upper()}`",0xffaa00)
    )

# =======================
# START
# =======================

threading.Thread(target=run_flask, daemon=True).start()
threading.Thread(target=self_ping, daemon=True).start()
bot.run(DISCORD_TOKEN)
