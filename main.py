import os, time, asyncio, threading, requests
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

OWNER_ID_RAW = os.getenv("OWNER_ID")
if not OWNER_ID_RAW:
    raise Exception("OWNER_ID missing")
OWNER_ID = int(OWNER_ID_RAW)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RENDER_URL = os.getenv("RENDER_URL")

# =======================
# SUPABASE
# =======================

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =======================
# DISCORD
# =======================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# =======================
# FLASK
# =======================

app = Flask(__name__)

@app.route("/ping")
def ping():
    return "pong"

@app.route("/check/<uid>")
def check(uid):
    # maintenance
    m = supabase.table("bot_settings").select("value").eq("key","maintenance").execute()
    if m.data and m.data[0]["value"] == "true":
        return jsonify({"allowed": False, "reason": "MAINTENANCE"})

    # temp ban
    if supabase.table("temp_bans").select("*").eq("user_id",uid).execute().data:
        return jsonify({"allowed": False, "reason": "TEMPBAN"})

    # perm ban
    if supabase.table("banned_users").select("*").eq("user_id",uid).execute().data:
        return jsonify({"allowed": False, "reason": "BAN"})

    # access toggle
    a = supabase.table("bot_settings").select("value").eq("key","access_enabled").execute()
    if a.data and a.data[0]["value"] == "false":
        return jsonify({"allowed": True})

    # access list
    ok = supabase.table("access_users").select("user_id").eq("user_id",uid).execute().data
    return jsonify({"allowed": bool(ok)})

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# =======================
# HELPERS
# =======================

def is_owner(uid): 
    return uid == OWNER_ID

def embed(title, desc, color=0x5865F2):
    e = discord.Embed(title=title, description=desc, color=color)
    e.timestamp = datetime.utcnow()
    return e

def roblox(uid):
    try:
        r = requests.get(f"https://users.roblox.com/v1/users/{uid}", timeout=5).json()
        return r.get("name","Unknown"), r.get("displayName","Unknown")
    except:
        return "Unknown","Unknown"

def parse_time(t):
    unit=t[-1]; val=int(t[:-1])
    if unit=="m": return timedelta(minutes=val)
    if unit=="h": return timedelta(hours=val)
    if unit=="d": return timedelta(days=val)

# =======================
# AUTO UNBAN
# =======================

async def auto_unban():
    await bot.wait_until_ready()
    while True:
        now = datetime.utcnow().isoformat()
        data = supabase.table("temp_bans").select("*").lte("unban_at",now).execute().data
        for u in data:
            supabase.table("temp_bans").delete().eq("user_id",u["user_id"]).execute()
        await asyncio.sleep(60)

# =======================
# SELF PING
# =======================

def self_ping():
    while True:
        try:
            if RENDER_URL:
                requests.get(RENDER_URL,timeout=10)
        except: pass
        time.sleep(300)

# =======================
# EVENTS
# =======================

@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.loop.create_task(auto_unban())
    print("Bot Online")

# =======================
# ACCESS COMMANDS
# =======================

@bot.tree.command(name="access_on")
async def access_on(i:discord.Interaction):
    if not is_owner(i.user.id): return
    supabase.table("bot_settings").update({"value":"true"}).eq("key","access_enabled").execute()
    await i.response.send_message(embed=embed("🔐 ACCESS","ON"))

@bot.tree.command(name="access_off")
async def access_off(i:discord.Interaction):
    if not is_owner(i.user.id): return
    supabase.table("bot_settings").update({"value":"false"}).eq("key","access_enabled").execute()
    await i.response.send_message(embed=embed("🔐 ACCESS","OFF"))

@bot.tree.command(name="access_add")
async def access_add(i:discord.Interaction, user_id:str):
    if not is_owner(i.user.id): return
    u,d = roblox(user_id)
    supabase.table("access_users").upsert({
        "user_id":user_id,"username":u,"display_name":d
    }).execute()
    await i.response.send_message(embed=embed("ACCESS ADDED",f"{d} (@{u})\n`{user_id}`"))

@bot.tree.command(name="access_remove")
async def access_remove(i:discord.Interaction, user_id:str):
    if not is_owner(i.user.id): return
    supabase.table("access_users").delete().eq("user_id",user_id).execute()
    await i.response.send_message(embed=embed("ACCESS REMOVED",f"`{user_id}`"))

@bot.tree.command(name="access_list")
async def access_list(i:discord.Interaction):
    data=supabase.table("access_users").select("*").execute().data
    txt="\n".join(f"{u['display_name']} (@{u['username']}) `{u['user_id']}`" for u in data) or "Empty"
    await i.response.send_message(embed=embed("ACCESS LIST",txt))

# =======================
# BAN / TEMPBAN / LIST
# =======================

@bot.tree.command(name="ban")
async def ban(i:discord.Interaction, user_id:str, reason:str):
    if not is_owner(i.user.id): return
    u,d=roblox(user_id)
    supabase.table("banned_users").upsert({
        "user_id":user_id,"username":u,"display_name":d,"reason":reason
    }).execute()
    await i.response.send_message(embed=embed("BANNED",f"{d} (@{u})\n{reason}",0xff0000))

@bot.tree.command(name="tempban")
async def tempban(i:discord.Interaction, user_id:str, time:str, reason:str):
    if not is_owner(i.user.id): return
    delta=parse_time(time)
    u,d=roblox(user_id)
    now=datetime.utcnow(); unban=now+delta
    supabase.table("temp_bans").upsert({
        "user_id":user_id,"username":u,"display_name":d,
        "reason":reason,"banned_at":now.isoformat(),"unban_at":unban.isoformat()
    }).execute()
    await i.response.send_message(embed=embed("TEMPBAN",f"{d}\nUnban <t:{int(unban.timestamp())}:F>",0xffaa00))

    @bot.tree.command(name="unban", description="Unban a player")
@app_commands.describe(user_id="Roblox User ID")
async def unban(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message(
            "❌ Owner only",
            ephemeral=False
        )

    supabase.table("banned_users").delete().eq("user_id", user_id).execute()

    await interaction.response.send_message(
        embed=discord.Embed(
            title="✅ UNBANNED",
            description=f"Player `{user_id}` has been unbanned",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        ),
        ephemeral=False
    )

@bot.tree.command(name="list")
async def listban(i:discord.Interaction):
    perm=supabase.table("banned_users").select("*").execute().data
    temp=supabase.table("temp_bans").select("*").execute().data
    txt="**PERM:**\n"
    for u in perm:
        txt+=f"{u['display_name']} `{u['user_id']}` {u['reason']}\n"
    txt+="\n**TEMP:**\n"
    for u in temp:
        txt+=f"{u['display_name']} `{u['user_id']}` until {u['unban_at']}\n"
    await i.response.send_message(embed=embed("BANNED LIST",txt or "None"))

# =======================
# MAINTENANCE
# =======================

@bot.tree.command(name="maintenance")
async def maintenance(i:discord.Interaction, mode:str):
    if not is_owner(i.user.id): return
    val="true" if mode=="on" else "false"
    supabase.table("bot_settings").update({"value":val}).eq("key","maintenance").execute()
    if mode=="on":
        users=supabase.table("access_users").select("*").execute().data
        for u in users:
            supabase.table("kick_logs").insert({
                "user_id":u["user_id"],"username":u["username"],
                "display_name":u["display_name"],"reason":"Maintenance"
            }).execute()
    await i.response.send_message(embed=embed("MAINTENANCE",mode.upper()))

# =======================
# START
# =======================

threading.Thread(target=run_flask,daemon=True).start()
threading.Thread(target=self_ping,daemon=True).start()
bot.run(DISCORD_TOKEN)
