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

    await i.response.send_message(embed=emb(
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

    await i.response.send_message(embed=emb(
        "⏱ TEMPBAN",
        f"ID: `{user_id}`\nUsername: `{u}`\nDisplay: `{d}`\nTime: `{minutes} min`\nReason: {reason}",
        0xffa500
    ))

@bot.tree.command(name="unban")
async def unban(i:discord.Interaction, user_id:str):
    if not owner(i): return

    supabase.table("bans").delete().eq("user_id", user_id).execute()

    await i.response.send_message(embed=emb(
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

    await i.response.send_message(embed=emb("🚫 BANNED USERS", txt or "None"))

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
        return await i.response.send_message(embed=emb(
            "🔐 ACCESS",
            f"Access `{mode.value.upper()}`"
        ))

    if mode.value=="add" and user_id:
        u,d=roblox_info(user_id)
        supabase.table("access_users").upsert({
            "user_id":user_id,"username":u,"display_name":d
        }).execute()
        return await i.response.send_message(embed=emb(
            "🔐 ACCESS ADD",
            f"{u} ({d}) added"
        ))

    if mode.value=="remove" and user_id:
        supabase.table("access_users").delete().eq("user_id",user_id).execute()
        return await i.response.send_message(embed=emb(
            "🔐 ACCESS REMOVE",
            f"{user_id} removed"
        ))

    if mode.value=="list":
        data=supabase.table("access_users").select("*").execute().data
        txt="\n".join(f"{x['username']} ({x['display_name']})" for x in data) or "None"
        return await i.response.send_message(embed=emb("🔐 ACCESS LIST",txt))

# ================== KICK ==================
@bot.tree.command(name="kick")
async def kick(i: discord.Interaction, user_id: str, reason: str = "No reason provided"):
    if not owner(i):
        return await i.response.send_message("❌ Only bot owner can use this command", ephemeral=True)

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

    await i.response.send_message(embed=emb(
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
    if not owner(i): return
    supabase.table("bot_settings").update(
        {"value":"true" if mode.value=="on" else "false"}
    ).eq("key","maintenance").execute()
    await i.response.send_message(embed=emb("🛠 MAINTENANCE", f"{mode.value.upper()}"))

# ================== WHOIS ==================
@bot.tree.command(name="whois")
async def whois(i: discord.Interaction, user_id: str):
    if not owner(i):
        return await i.response.send_message(embed=emb("❌ NO PERMISSION","Owner only command"))

    await i.response.defer()

    u,d = roblox_info(user_id)

    # Ban Check
    r = supabase.table("bans").select("*").eq("user_id", user_id).execute().data
    ban_status = "🟢 Not Banned"
    ban_reason = "—"

    if r:
        b = r[0]
        if b["perm"]:
            ban_status = "🔴 Permanent Ban"
            ban_reason = b["reason"]
        else:
            if time.time() < float(b["expire"]):
                mins = int((float(b["expire"]) - time.time()) / 60)
                ban_status = f"⏱ Temp Ban ({mins} min left)"
                ban_reason = b["reason"]

    # Access Check
    access_status = "❌ No Access"
    try:
        a = supabase.table("access_users").select("user_id").eq("user_id", user_id).execute()
        if a.data:
            access_status = "✅ Has Access"
    except:
        access_status = "⚠️ Access Check Failed"

    desc = (
        f"**Roblox ID:** `{user_id}`\n"
        f"**Username:** `{u}`\n"
        f"**Display Name:** `{d}`\n\n"
        f"**Ban Status:** {ban_status}\n"
        f"**Reason:** {ban_reason}\n\n"
        f"**Access:** {access_status}"
    )

    await i.followup.send(embed=emb("🔍 WHOIS RESULT", desc, 0x3498db))

# ================== STATS ==================
START_TIME = time.time()

@bot.tree.command(name="stats")
async def stats(i: discord.Interaction):
    if not owner(i):
        return await i.response.send_message(embed=emb("❌ NO PERMISSION","Owner only command"))

    data = supabase.table("bans").select("*").execute().data
    perm_bans = sum(1 for x in data if x["perm"])
    temp_bans = sum(1 for x in data if not x["perm"] and time.time() < float(x["expire"]))

    access_users = supabase.table("access_users").select("user_id").execute().data
    access_count = len(access_users)

    a = supabase.table("bot_settings").select("value").eq("key","access_enabled").execute().data
    access_status = "🟢 OFF (Everyone Allowed)"
    if a and a[0]["value"] == "true":
        access_status = "🔐 ON (Whitelist Enabled)"

    m = supabase.table("bot_settings").select("value").eq("key","maintenance").execute().data
    maintenance_status = "🟢 OFF"
    if m and m[0]["value"]=="true":
        maintenance_status = "🛠 ON (Auto Kick)"

    uptime = int(time.time() - START_TIME)
    hrs = uptime//3600
    mins = (uptime%3600)//60

    desc = (
        f"**🚫 Permanent Bans:** `{perm_bans}`\n"
        f"**⏱ Active Temp Bans:** `{temp_bans}`\n\n"
        f"**🔐 Access Users:** `{access_count}`\n"
        f"**Access System:** {access_status}\n\n"
        f"**Maintenance:** {maintenance_status}\n\n"
        f"**🤖 Bot Uptime:** `{hrs}h {mins}m`"
    )

    await i.response.send_message(embed=emb("📊 SYSTEM STATS", desc, 0x2ecc71))

# ================== OWNER CMD ==================
@bot.tree.command(name="owner")
@app_commands.choices(action=[
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="remove", value="remove"),
    app_commands.Choice(name="list", value="list"),
])
async def owner_cmd(i: discord.Interaction, action: app_commands.Choice[str], user_id: str=None):
    if i.user.id != OWNER_ID:
        return await i.response.send_message(embed=emb("❌ DENIED","Only MAIN owner can manage owners"))

    if action.value=="add" and user_id:
        supabase.table("bot_admins").upsert({"user_id":user_id}).execute()
        return await i.response.send_message(embed=emb("👑 OWNER ADDED",f"User `{user_id}` added",0x00ff00))

    if action.value=="remove" and user_id:
        supabase.table("bot_admins").delete().eq("user_id",user_id).execute()
        return await i.response.send_message(embed=emb("🗑 OWNER REMOVED",f"`{user_id}` removed",0xff0000))

    if action.value=="list":
        data = supabase.table("bot_admins").select("*").execute().data
        txt = f"**MAIN OWNER:** `{OWNER_ID}`\n\n**EXTRA OWNERS:**\n"
        txt += "\n".join(f"• `{x['user_id']}`" for x in data) or "None"
        return await i.response.send_message(embed=emb("👑 OWNER LIST",txt))

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

    if time.time() < float(b["expire"]):
        return "true"

    supabase.table("bans").delete().eq("user_id", uid).execute()
    return "false"

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
