import os
import threading
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from flask import Flask, jsonify
from supabase import create_client, Client

# =======================
# ENV
# =======================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

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
# HELPERS
# =======================

def is_owner(uid: int):
    return uid == OWNER_ID

def emb(title, desc, color):
    return discord.Embed(
        title=title,
        description=desc,
        color=color,
        timestamp=datetime.utcnow()
    )

# =======================
# FLASK API
# =======================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Alive"

@app.route("/ping")
def ping():
    return jsonify({"status": "ok"})

@app.route("/check/<user_id>")
def check_access(user_id):
    now = datetime.utcnow()

    # Maintenance
    m = supabase.table("bot_settings").select("value").eq("key","maintenance").execute()
    if m.data and m.data[0]["value"] == "true":
        return jsonify({"allowed": False, "reason": "🛠 MAINTENANCE"})

    # Access system
    a = supabase.table("bot_settings").select("value").eq("key","access_enabled").execute()
    if a.data and a.data[0]["value"] == "true":
        r = supabase.table("access_users").select("user_id").eq("user_id", user_id).execute()
        if not r.data:
            return jsonify({"allowed": False, "reason": "🔐 NO ACCESS"})

    # Ban check
    ban = supabase.table("banned_users").select("*").eq("user_id", user_id).execute()
    if ban.data:
        b = ban.data[0]

        # Temp ban
        if b["is_temp"] and b["expires_at"]:
            exp = datetime.fromisoformat(b["expires_at"].replace("Z",""))
            if now < exp:
                mins = int((exp-now).total_seconds()/60)
                return jsonify({
                    "allowed": False,
                    "reason": f"⏱ TEMP BAN ({mins} min left)\n{b['reason']}"
                })

            # auto unban
            supabase.table("banned_users").delete().eq("user_id", user_id).execute()
            return jsonify({"allowed": True})

        # Perm ban
        return jsonify({
            "allowed": False,
            "reason": f"🔨 PERMANENT BAN\n{b['reason']}"
        })

    return jsonify({"allowed": True})

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# =======================
# DISCORD EVENTS
# =======================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot Ready")

# =======================
# BAN COMMANDS
# =======================

@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, user_id: str, reason: str):
    if not is_owner(interaction.user.id):
        return

    supabase.table("banned_users").upsert({
        "user_id": user_id,
        "reason": reason,
        "is_temp": False
    }).execute()

    await interaction.response.send_message(
        embed=emb("🔨 PERMANENT BAN", f"ID: `{user_id}`\n{reason}", 0xff0000)
    )

@bot.tree.command(name="tempban")
async def tempban(interaction: discord.Interaction, user_id: str, minutes: int, reason: str):
    if not is_owner(interaction.user.id):
        return

    expires = datetime.utcnow() + timedelta(minutes=minutes)

    supabase.table("banned_users").upsert({
        "user_id": user_id,
        "reason": reason,
        "is_temp": True,
        "expires_at": expires.isoformat()
    }).execute()

    await interaction.response.send_message(
        embed=emb("⏱ TEMP BAN", f"ID: `{user_id}`\n{minutes} min\n{reason}", 0xffa500)
    )

@bot.tree.command(name="unban")
async def unban(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction.user.id):
        return

    supabase.table("banned_users").delete().eq("user_id", user_id).execute()

    await interaction.response.send_message(
        embed=emb("✅ UNBANNED", f"ID `{user_id}` fully unbanned", 0x00ff00)
    )

@bot.tree.command(name="list")
async def list_ban(interaction: discord.Interaction):
    data = supabase.table("banned_users").select("*").execute().data
    if not data:
        return await interaction.response.send_message("No banned users")

    msg = ""
    for i,u in enumerate(data,1):
        t = "TEMP" if u["is_temp"] else "PERM"
        msg += f"{i}. `{u['user_id']}` [{t}] - {u['reason']}\n"

    await interaction.response.send_message(embed=emb("🚫 BANNED USERS", msg, 0xff5555))

# =======================
# ACCESS
# =======================

@bot.tree.command(name="access_add")
async def access_add(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction.user.id):
        return

    supabase.table("access_users").upsert({"user_id": user_id}).execute()
    await interaction.response.send_message(embed=emb("🔐 ACCESS ADDED", user_id, 0x00ff00))

@bot.tree.command(name="access_remove")
async def access_remove(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction.user.id):
        return

    supabase.table("access_users").delete().eq("user_id", user_id).execute()
    await interaction.response.send_message(embed=emb("🔐 ACCESS REMOVED", user_id, 0xff0000))

@bot.tree.command(name="access_list")
async def access_list(interaction: discord.Interaction):
    data = supabase.table("access_users").select("user_id").execute().data
    msg = "\n".join(f"`{u['user_id']}`" for u in data) or "No users"
    await interaction.response.send_message(embed=emb("🔐 ACCESS LIST", msg, 0x00ff00))

@bot.tree.command(name="access_toggle")
async def access_toggle(interaction: discord.Interaction, state: str):
    if not is_owner(interaction.user.id):
        return

    supabase.table("bot_settings").update({
        "value": "true" if state=="on" else "false"
    }).eq("key","access_enabled").execute()

    await interaction.response.send_message(embed=emb("🔐 ACCESS", state.upper(), 0x00ff00))

# =======================
# MAINTENANCE
# =======================

@bot.tree.command(name="maintenance")
async def maintenance(interaction: discord.Interaction, state: str):
    if not is_owner(interaction.user.id):
        return

    supabase.table("bot_settings").update({
        "value": "true" if state=="on" else "false"
    }).eq("key","maintenance").execute()

    await interaction.response.send_message(embed=emb("🛠 MAINTENANCE", state.upper(), 0xffaa00))

# =======================
# START
# =======================

threading.Thread(target=run_flask, daemon=True).start()
bot.run(DISCORD_TOKEN)
