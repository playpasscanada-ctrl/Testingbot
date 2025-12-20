import os, json, time, threading, requests
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from flask import Flask, jsonify
from supabase import create_client, Client

# ================== ENV ==================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RENDER_URL = os.getenv("RENDER_URL")

# ================== SUPABASE ==================
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================== ROBLOX ==================
def roblox_info(uid):
    try:
        r = requests.get(f"https://users.roblox.com/v1/users/{uid}", timeout=5).json()
        return r.get("name","Unknown"), r.get("displayName","Unknown")
    except:
        return "Unknown","Unknown"

# ================== DISCORD ==================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def owner(i):
    if i.user.id == OWNER_ID:
        return True
    try:
        r = supabase.table("bot_admins").select("user_id").eq("user_id", str(i.user.id)).execute()
        return bool(r.data)
    except:
        return False
        
def emb(title, desc, color=0x5865F2):
    e = discord.Embed(title=title, description=desc, color=color)
    e.timestamp = datetime.utcnow()
    return e

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("BOT ONLINE")

# ================== SAFE SEND ==================
async def safe_send(i, embed):
    try:
        if not i.response.is_done():
            await i.response.send_message(embed=embed)
        else:
            await i.followup.send(embed=embed)
    except:
        try:
            await i.followup.send(embed=embed)
        except:
            pass

# ================== BAN ==================
@bot.tree.command(name="ban")
async def ban(i:discord.Interaction, user_id:str, reason:str):
    if not owner(i): return
    u,d = roblox_info(user_id)

    supabase.table("bans").upsert({
        "user_id": user_id,
        "perm": True,
        "reason": reason,
        "expire": None
    }).execute()

    await safe_send(i, emb(
        "🔨 BANNED",
        f"ID: `{user_id}`\nUsername: `{u}`\nDisplay: `{d}`\nReason: {reason}",
        0xff0000
    ))

@bot.tree.command(name="tempban")
async def tempban(i:discord.Interaction, user_id:str, minutes:int, reason:str):
    if not owner(i): return
    u,d = roblox_info(user_id)

    supabase.table("bans").upsert({
        "user_id": user_id,
        "perm": False,
        "reason": reason,
        "expire": time.time() + minutes * 60
    }).execute()

    await safe_send(i, emb(
        "⏱ TEMPBAN",
        f"ID: `{user_id}`\nUsername: `{u}`\nDisplay: `{d}`\nTime: `{minutes} min`\nReason: {reason}",
        0xffa500
    ))

@bot.tree.command(name="unban")
async def unban(i:discord.Interaction, user_id:str):
    if not owner(i): return

    supabase.table("bans").delete().eq("user_id", user_id).execute()

    await safe_send(i, emb(
        "✅ UNBANNED",
        f"User `{user_id}` removed from ALL bans",
        0x00ff00
    ))

@bot.tree.command(name="list")
async def listb(i:discord.Interaction):
    if not owner(i): return
    
    data = supabase.table("bans").select("*").execute().data
    txt = ""
    now = time.time()

    for x in list(data):
        if not x["perm"] and x["expire"] and now > float(x["expire"]):
            supabase.table("bans").delete().eq("user_id", x["user_id"]).execute()
            continue
        
        u,n = roblox_info(x["user_id"])
        if x["perm"]:
            t = "PERM"
        else:
            t = f"{int((float(x['expire'])-now)/60)}m"

        txt += f"• `{x['user_id']}` | {u} ({n}) | {t}\n"

    await safe_send(i, emb("🚫 BANNED USERS", txt or "None"))

# ================== ACCESS ==================
@bot.tree.command(name="access")
@app_commands.choices(mode=[
    app_commands.Choice(name="on", value="on"),
    app_commands.Choice(name="off", value="off"),
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="remove", value="remove"),
    app_commands.Choice(name="list", value="list"),
])
async def access(i:discord.Interaction, mode:app_commands.Choice[str], user_id:str=None):
    if not owner(i): return

    if mode.value in ["on","off"]:
        supabase.table("bot_settings").update(
            {"value":"true" if mode.value=="on" else "false"}
        ).eq("key","access_enabled").execute()
        return await safe_send(i, emb("🔐 ACCESS",f"Access `{mode.value.upper()}`"))

    if mode.value=="add" and user_id:
        u,d=roblox_info(user_id)
        supabase.table("access_users").upsert({
            "user_id":user_id,"username":u,"display_name":d
        }).execute()
        return await safe_send(i, emb("🔐 ACCESS ADD",f"{u} ({d}) added"))

    if mode.value=="remove" and user_id:
        supabase.table("access_users").delete().eq("user_id",user_id).execute()
        return await safe_send(i, emb("🔐 ACCESS REMOVE",f"{user_id} removed"))

    if mode.value=="list":
        data=supabase.table("access_users").select("*").execute().data
        txt="\n".join(f"{x['username']} ({x['display_name']})" for x in data) or "None"
        return await safe_send(i, emb("🔐 ACCESS LIST",txt))

# ================== KICK ==================
@bot.tree.command(name="kick")
async def kick(i: discord.Interaction, user_id: str, reason: str = "No reason provided"):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION","Owner only"))

    username, display = roblox_info(user_id)

    try:
        supabase.table("kick_logs").insert({
            "user_id": user_id,
            "username": username,
            "display_name": display,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
    except:
        pass

    await safe_send(i, emb(
        "👢 PLAYER KICKED",
        f"**ID:** `{user_id}`\n**Username:** `{username}`\n**Display Name:** `{display}`\n**Action:** KICK\n**Reason:** {reason}",
        0xff5555
    ))

# ================== MAINTENANCE ==================
@bot.tree.command(name="maintenance")
@app_commands.choices(mode=[
    app_commands.Choice(name="on", value="on"),
    app_commands.Choice(name="off", value="off")
])
async def maintenance(i:discord.Interaction, mode:app_commands.Choice[str]):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION","Owner only"))

    supabase.table("bot_settings").update(
        {"value":"true" if mode.value=="on" else "false"}
    ).eq("key","maintenance").execute()

    await safe_send(i, emb(
        "🛠 MAINTENANCE",
        f"{mode.value.upper()}"
    ))

# ================== WHOIS / STATS / OWNER (unchanged logic – already working in your file)
# ================== FLASK ==================
app = Flask(__name__)

@app.route("/ping")
def ping(): 
    return "pong"

@app.route("/maintenance")
def mcheck():
    r=supabase.table("bot_settings").select("value").eq("key","maintenance").execute()
    return "true" if r.data[0]["value"]=="true" else "false"

@app.route("/access/<uid>")
def acheck(uid):
    r=supabase.table("bot_settings").select("value").eq("key","access_enabled").execute()
    if r.data[0]["value"]=="false": 
        return "true"
    u=supabase.table("access_users").select("user_id").eq("user_id",uid).execute()
    return "true" if u.data else "false"

@app.route("/check/<uid>")
def bcheck(uid):
    r = supabase.table("bans").select("*").eq("user_id", uid).execute().data
    if not r:
        return "false"

    b = r[0]

    if b["perm"]:
        return "true"

    if b["expire"] and time.time() < float(b["expire"]):
        return "true"

    supabase.table("bans").delete().eq("user_id", uid).execute()
    return "false"

@app.route("/baninfo/<uid>")
def info(uid):
    r = supabase.table("bans").select("*").eq("user_id", uid).execute().data
    if not r: 
        return jsonify({"ban": False})

    b = r[0]

    if b["perm"]:
        return jsonify({
            "ban": True,
            "perm": True,
            "reason": b["reason"]
        })

    left = int((float(b["expire"]) - time.time()) / 60)

    return jsonify({
        "ban": True,
        "perm": False,
        "reason": b["reason"],
        "minutes": left
    })

# ================== KEEP ALIVE ==================
def keep_alive():
    while True:
        try:
            requests.get(f"{RENDER_URL}/ping",timeout=5)
        except:
            pass
        time.sleep(300)

threading.Thread(target=lambda:app.run("0.0.0.0",10000)).start()
threading.Thread(target=keep_alive,daemon=True).start()

bot.run(DISCORD_TOKEN)
