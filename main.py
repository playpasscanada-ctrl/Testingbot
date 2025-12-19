import os
import time
import threading
from datetime import datetime, timedelta

import requests
import discord
from discord import app_commands
from discord.ext import commands, tasks
from flask import Flask, jsonify
from supabase import create_client

# ================= ENV =================
TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RENDER_URL = os.getenv("RENDER_URL")

# ================= SUPABASE =================
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= DISCORD =================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= FLASK =================
app = Flask(__name__)

@app.route("/ping")
def ping():
    return "pong"

@app.route("/check/<uid>")
def check(uid):
    # maintenance
    m = sb.table("bot_settings").select("value").eq("key","maintenance_enabled").execute()
    if m.data and m.data[0]["value"] == "true":
        return jsonify({"allowed": False, "reason": "MAINTENANCE"})

    # perm ban
    if sb.table("banned_users").select("user_id").eq("user_id",uid).execute().data:
        return jsonify({"allowed": False, "reason": "BANNED"})

    # temp ban
    t = sb.table("temp_bans").select("*").eq("user_id",uid).execute().data
    if t:
        if datetime.fromisoformat(t[0]["expires_at"]) > datetime.utcnow():
            return jsonify({"allowed": False, "reason": "TEMPBANNED"})
        else:
            sb.table("temp_bans").delete().eq("user_id",uid).execute()

    # access
    a = sb.table("bot_settings").select("value").eq("key","access_enabled").execute()
    if a.data and a.data[0]["value"] == "true":
        if not sb.table("access_users").select("user_id").eq("user_id",uid).execute().data:
            return jsonify({"allowed": False, "reason": "NO_ACCESS"})

    return jsonify({"allowed": True})

def run_flask():
    app.run("0.0.0.0",10000)

# ================= HELPERS =================
def is_owner(i): return i.user.id == OWNER_ID

def roblox(uid):
    try:
        r = requests.get(f"https://users.roblox.com/v1/users/{uid}",timeout=10).json()
        return r["name"], r["displayName"]
    except:
        return "Unknown","Unknown"

def emb(title, desc, color=0x2f3136):
    e = discord.Embed(title=title, description=desc, color=color)
    e.timestamp = datetime.utcnow()
    return e

async def reply(i, embed):
    if i.response.is_done():
        await i.followup.send(embed=embed)
    else:
        await i.response.send_message(embed=embed)

# ================= PING =================
@tasks.loop(minutes=5)
async def keep_alive():
    try: requests.get(RENDER_URL,timeout=10)
    except: pass

# ================= TEMP CLEAN =================
@tasks.loop(minutes=1)
async def clean_temp():
    sb.table("temp_bans").delete().lte("expires_at", datetime.utcnow().isoformat()).execute()

# ================= READY =================
@bot.event
async def on_ready():
    await bot.tree.sync()
    keep_alive.start()
    clean_temp.start()
    print("BOT READY")

# ================= ACCESS GROUP =================
access = app_commands.Group(name="access", description="Access control")

@access.command(name="on")
async def access_on(i:discord.Interaction):
    if not is_owner(i): return
    sb.table("bot_settings").update({"value":"true"}).eq("key","access_enabled").execute()
    await reply(i, emb("ACCESS","Access ENABLED"))

@access.command(name="off")
async def access_off(i:discord.Interaction):
    if not is_owner(i): return
    sb.table("bot_settings").update({"value":"false"}).eq("key","access_enabled").execute()
    await reply(i, emb("ACCESS","Access DISABLED"))

@access.command(name="add")
async def access_add(i:discord.Interaction, user_id:str):
    if not is_owner(i): return
    u,d = roblox(user_id)
    sb.table("access_users").upsert({
        "user_id":user_id,"username":u,"display_name":d
    }).execute()
    await reply(i, emb("ACCESS ADD",f"ID: `{user_id}`\nUsername: `{u}`\nDisplay: `{d}`"))

@access.command(name="remove")
async def access_remove(i:discord.Interaction, user_id:str):
    if not is_owner(i): return
    sb.table("access_users").delete().eq("user_id",user_id).execute()
    await reply(i, emb("ACCESS REMOVE",f"ID: `{user_id}`"))

@access.command(name="list")
async def access_list(i:discord.Interaction):
    rows = sb.table("access_users").select("*").execute().data
    txt = "\n".join(f"`{r['user_id']}` | {r['username']} ({r['display_name']})" for r in rows) or "EMPTY"
    await reply(i, emb("ACCESS LIST",txt))

bot.tree.add_command(access)

# ================= MAINTENANCE =================
maint = app_commands.Group(name="maintenance", description="Maintenance")

@maint.command(name="on")
async def m_on(i:discord.Interaction):
    if not is_owner(i): return
    sb.table("bot_settings").update({"value":"true"}).eq("key","maintenance_enabled").execute()
    await reply(i, emb("MAINTENANCE","ON → ALL PLAYERS WILL BE KICKED"))

@maint.command(name="off")
async def m_off(i:discord.Interaction):
    if not is_owner(i): return
    sb.table("bot_settings").update({"value":"false"}).eq("key","maintenance_enabled").execute()
    await reply(i, emb("MAINTENANCE","OFF"))

bot.tree.add_command(maint)

# ================= BAN =================
@bot.tree.command(name="ban")
async def ban(i:discord.Interaction, user_id:str, reason:str):
    if not is_owner(i): return
    u,d = roblox(user_id)
    sb.table("banned_users").upsert({
        "user_id":user_id,"username":u,"reason":reason
    }).execute()
    await reply(i, emb("BANNED",f"ID:`{user_id}`\nUsername:`{u}`\nDisplay:`{d}`\nReason:{reason}",0xff0000))

@bot.tree.command(name="tempban")
async def tempban(i:discord.Interaction, user_id:str, minutes:int, reason:str):
    if not is_owner(i): return
    u,d = roblox(user_id)
    exp = datetime.utcnow()+timedelta(minutes=minutes)
    sb.table("temp_bans").upsert({
        "user_id":user_id,"username":u,"reason":reason,"expires_at":exp.isoformat()
    }).execute()
    await reply(i, emb("TEMP BAN",f"ID:`{user_id}`\nUsername:`{u}`\nTime:{minutes}m",0xffa500))

@bot.tree.command(name="unban")
async def unban(i:discord.Interaction, user_id:str):
    if not is_owner(i): return
    sb.table("banned_users").delete().eq("user_id",user_id).execute()
    sb.table("temp_bans").delete().eq("user_id",user_id).execute()
    await reply(i, emb("UNBAN",f"ID:`{user_id}`"))

@bot.tree.command(name="kick")
async def kick(i:discord.Interaction, user_id:str, reason:str):
    if not is_owner(i): return
    await reply(i, emb("KICK",f"ID:`{user_id}`\nReason:{reason}",0xff5555))

# ================= START =================
threading.Thread(target=run_flask,daemon=True).start()
bot.run(TOKEN)
