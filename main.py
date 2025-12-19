import os, asyncio, threading, time
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from flask import Flask, jsonify
from supabase import create_client

# ================= ENV =================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RENDER_URL = os.getenv("RENDER_URL")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= DISCORD =================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def is_owner(i: discord.Interaction):
    return i.user.id == OWNER_ID

def embed(title, desc, color=0x00ff00):
    e = discord.Embed(title=title, description=desc, color=color)
    e.timestamp = datetime.utcnow()
    return e

# ================= FLASK =================
app = Flask(__name__)

@app.route("/")
def home():
    return "ALIVE"

@app.route("/check/<user_id>")
def roblox_check(user_id):
    now = datetime.utcnow()

    # TEMPBAN AUTO EXPIRE
    tb = supabase.table("temp_bans").select("*").eq("user_id", user_id).execute().data
    if tb and tb[0]["expires_at"]:
        if now >= datetime.fromisoformat(tb[0]["expires_at"]):
            supabase.table("temp_bans").delete().eq("user_id", user_id).execute()
        else:
            return jsonify({"allowed": False, "reason": "TEMPBAN"})

    # PERMA BAN
    if supabase.table("banned_users").select("user_id").eq("user_id", user_id).execute().data:
        return jsonify({"allowed": False, "reason": "BANNED"})

    # MAINTENANCE AUTO KICK
    m = supabase.table("bot_settings").select("value").eq("key", "maintenance").execute().data
    if m and m[0]["value"] == "true":
        supabase.table("kick_logs").insert({
            "user_id": user_id,
            "reason": "MAINTENANCE"
        }).execute()
        return jsonify({"allowed": False, "reason": "MAINTENANCE"})

    # ACCESS SYSTEM
    a = supabase.table("bot_settings").select("value").eq("key", "access_enabled").execute().data
    if a and a[0]["value"] == "true":
        if not supabase.table("access_users").select("user_id").eq("user_id", user_id).execute().data:
            return jsonify({"allowed": False, "reason": "NO ACCESS"})

    return jsonify({"allowed": True})

@app.route("/kickcheck/<user_id>")
def kickcheck(user_id):
    k = supabase.table("kick_logs").select("*").eq("user_id", user_id).execute().data
    if k:
        supabase.table("kick_logs").delete().eq("user_id", user_id).execute()
        return jsonify({"kick": True})
    return jsonify({"kick": False})

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# ================= EVENTS =================
@bot.event
async def on_ready():
    await bot.tree.sync()
    keep_alive.start()
    print("BOT READY")

# ================= AUTO PING =================
@tasks.loop(minutes=5)
async def keep_alive():
    import requests
    try:
        requests.get(RENDER_URL, timeout=10)
    except:
        pass

# ================= COMMANDS =================

@bot.tree.command(name="maintenance")
async def maintenance(i: discord.Interaction, state: str):
    if not is_owner(i): return
    supabase.table("bot_settings").update({"value": "true" if state=="on" else "false"}).eq("key","maintenance").execute()
    await i.response.send_message(embed("🛠 MAINTENANCE", state.upper()))

@bot.tree.command(name="access_toggle")
async def access_toggle(i: discord.Interaction, state: str):
    if not is_owner(i): return
    supabase.table("bot_settings").update({"value": "true" if state=="on" else "false"}).eq("key","access_enabled").execute()
    await i.response.send_message(embed("🔐 ACCESS", state.upper()))

@bot.tree.command(name="access_add")
async def access_add(i: discord.Interaction, user_id: str):
    if not is_owner(i): return
    supabase.table("access_users").upsert({"user_id":user_id}).execute()
    await i.response.send_message(embed("✅ ACCESS ADDED", user_id))

@bot.tree.command(name="access_remove")
async def access_remove(i: discord.Interaction, user_id: str):
    if not is_owner(i): return
    supabase.table("access_users").delete().eq("user_id",user_id).execute()
    await i.response.send_message(embed("❌ ACCESS REMOVED", user_id))

@bot.tree.command(name="ban")
async def ban(i: discord.Interaction, user_id: str, reason: str):
    if not is_owner(i): return
    supabase.table("banned_users").upsert({"user_id":user_id,"reason":reason}).execute()
    await i.response.send_message(embed("🔨 BANNED", f"{user_id}\n{reason}"))

@bot.tree.command(name="tempban")
async def tempban(i: discord.Interaction, user_id: str, minutes: int, reason: str):
    if not is_owner(i): return
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    supabase.table("temp_bans").upsert({
        "user_id":user_id,
        "reason":reason,
        "expires_at":expire.isoformat()
    }).execute()
    await i.response.send_message(embed("⏳ TEMPBAN", f"{user_id}\nExpires in {minutes} min"))

@bot.tree.command(name="unban")
async def unban(i: discord.Interaction, user_id: str):
    if not is_owner(i): return
    supabase.table("banned_users").delete().eq("user_id",user_id).execute()
    supabase.table("temp_bans").delete().eq("user_id",user_id).execute()
    await i.response.send_message(embed("✅ UNBANNED", user_id))

@bot.tree.command(name="kick")
async def kick(i: discord.Interaction, user_id: str, reason: str):
    if not is_owner(i): return
    supabase.table("kick_logs").insert({"user_id":user_id,"reason":reason}).execute()
    await i.response.send_message(embed("👢 KICKED", f"{user_id}\n{reason}"))

@bot.tree.command(name="list")
async def list_ban(i: discord.Interaction):
    data = supabase.table("banned_users").select("*").execute().data
    msg = "\n".join([f"{d['user_id']} | {d['reason']}" for d in data]) or "EMPTY"
    await i.response.send_message(embed("📃 BANNED LIST", msg))

# ================= START =================
threading.Thread(target=run_flask, daemon=True).start()
bot.run(DISCORD_TOKEN)
