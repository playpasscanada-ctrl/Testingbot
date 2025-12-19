import os
import asyncio
import threading
import time
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from flask import Flask, jsonify
from supabase import create_client, Client
import aiohttp
import requests

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

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase env missing")

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
# FLASK
# =======================

app = Flask(__name__)

@app.route("/")
def home():
    return "OK"

@app.route("/ping")
def ping():
    return jsonify({"status": "alive", "time": datetime.utcnow().isoformat()})

@app.route("/check/<uid>")
def check(uid):
    # maintenance
    m = supabase.table("bot_settings").select("value").eq("key", "maintenance").execute()
    if m.data and m.data[0]["value"] == "true":
        return "false"

    # ban check (auto temp unban)
    b = supabase.table("banned_users").select("*").eq("user_id", uid).execute()
    if b.data:
        ban = b.data[0]
        if ban["temp"] and ban["expire_at"]:
            if datetime.utcnow() > datetime.fromisoformat(ban["expire_at"]):
                supabase.table("banned_users").delete().eq("user_id", uid).execute()
            else:
                return "true"
        else:
            return "true"

    # access
    a = supabase.table("bot_settings").select("value").eq("key", "access_enabled").execute()
    if a.data and a.data[0]["value"] == "false":
        return "false"

    r = supabase.table("access_users").select("user_id").eq("user_id", uid).execute()
    return "false" if not r.data else "true"

@app.route("/kickcheck/<uid>")
def kickcheck(uid):
    r = supabase.table("kick_logs").select("*").eq("user_id", uid).execute()
    if r.data:
        supabase.table("kick_logs").delete().eq("user_id", uid).execute()
        return "kick"
    return "ok"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# =======================
# HELPERS
# =======================

def is_owner(uid: int):
    return uid == OWNER_ID

def roblox_info(uid: str):
    try:
        r = requests.get(f"https://users.roblox.com/v1/users/{uid}", timeout=5).json()
        return r.get("name", "Unknown"), r.get("displayName", "Unknown")
    except:
        return "Unknown", "Unknown"

def embed(title, desc, color=0x5865F2):
    e = discord.Embed(
        title=title,
        description=desc,
        color=color,
        timestamp=datetime.utcnow()
    )
    e.set_footer(text="Ban System • Online")
    return e

# =======================
# KEEP ALIVE
# =======================

async def keep_alive():
    await bot.wait_until_ready()
    if not RENDER_URL:
        return
    while not bot.is_closed():
        try:
            async with aiohttp.ClientSession() as session:
                await session.get(RENDER_URL + "/ping")
        except:
            pass
        await asyncio.sleep(300)  # 5 min

# =======================
# EVENTS
# =======================

@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.loop.create_task(keep_alive())
    print("BOT READY")

# =======================
# ACCESS
# =======================

@bot.tree.command(name="access_add")
async def access_add(interaction: discord.Interaction, user_id: str):
    await interaction.response.defer()
    if not is_owner(interaction.user.id):
        return await interaction.followup.send("No permission")

    u, d = roblox_info(user_id)
    supabase.table("access_users").upsert({
        "user_id": user_id,
        "username": u,
        "display_name": d
    }).execute()

    await interaction.followup.send(
        embed=embed("🔐 ACCESS ADDED", f"{d} (@{u})\nID `{user_id}`", 0x00ff00)
    )

@bot.tree.command(name="access_remove")
async def access_remove(interaction: discord.Interaction, user_id: str):
    await interaction.response.defer()
    if not is_owner(interaction.user.id):
        return await interaction.followup.send("No permission")

    supabase.table("access_users").delete().eq("user_id", user_id).execute()
    await interaction.followup.send(
        embed=embed("🔐 ACCESS REMOVED", f"ID `{user_id}`", 0xff0000)
    )

@bot.tree.command(name="access_list")
async def access_list(interaction: discord.Interaction):
    await interaction.response.defer()
    data = supabase.table("access_users").select("*").execute().data
    if not data:
        return await interaction.followup.send(embed=embed("ACCESS", "Empty"))

    msg = ""
    for u in data:
        msg += f"`{u['user_id']}` {u['username']} ({u['display_name']})\n"

    await interaction.followup.send(embed=embed("ACCESS LIST", msg))

@bot.tree.command(name="access_toggle")
async def access_toggle(interaction: discord.Interaction, mode: str):
    await interaction.response.defer()
    if not is_owner(interaction.user.id):
        return await interaction.followup.send("No permission")

    supabase.table("bot_settings").update(
        {"value": "true" if mode == "on" else "false"}
    ).eq("key", "access_enabled").execute()

    await interaction.followup.send(
        embed=embed("ACCESS", f"Mode `{mode}`")
    )

# =======================
# BAN / TEMPBAN / UNBAN
# =======================

@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, user_id: str, reason: str):
    await interaction.response.defer()
    if not is_owner(interaction.user.id):
        return await interaction.followup.send("No permission")

    u, d = roblox_info(user_id)
    supabase.table("banned_users").upsert({
        "user_id": user_id,
        "username": u,
        "display_name": d,
        "reason": reason,
        "temp": False,
        "expire_at": None
    }).execute()

    await interaction.followup.send(
        embed=embed("🔨 BANNED", f"{d} (@{u})\n{reason}", 0xff0000)
    )

@bot.tree.command(name="tempban")
async def tempban(interaction: discord.Interaction, user_id: str, minutes: int, reason: str):
    await interaction.response.defer()
    if not is_owner(interaction.user.id):
        return await interaction.followup.send("No permission")

    u, d = roblox_info(user_id)
    expire = (datetime.utcnow() + timedelta(minutes=minutes)).isoformat()

    supabase.table("banned_users").upsert({
        "user_id": user_id,
        "username": u,
        "display_name": d,
        "reason": reason,
        "temp": True,
        "expire_at": expire
    }).execute()

    await interaction.followup.send(
        embed=embed("⏱ TEMP BAN", f"{d} (@{u})\n{minutes} min\n{reason}", 0xffa500)
    )

@bot.tree.command(name="unban")
async def unban(interaction: discord.Interaction, user_id: str):
    await interaction.response.defer()
    if not is_owner(interaction.user.id):
        return await interaction.followup.send("No permission")

    supabase.table("banned_users").delete().eq("user_id", user_id).execute()
    await interaction.followup.send(
        embed=embed("✅ UNBANNED", f"ID `{user_id}`", 0x00ff00)
    )

@bot.tree.command(name="list")
async def ban_list(interaction: discord.Interaction):
    await interaction.response.defer()
    data = supabase.table("banned_users").select("*").execute().data
    if not data:
        return await interaction.followup.send(embed=embed("BANS", "Empty"))

    msg = ""
    for b in data:
        t = "TEMP" if b["temp"] else "PERM"
        msg += f"`{b['user_id']}` {b['username']} ({t})\n{b['reason']}\n\n"

    await interaction.followup.send(embed=embed("BANNED USERS", msg))

# =======================
# KICK
# =======================

@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, user_id: str, reason: str):
    await interaction.response.defer()
    if not is_owner(interaction.user.id):
        return await interaction.followup.send("No permission")

    u, d = roblox_info(user_id)
    supabase.table("kick_logs").insert({
        "user_id": user_id,
        "username": u,
        "display_name": d,
        "reason": reason
    }).execute()

    await interaction.followup.send(
        embed=embed("👢 KICK", f"{d} (@{u})\n{reason}", 0xff5555)
    )

# =======================
# MAINTENANCE
# =======================

@bot.tree.command(name="maintenance")
async def maintenance(interaction: discord.Interaction, mode: str):
    await interaction.response.defer()
    if not is_owner(interaction.user.id):
        return await interaction.followup.send("No permission")

    supabase.table("bot_settings").update(
        {"value": "true" if mode == "on" else "false"}
    ).eq("key", "maintenance").execute()

    await interaction.followup.send(
        embed=embed("🛠 MAINTENANCE", f"Mode `{mode}`")
    )

# =======================
# START
# =======================

threading.Thread(target=run_flask, daemon=True).start()
bot.run(DISCORD_TOKEN)
