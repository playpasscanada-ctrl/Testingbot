import os
import asyncio
import threading
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from flask import Flask, jsonify
from supabase import create_client, Client
import aiohttp

# =======================
# ENV
# =======================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

OWNER_ID_RAW = os.getenv("OWNER_ID")
if not OWNER_ID_RAW:
    raise Exception("OWNER_ID env variable missing")
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
# FLASK
# =======================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Alive"

@app.route("/ping")
def ping():
    return jsonify({"status": "alive", "time": datetime.utcnow().isoformat()})

@app.route("/check/<user_id>")
def check_user(user_id):
    # maintenance
    m = supabase.table("bot_settings").select("value").eq("key", "maintenance").execute()
    if m.data and m.data[0]["value"] == "true":
        return jsonify({"allowed": False, "reason": "MAINTENANCE"})

    # ban check
    ban = supabase.table("banned_users").select("*").eq("user_id", user_id).execute()
    if ban.data:
        expires = ban.data[0].get("expires_at")
        if expires:
            if datetime.utcnow() >= datetime.fromisoformat(expires):
                supabase.table("banned_users").delete().eq("user_id", user_id).execute()
            else:
                return jsonify({"allowed": False, "reason": "TEMPBAN"})
        else:
            return jsonify({"allowed": False, "reason": "PERMABAN"})

    # access enabled?
    a = supabase.table("bot_settings").select("value").eq("key", "access_enabled").execute()
    if a.data and a.data[0]["value"] == "false":
        return jsonify({"allowed": True})

    r = supabase.table("access_users").select("user_id").eq("user_id", user_id).execute()
    return jsonify({"allowed": bool(r.data)})

def run_flask():
    app.run(host="0.0.0.0", port=10000)

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
        await asyncio.sleep(300)

# =======================
# EVENTS
# =======================

@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.loop.create_task(keep_alive())
    print("Bot ready")

# =======================
# HELPERS
# =======================

def is_owner(uid):
    return uid == OWNER_ID

def embed(title, desc, color):
    return discord.Embed(
        title=title,
        description=desc,
        color=color,
        timestamp=datetime.utcnow()
    )

# =======================
# ACCESS
# =======================

@bot.tree.command(name="access_add")
async def access_add(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("Owner only", ephemeral=False)

    supabase.table("access_users").upsert({"user_id": user_id}).execute()
    await interaction.response.send_message(embed=embed("ACCESS ADDED", user_id, 0x00ff00))

@bot.tree.command(name="access_remove")
async def access_remove(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("Owner only", ephemeral=False)

    supabase.table("access_users").delete().eq("user_id", user_id).execute()
    await interaction.response.send_message(embed=embed("ACCESS REMOVED", user_id, 0xff0000))

@bot.tree.command(name="access_list")
async def access_list(interaction: discord.Interaction):
    data = supabase.table("access_users").select("*").execute().data
    msg = "\n".join(f"`{u['user_id']}`" for u in data) or "Empty"
    await interaction.response.send_message(embed=embed("ACCESS LIST", msg, 0x00ffff))

@bot.tree.command(name="access_toggle")
async def access_toggle(interaction: discord.Interaction, state: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("Owner only")

    val = "true" if state.lower() == "on" else "false"
    supabase.table("bot_settings").update({"value": val}).eq("key", "access_enabled").execute()
    await interaction.response.send_message(embed=embed("ACCESS", state.upper(), 0xffff00))

# =======================
# BAN / TEMPBAN / UNBAN
# =======================

@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, user_id: str, reason: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("Owner only")

    supabase.table("banned_users").upsert({
        "user_id": user_id,
        "reason": reason,
        "expires_at": None
    }).execute()

    await interaction.response.send_message(embed=embed("PERM BAN", f"{user_id}\n{reason}", 0xff0000))

@bot.tree.command(name="tempban")
async def tempban(interaction: discord.Interaction, user_id: str, minutes: int, reason: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("Owner only")

    expires = datetime.utcnow() + timedelta(minutes=minutes)
    supabase.table("banned_users").upsert({
        "user_id": user_id,
        "reason": reason,
        "expires_at": expires.isoformat()
    }).execute()

    await interaction.response.send_message(
        embed=embed("TEMP BAN", f"{user_id}\n{minutes} min\n{reason}", 0xff8800)
    )

@bot.tree.command(name="unban")
async def unban(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("Owner only")

    supabase.table("banned_users").delete().eq("user_id", user_id).execute()
    await interaction.response.send_message(embed=embed("UNBANNED", user_id, 0x00ff00))

@bot.tree.command(name="list")
async def ban_list(interaction: discord.Interaction):
    data = supabase.table("banned_users").select("*").execute().data
    if not data:
        return await interaction.response.send_message(embed=embed("BAN LIST", "Empty", 0x00ff00))

    msg = ""
    for u in data:
        msg += f"`{u['user_id']}` | {u['reason']}\n"
    await interaction.response.send_message(embed=embed("BAN LIST", msg, 0xff0000))

# =======================
# MAINTENANCE
# =======================

@bot.tree.command(name="maintenance")
async def maintenance(interaction: discord.Interaction, state: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("Owner only")

    val = "true" if state.lower() == "on" else "false"
    supabase.table("bot_settings").update({"value": val}).eq("key", "maintenance").execute()
    await interaction.response.send_message(embed=embed("MAINTENANCE", state.upper(), 0xffff00))

# =======================
# START
# =======================

threading.Thread(target=run_flask, daemon=True).start()
bot.run(DISCORD_TOKEN)
