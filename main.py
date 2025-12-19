import os, time, threading, requests
from datetime import datetime
from flask import Flask
import discord
from discord import app_commands
from supabase import create_client

# ================= ENV =================
TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT", 8080))
OWNER_IDS = [int(x) for x in os.getenv("OWNER_IDS","").split(",") if x]
RENDER_URL = os.getenv("RENDER_URL")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

WAITING = {}

# ================= EMBED =================
def embed(title, desc, color=0x5865F2):
    e = discord.Embed(title=title, description=desc, color=color, timestamp=datetime.utcnow())
    e.set_footer(text="Ban System • Online")
    return e

# ================= ROBLOX =================
def roblox(uid):
    try:
        r = requests.get(f"https://users.roblox.com/v1/users/{uid}",timeout=5).json()
        return r.get("name","Unknown"), r.get("displayName","Unknown")
    except:
        return "Unknown","Unknown"

def owner(i): 
    return i.user.id in OWNER_IDS

def access_row():
    return supabase.table("access_control").select("*").eq("key","main").single().execute().data

# ================= DISCORD =================
class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = Bot()

@bot.event
async def on_ready():
    print("Bot Online")

# ================= BAN COMMANDS =================
@bot.tree.command(name="add")
async def add(interaction: discord.Interaction, user_id: str):
    if not owner(interaction): return
    WAITING[interaction.user.id]={"type":"perm","uid":user_id}
    u,d=roblox(user_id)
    await interaction.response.send_message(embed=embed(
        "🔨 PERMANENT BAN",
        f"{d} (@{u})\nID `{user_id}`\n✍️ Type reason",
        0xff0000))

@bot.tree.command(name="tempban")
async def tempban(interaction: discord.Interaction, user_id: str, minutes: int):
    if not owner(interaction): return
    WAITING[interaction.user.id]={"type":"temp","uid":user_id,"mins":minutes}
    u,d=roblox(user_id)
    await interaction.response.send_message(embed=embed(
        "⏱ TEMP BAN",
        f"{d} (@{u})\nID `{user_id}`\nTime `{minutes} min`\n✍️ Type reason",
        0xffa500))

@bot.tree.command(name="unban")
async def unban(interaction: discord.Interaction, user_id: str):
    if not owner(interaction): return
    supabase.table("blocked_users").delete().eq("user_id",user_id).execute()
    await interaction.response.send_message(embed=embed("✅ UNBANNED",user_id,0x00ff00))

@bot.tree.command(name="list")
async def listban(interaction: discord.Interaction):
    if not owner(interaction): return
    rows = supabase.table("blocked_users").select("*").execute().data
    if not rows:
        return await interaction.response.send_message(embed=embed("📭 No Bans","No users banned",0x00ff00))
    txt=""
    for i,r in enumerate(rows,1):
        u,n=roblox(r["user_id"])
        t="PERM" if r["perm"] else f"{int((r['expire']-time.time())/60)}m"
        txt+=f"**{i}. {n} (@{u})**\nID `{r['user_id']}` `{t}`\nReason: {r['reason']}\n\n"
    await interaction.response.send_message(embed=embed("🚫 Blocked Users",txt))

# ================= ACCESS =================
@bot.tree.command(name="access")
async def access(interaction: discord.Interaction, action: str, user_id: str=None):
    if not owner(interaction): return
    row=access_row()
    users=row["users"] or {}

    if action=="on": row["enabled"]=True
    elif action=="off": row["enabled"]=False
    elif action=="add" and user_id: users[user_id]=True
    elif action=="remove" and user_id: users.pop(user_id,None)
    elif action=="list":
        txt="\n".join(f"`{u}`" for u in users) or "No users"
        return await interaction.response.send_message(embed=embed("🔐 ACCESS LIST",txt,0x00ff00))

    supabase.table("access_control").update({
        "enabled": row["enabled"],
        "users": users
    }).eq("key","main").execute()

    await interaction.response.send_message(embed=embed("🔐 ACCESS UPDATED",action,0x00ff00))

@bot.tree.command(name="accessad")
async def accessad(interaction: discord.Interaction, user_id: str):
    if not owner(interaction): return
    row=access_row()
    users=row["users"] or {}
    row["enabled"]=True
    users[user_id]=True
    supabase.table("access_control").update({
        "enabled":True,"users":users
    }).eq("key","main").execute()
    await interaction.response.send_message(embed=embed("🔐 ACCESS GRANTED",user_id,0x00ff00))

@bot.tree.command(name="accesslist")
async def accesslist(interaction: discord.Interaction):
    if not owner(interaction): return
    users=access_row()["users"] or {}
    txt="\n".join(f"`{u}`" for u in users) or "No users"
    await interaction.response.send_message(embed=embed("🔐 ACCESS LIST",txt,0x00ff00))

@bot.tree.command(name="remove")
async def remove(interaction: discord.Interaction, user_id: str):
    if not owner(interaction): return
    row=access_row()
    users=row["users"] or {}
    if user_id in users:
        users.pop(user_id)
        supabase.table("access_control").update({"users":users}).eq("key","main").execute()
        await interaction.response.send_message(embed=embed("🔐 ACCESS REMOVED",user_id,0xff0000))
    else:
        await interaction.response.send_message(embed=embed("⚠️ NOT FOUND",user_id,0xffaa00))

# ================= KICK =================
@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, user_id: str):
    if not owner(interaction): return
    supabase.table("kicks").upsert({"user_id":user_id,"ts":time.time()}).execute()
    await interaction.response.send_message(embed=embed("🦵 KICK",user_id,0xff5555))

# ================= MAINTENANCE =================
@bot.tree.command(name="maintenance")
async def maintenance(interaction: discord.Interaction, mode: str):
    if not owner(interaction): return
    supabase.table("maintenance").update({
        "enabled":mode=="on"
    }).eq("key","main").execute()
    await interaction.response.send_message(embed=embed("🛠 MAINTENANCE",mode.upper(),0xffaa00))

# ================= MESSAGE (REASON) =================
@bot.event
async def on_message(msg):
    if msg.author.id not in WAITING: return
    d=WAITING.pop(msg.author.id)
    uid=d["uid"]

    if d["type"]=="perm":
        supabase.table("blocked_users").upsert({
            "user_id":uid,"perm":True,"reason":msg.content,"expire":None
        }).execute()
        title,color="✅ PERM BAN ADDED",0xff0000
    else:
        supabase.table("blocked_users").upsert({
            "user_id":uid,"perm":False,"reason":msg.content,
            "expire":time.time()+d["mins"]*60
        }).execute()
        title,color="✅ TEMP BAN ADDED",0xffa500

    await msg.channel.send(embed=embed(title,f"User `{uid}`\nReason: {msg.content}",color))

# ================= FLASK =================
app=Flask(__name__)

@app.route("/ping")
def ping(): return "pong"

@app.route("/maintenance")
def maint():
    r=supabase.table("maintenance").select("enabled").eq("key","main").single().execute().data
    return "true" if r["enabled"] else "false"

@app.route("/access/<uid>")
def access_check(uid):
    row=access_row()
    if not row["enabled"]: return "true"
    return "true" if uid in (row["users"] or {}) else "false"

@app.route("/kickcheck/<uid>")
def kick_check(uid):
    r=supabase.table("kicks").select("*").eq("user_id",uid).single().execute()
    if r.data:
        supabase.table("kicks").delete().eq("user_id",uid).execute()
        return "kick"
    return "ok"

@app.route("/check/<uid>")
def check(uid):
    r=supabase.table("blocked_users").select("*").eq("user_id",uid).single().execute()
    if not r.data: return "false"
    if r.data["perm"] or time.time() < (r.data["expire"] or 0): return "true"
    return "false"

@app.route("/reason/<uid>")
def reason(uid):
    r=supabase.table("blocked_users").select("reason").eq("user_id",uid).single().execute()
    return r.data["reason"] if r.data else ""

def run_flask():
    app.run(host="0.0.0.0",port=PORT)

threading.Thread(target=run_flask).start()
bot.run(TOKEN)
