import os
import asyncio
import threading
from datetime import datetime

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
    raise Exception("OWNER_ID env variable missing")
OWNER_ID = int(OWNER_ID_RAW)  # discord user id
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
# FLASK (PING + ROBLOX API)
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
    # maintenance check
    m = supabase.table("bot_settings").select("value").eq("key", "maintenance").execute()
    if m.data and m.data[0]["value"] == "true":
        return jsonify({"allowed": False, "reason": "MAINTENANCE"})

    # access enabled?
    a = supabase.table("bot_settings").select("value").eq("key", "access_enabled").execute()
    if a.data and a.data[0]["value"] == "false":
        return jsonify({"allowed": True})

    # check access list
    r = supabase.table("access_users").select("user_id").eq("user_id", user_id).execute()
    return jsonify({"allowed": bool(r.data)})

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# =======================
# EVENTS
# =======================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot ready")

# =======================
# HELPERS
# =======================

def is_owner(user_id: int):
    return user_id == OWNER_ID

# =======================
# ACCESS COMMANDS
# =======================

@bot.tree.command(name="access_add", description="Add user to access list")
@app_commands.describe(user_id="Roblox User ID", username="Username", display_name="Display Name")
async def access_add(interaction: discord.Interaction, user_id: str, username: str, display_name: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("❌ Owner only", ephemeral=False)

    supabase.table("access_users").upsert({
        "user_id": user_id,
        "username": username,
        "display_name": display_name
    }).execute()

    await interaction.response.send_message(
        f"✅ ACCESS ADDED\nUserID: `{user_id}`\nUsername: `{username}`\nDisplay: `{display_name}`",
        ephemeral=False
    )

@bot.tree.command(name="access_remove", description="Remove user from access list")
@app_commands.describe(user_id="Roblox User ID")
async def access_remove(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("❌ Owner only", ephemeral=False)

    supabase.table("access_users").delete().eq("user_id", user_id).execute()

    await interaction.response.send_message(
        f"🗑️ ACCESS REMOVED\nUserID: `{user_id}`",
        ephemeral=False
    )

@bot.tree.command(name="access_list", description="List all access users")
async def access_list(interaction: discord.Interaction):
    data = supabase.table("access_users").select("*").execute().data

    if not data:
        return await interaction.response.send_message("Access list empty", ephemeral=False)

    msg = "**ACCESS USERS:**\n"
    for u in data:
        msg += f"- `{u['user_id']}` | {u['username']} ({u['display_name']})\n"

    await interaction.response.send_message(msg, ephemeral=False)

# =======================
# BAN COMMANDS
# =======================

@bot.tree.command(name="ban", description="Ban a player")
@app_commands.describe(user_id="Roblox User ID", username="Username", display_name="Display Name", reason="Reason")
async def ban(interaction: discord.Interaction, user_id: str, username: str, display_name: str, reason: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("❌ Owner only", ephemeral=False)

    supabase.table("banned_users").upsert({
        "user_id": user_id,
        "username": username,
        "display_name": display_name,
        "reason": reason
    }).execute()

    await interaction.response.send_message(
        f"🔨 BANNED\n{username} ({display_name})\nReason: {reason}",
        ephemeral=False
    )

@bot.tree.command(name="unban", description="Unban a player")
@app_commands.describe(user_id="Roblox User ID")
async def unban(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("❌ Owner only", ephemeral=False)

    supabase.table("banned_users").delete().eq("user_id", user_id).execute()

    await interaction.response.send_message(
        f"✅ UNBANNED `{user_id}`",
        ephemeral=False
    )

@bot.tree.command(name="list", description="List all banned users")
async def ban_list(interaction: discord.Interaction):
    data = supabase.table("banned_users").select("*").execute().data

    if not data:
        return await interaction.response.send_message("No banned users", ephemeral=False)

    msg = "**BANNED USERS:**\n"
    for u in data:
        msg += f"- `{u['user_id']}` | {u['username']} ({u['display_name']}) | {u['reason']}\n"

    await interaction.response.send_message(msg, ephemeral=False)

# =======================
# KICK
# =======================

@bot.tree.command(name="kick", description="Kick a player")
@app_commands.describe(user_id="Roblox User ID", username="Username", display_name="Display Name", reason="Reason")
async def kick(interaction: discord.Interaction, user_id: str, username: str, display_name: str, reason: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("❌ Owner only", ephemeral=False)

    supabase.table("kick_logs").insert({
        "user_id": user_id,
        "username": username,
        "display_name": display_name,
        "reason": reason
    }).execute()

    await interaction.response.send_message(
        f"👢 KICKED\n{username} ({display_name})\nReason: {reason}",
        ephemeral=False
    )

# =======================
# SETTINGS
# =======================

@bot.tree.command(name="maintenance", description="Turn maintenance on/off")
@app_commands.describe(state="on or off")
async def maintenance(interaction: discord.Interaction, state: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("❌ Owner only", ephemeral=False)

    value = "true" if state.lower() == "on" else "false"
    supabase.table("bot_settings").update({"value": value}).eq("key", "maintenance").execute()

    await interaction.response.send_message(
        f"🛠️ Maintenance `{state.upper()}`",
        ephemeral=False
    )

@bot.tree.command(name="access_toggle", description="Enable/Disable access system")
@app_commands.describe(state="on or off")
async def access_toggle(interaction: discord.Interaction, state: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message("❌ Owner only", ephemeral=False)

    value = "true" if state.lower() == "on" else "false"
    supabase.table("bot_settings").update({"value": value}).eq("key", "access_enabled").execute()

    await interaction.response.send_message(
        f"🔐 Access system `{state.upper()}`",
        ephemeral=False
    )

# =======================
# START
# =======================

threading.Thread(target=run_flask, daemon=True).start()
bot.run(DISCORD_TOKEN)
