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

# ================== FILE ==================
BAN_FILE = "bans.json"

def load_bans():
    if not os.path.exists(BAN_FILE):
        return {}
    with open(BAN_FILE, "r") as f:
        return json.load(f)

def save_bans(data):
    with open(BAN_FILE, "w") as f:
        json.dump(data, f, indent=2)

BANS = load_bans()

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
    return i.user.id == OWNER_ID

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
    BANS[user_id]={"perm":True,"reason":reason}
    save_bans(BANS)
    await i.response.send_message(embed=emb(
        "🔨 BANNED",
        f"ID: `{user_id}`\nUsername: `{u}`\nDisplay: `{d}`\nReason: {reason}",
        0xff0000
    ))

@bot.tree.command(name="tempban")
async def tempban(i:discord.Interaction, user_id:str, minutes:int, reason:str):
    if not owner(i): return
    u,d = roblox_info(user_id)
    BANS[user_id]={
        "perm":False,
        "reason":reason,
        "expire":time.time()+minutes*60
    }
    save_bans(BANS)
    await i.response.send_message(embed=emb(
        "⏱ TEMPBAN",
        f"ID: `{user_id}`\nUsername: `{u}`\nDisplay: `{d}`\nTime: `{minutes} min`\nReason: {reason}",
        0xffa500
    ))

@bot.tree.command(name="unban")
async def unban(i:discord.Interaction, user_id:str):
    if not owner(i): return
    BANS.pop(user_id,None)
    save_bans(BANS)
    await i.response.send_message(embed=emb(
        "✅ UNBANNED",
        f"User `{user_id}` removed from all bans",
        0x00ff00
    ))

@bot.tree.command(name="list")
async def listb(i:discord.Interaction):
    if not owner(i): return
    txt=""
    for uid,d in list(BANS.items()):
        if not d["perm"] and time.time()>d["expire"]:
            BANS.pop(uid)
            continue
        u,n=roblox_info(uid)
        t="PERM" if d["perm"] else f"{int((d['expire']-time.time())/60)}m"
        txt+=f"• `{uid}` | {u} ({n}) | {t}\n"
    save_bans(BANS)
    await i.response.send_message(embed=emb("🚫 BANNED USERS",txt or "None"))

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

@bot.tree.command(name="kick", description="Kick a Roblox player")
@app_commands.describe(
    user_id="Roblox User ID",
    reason="Kick reason"
)
async def kick(interaction: discord.Interaction, user_id: str, reason: str):
    if not is_owner(interaction.user.id):
        return await interaction.response.send_message(
            embed=make_embed("❌ NO PERMISSION", "Owner only command", 0xff0000)
        )

    # ---- Fetch Roblox username & display name ----
    try:
        r = requests.post(
            "https://users.roblox.com/v1/users",
            json={"userIds": [int(user_id)]},
            timeout=10
        )
        data = r.json()["data"][0]
        username = data["name"]
        display_name = data["displayName"]
    except Exception:
        username = "Unknown"
        display_name = "Unknown"

    # ---- Save kick log in Supabase ----
    supabase.table("kick_logs").insert({
        "user_id": user_id,
        "username": username,
        "display_name": display_name,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }).execute()

    # ---- Embed response ----
    embed = discord.Embed(
        title="👢 PLAYER KICKED",
        color=0xffa500,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="User ID", value=f"`{user_id}`", inline=False)
    embed.add_field(name="Username", value=username, inline=True)
    embed.add_field(name="Display Name", value=display_name, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)

    await interaction.response.send_message(embed=embed)

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
    await i.response.send_message(embed=emb(
        "🛠 MAINTENANCE",
        f"{mode.value.upper()}"
    ))

# ================== FLASK ==================
app = Flask(__name__)

@app.route("/ping")
def ping(): return "pong"

@app.route("/maintenance")
def mcheck():
    r=supabase.table("bot_settings").select("value").eq("key","maintenance").execute()
    return "true" if r.data[0]["value"]=="true" else "false"

@app.route("/access/<uid>")
def acheck(uid):
    r=supabase.table("bot_settings").select("value").eq("key","access_enabled").execute()
    if r.data[0]["value"]=="false": return "true"
    u=supabase.table("access_users").select("user_id").eq("user_id",uid).execute()
    return "true" if u.data else "false"

@app.route("/check/<uid>")
def bcheck(uid):
    d=BANS.get(uid)
    if not d: return "false"
    if d["perm"]: return "true"
    if time.time()<d["expire"]: return "true"
    BANS.pop(uid,None); save_bans(BANS)
    return "false"

# ================== KEEP ALIVE ==================
def keep_alive():
    while True:
        try:
            requests.get(f"{RENDER_URL}/ping",timeout=5)
        except: pass
        time.sleep(300)

threading.Thread(target=lambda:app.run("0.0.0.0",10000)).start()
threading.Thread(target=keep_alive,daemon=True).start()

bot.run(DISCORD_TOKEN)
