import os, time, threading, requests
from flask import Flask
import discord
from discord import app_commands
from supabase import create_client, Client

# ================= ENV =================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RENDER_URL = os.getenv("RENDER_URL")

OWNER_IDS = [int(x) for x in os.getenv("OWNER_IDS","").split(",") if x]

# ================= CLIENTS =================
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

# ================= HELPERS =================
def owner(i):
    return i.user.id in OWNER_IDS

def embed(t, d, c):
    return discord.Embed(title=t, description=d, color=c)

def roblox(uid):
    try:
        r = requests.get(f"https://users.roblox.com/v1/users/{uid}", timeout=5).json()
        return r.get("name","Unknown"), r.get("displayName","Unknown")
    except:
        return "Unknown","Unknown"

def get_config(key):
    r = supabase.table("config").select("value").eq("key", key).execute().data
    return r[0]["value"] if r else "off"

# ================= DISCORD =================
@bot.event
async def on_ready():
    await tree.sync()
    print("✅ Bot Online")

# ================= COMMANDS =================

@tree.command(name="ban")
async def ban(i: discord.Interaction, user_id: str, reason: str = "No reason"):
    if not owner(i):
        return await i.response.send_message("❌ No permission")

    await i.response.defer()
    u, d = roblox(user_id)

    supabase.table("bans").upsert({
        "user_id": user_id,
        "username": u,
        "display_name": d,
        "reason": reason
    }).execute()

    await i.followup.send(embed=embed(
        "⛔ PLAYER BANNED",
        f"Username: `{u}`\nDisplay Name: `{d}`\nID: `{user_id}`\nReason: `{reason}`",
        0xff0000
    ))

@tree.command(name="list")
async def list_bans(i: discord.Interaction):
    if not owner(i):
        return await i.response.send_message("❌ No permission")

    await i.response.defer()
    data = supabase.table("bans").select("*").execute().data

    if not data:
        return await i.followup.send("📭 No banned users")

    txt = ""
    for idx, b in enumerate(data, 1):
        txt += (
            f"**{idx}. {b['display_name']} (@{b['username']})**\n"
            f"ID: `{b['user_id']}`\n"
            f"Reason: `{b['reason']}`\n\n"
        )

    await i.followup.send(embed=embed("🚫 BANNED USERS", txt, 0xff0000))

@tree.command(name="kick")
async def kick(i: discord.Interaction, user_id: str, reason: str = "No reason"):
    if not owner(i):
        return await i.response.send_message("❌ No permission")

    await i.response.defer()
    u, d = roblox(user_id)

    supabase.table("kicks").upsert({
        "user_id": user_id,
        "username": u,
        "display_name": d,
        "reason": reason
    }).execute()

    await i.followup.send(embed=embed(
        "👢 PLAYER KICKED",
        f"Username: `{u}`\nDisplay Name: `{d}`\nID: `{user_id}`",
        0xff9900
    ))

@tree.command(name="access")
async def access(i: discord.Interaction, action: str, user_id: str = None):
    if not owner(i):
        return await i.response.send_message("❌ No permission")

    await i.response.defer()

    if action == "on":
        supabase.table("config").upsert({"key":"access","value":"on"}).execute()
        msg = "🔓 Access system ON"

    elif action == "off":
        supabase.table("config").upsert({"key":"access","value":"off"}).execute()
        msg = "🔒 Access system OFF"

    elif action == "add" and user_id:
        u, d = roblox(user_id)
        supabase.table("access").upsert({
            "user_id": user_id,
            "username": u,
            "display_name": d
        }).execute()
        msg = f"✅ Access added\n{d} (@{u})\nID: `{user_id}`"

    elif action == "remove" and user_id:
        supabase.table("access").delete().eq("user_id", user_id).execute()
        msg = f"❌ Access removed for `{user_id}`"

    elif action == "list":
        data = supabase.table("access").select("*").execute().data
        if not data:
            return await i.followup.send("🔐 No access users")

        txt = ""
        for idx, a in enumerate(data, 1):
            txt += (
                f"**{idx}. {a['display_name']} (@{a['username']})**\n"
                f"ID: `{a['user_id']}`\n\n"
            )

        return await i.followup.send(embed=embed("🔐 ACCESS LIST", txt, 0x00ff00))

    else:
        msg = "⚠️ Invalid action"

    await i.followup.send(embed=embed("🔐 ACCESS UPDATE", msg, 0x00ff00))

@tree.command(name="maintenance")
async def maintenance(i: discord.Interaction, mode: str):
    if not owner(i):
        return await i.response.send_message("❌ No permission")

    await i.response.defer()
    supabase.table("config").upsert({"key":"maintenance","value":mode}).execute()

    await i.followup.send(embed=embed(
        "🛠 MAINTENANCE",
        f"Status: `{mode.upper()}`",
        0xffff00
    ))

# ================= FLASK API (ROBLOX) =================

@app.route("/ping")
def ping():
    return "pong"

@app.route("/maintenance")
def maintenance_check():
    return "true" if get_config("maintenance") == "on" else "false"

@app.route("/access/<uid>")
def access_check(uid):
    if get_config("access") == "off":
        return "true"
    r = supabase.table("access").select("*").eq("user_id", uid).execute().data
    return "true" if r else "false"

@app.route("/check/<uid>")
def ban_check(uid):
    r = supabase.table("bans").select("*").eq("user_id", uid).execute().data
    return "true" if r else "false"

@app.route("/kick/<uid>")
def kick_check(uid):
    r = supabase.table("kicks").select("*").eq("user_id", uid).execute().data
    if r:
        supabase.table("kicks").delete().eq("user_id", uid).execute()
        return "kick"
    return "ok"

# ================= KEEP ALIVE =================
def keep_alive():
    while True:
        try:
            requests.get(f"{RENDER_URL}/ping", timeout=5)
        except:
            pass
        time.sleep(300)

threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()
threading.Thread(target=keep_alive, daemon=True).start()

bot.run(DISCORD_TOKEN)
