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

# ================== SETTINGS ==================
VERIFY_CHANNEL_ID = 123456789012345678      # <-- apna verify channel
LOG_CHANNEL_ID = 987654321098765432         # <-- apna logs channel

# ================== ROBLOX ==================
def roblox_info(uid):
    try:
        r = requests.get(f"https://users.roblox.com/v1/users/{uid}", timeout=5).json()
        return r.get("name","Unknown"), r.get("displayName","Unknown")
    except:
        return "Unknown","Unknown"

# ================== DISCORD ==================
intents = discord.Intents.default()
intents.message_content = True
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


# ================== VERIFY + AUTO WHITELIST + LOGS ==================
@bot.event
async def on_message(msg):

    if msg.author.bot:
        return

    if msg.channel.id != 1451973498200133786:
        return

    user_id = msg.content.strip()

    if not user_id.isdigit():
        await msg.delete()
        await msg.channel.send(
            f"{msg.author.mention} ❌ Sirf Roblox User ID bhejo!",
            delete_after=5
        )
        return

    try:
        data = requests.get(
            f"https://users.roblox.com/v1/users/{user_id}",
            timeout=5
        ).json()

        username = data.get("name","Unknown")
        display = data.get("displayName","Unknown")


        # =========================
        # ⚠️ BLACKLIST CHECK HERE
        # =========================
        try:
            blk = supabase.table("blacklist_users").select("user_id").eq("user_id", user_id).execute().data
            if blk:
                await msg.reply("🚫 You are blacklisted, verification denied.")
                return
        except:
            pass


        # =========================
        # AUTO ADD TO WHITELIST
        # =========================
        try:
            supabase.table("access_users").upsert({
                "user_id": user_id,
                "username": username,
                "display_name": display
            }).execute()
        except:
            pass

        # =========================
        # SAVE VERIFY LOG TO SUPABASE
        # =========================
        try:
            supabase.table("verify_logs").insert({
                "discord_id": str(msg.author.id),
                "roblox_id": user_id,
                "username": username,
                "display_name": display,
                "timestamp": datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            print("VERIFY LOG ERROR:", e)

        # USER REPLY
        embed = discord.Embed(
            title="✅ Verified & Whitelisted",
            color=0x2ecc71
        )
        embed.add_field(name="Roblox ID", value=f"`{user_id}`", inline=False)
        embed.add_field(name="Username", value=username, inline=True)
        embed.add_field(name="Display Name", value=display, inline=True)
        embed.set_footer(text="Access Granted")

        await msg.reply(embed=embed)

        # LOGS CHANNEL
        try:
            log_ch = bot.get_channel(1451973589342621791)
            if log_ch:
                log = discord.Embed(
                    title="📥 New Verification Logged",
                    color=0x3498db
                )
                log.add_field(name="Discord User", value=f"{msg.author.mention}", inline=False)
                log.add_field(name="Roblox ID", value=f"`{user_id}`", inline=False)
                log.add_field(name="Username", value=username, inline=True)
                log.add_field(name="Display Name", value=display, inline=True)
                log.timestamp = datetime.utcnow()

                await log_ch.send(embed=log)
        except:
            pass

    except:
        await msg.reply("❌ Invalid Roblox ID ya Roblox API down hai")


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
    if not owner(i):
        return

    # Roblox Info
    username, display = roblox_info(user_id)

    # Delete from bans
    supabase.table("bans").delete().eq("user_id", user_id).execute()

    # Response
    await safe_send(
        i,
        emb(
            "✅ USER UNBANNED",
            f"**Roblox ID:** `{user_id}`\n"
            f"**Username:** `{username}`\n"
            f"**Display Name:** `{display}`\n\n"
            f"🎉 Successfully **UNBANNED**",
            0x00ff00
        )
    )
    

from discord import ui

@bot.tree.command(name="banclear", description="Remove ALL banned users with confirmation")
async def banclear(i: discord.Interaction):

    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Only owners can do this"))

    class Confirm(ui.View):
        def __init__(self):
            super().__init__(timeout=30)

        @ui.button(label="YES - Clear All Bans", style=discord.ButtonStyle.danger)
        async def yes(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != i.user.id:
                return await interaction.response.send_message(
                    "❌ Ye confirmation tumhara nahi hai.", ephemeral=True
                )

            supabase.table("bans").delete().neq("user_id", "").execute()

            await interaction.response.edit_message(
                embed=emb(
                    "🚫 BAN RESET CONFIRMED",
                    "All bans successfully removed from system!",
                    0xff0000
                ),
                view=None
            )
            self.stop()

        @ui.button(label="NO - Cancel", style=discord.ButtonStyle.success)
        async def no(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != i.user.id:
                return await interaction.response.send_message(
                    "❌ Ye confirmation tumhara nahi hai.", ephemeral=True
                )

            await interaction.response.edit_message(
                embed=emb("❎ CANCELLED", "Ban reset cancelled.", 0x2ecc71),
                view=None
            )
            self.stop()

    view = Confirm()

    await i.response.send_message(
        embed=emb(
            "⚠️ CONFIRMATION REQUIRED",
            "Are you sure you want to **delete ALL banned users?**\nThis cannot be undone.",
            0xffaa00
        ),
        view=view
    )


@bot.tree.command(name="list")
async def listb(i:discord.Interaction):
    if not owner(i): 
        return
    
    data = supabase.table("bans").select("*").execute().data
    txt = ""
    now = time.time()

    for x in list(data):
        # Auto remove expired temp bans
        if not x["perm"] and x.get("expire") and now > float(x["expire"]):
            supabase.table("bans").delete().eq("user_id", x["user_id"]).execute()
            continue
        
        u, n = roblox_info(x["user_id"])

        # Ban Type & Time
        if x["perm"]:
            t = "PERM"
        else:
            t = f"{int((float(x['expire']) - now) / 60)}m"

        # Reason
        reason = x.get("reason", "No Reason")

        txt += f"• `{x['user_id']}` | {u} ({n}) | {t}\n   ➤ Reason: **{reason}**\n\n"

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
    if not owner(i): 
        return

    # ================== ACCESS ON / OFF ==================
    if mode.value in ["on","off"]:
        supabase.table("bot_settings").update(
            {"value":"true" if mode.value=="on" else "false"}
        ).eq("key","access_enabled").execute()

        return await safe_send(
            i,
            emb("🔐 ACCESS", f"Access `{mode.value.upper()}`")
        )

    # ================== ACCESS ADD ==================
    if mode.value=="add" and user_id:
        u, d = roblox_info(user_id)

        supabase.table("access_users").upsert({
            "user_id": user_id,
            "username": u,
            "display_name": d
        }).execute()

        return await safe_send(
            i,
            emb(
                "🔐 ACCESS GRANTED",
                f"**Roblox ID:** `{user_id}`\n"
                f"**Username:** `{u}`\n"
                f"**Display Name:** `{d}`\n\n"
                f"🎉 Successfully Added to Access List",
                0x2ecc71
            )
        )

    # ================== ACCESS REMOVE ==================
    if mode.value=="remove" and user_id:
        # Fetch info before deleting
        u, d = roblox_info(user_id)

        supabase.table("access_users").delete().eq("user_id", user_id).execute()

        return await safe_send(
            i,
            emb(
                "🔐 ACCESS REMOVED",
                f"**Roblox ID:** `{user_id}`\n"
                f"**Username:** `{u}`\n"
                f"**Display Name:** `{d}`\n\n"
                f"❌ Removed from Access List",
                0xff0000
            )
        )

    # ================== ACCESS LIST ==================
    if mode.value=="list":
        data = supabase.table("access_users").select("*").execute().data

        if not data:
            return await safe_send(i, emb("🔐 ACCESS LIST", "None"))

        txt = ""
        for x in data:
            txt += (
                f"• **Username:** {x['username']}\n"
                f"  Display: {x['display_name']}\n"
                f"  ID: `{x['user_id']}`\n\n"
            )

        return await safe_send(
            i,
            emb("🔐 ACCESS LIST", txt)
        )

from discord import ui

@bot.tree.command(name="accessclear", description="Remove ALL whitelisted users with confirmation")
async def accessclear(i: discord.Interaction):

    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Only owners can do this"))

    class Confirm(ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            self.value = None

        @ui.button(label="YES - Clear All", style=discord.ButtonStyle.danger)
        async def yes(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != i.user.id:
                return await interaction.response.send_message(
                    "❌ Ye confirmation tumhara nahi hai.", ephemeral=True
                )

            supabase.table("access_users").delete().neq("user_id", "").execute()

            await interaction.response.edit_message(
                embed=emb(
                    "🔐 ACCESS RESET CONFIRMED",
                    "All whitelisted users successfully removed!",
                    0xff0000
                ),
                view=None
            )
            self.value = True
            self.stop()

        @ui.button(label="NO - Cancel", style=discord.ButtonStyle.success)
        async def no(self, interaction: discord.Interaction, button: ui.Button):
            if interaction.user.id != i.user.id:
                return await interaction.response.send_message(
                    "❌ Ye confirmation tumhara nahi hai.", ephemeral=True
                )

            await interaction.response.edit_message(
                embed=emb("❎ CANCELLED", "Access reset cancelled.", 0x2ecc71),
                view=None
            )
            self.value = False
            self.stop()

    view = Confirm()
    await i.response.send_message(
        embed=emb(
            "⚠️ CONFIRMATION REQUIRED",
            "Are you sure you want to **delete ALL access whitelist users?**\nThis cannot be undone.",
            0xffaa00
        ),
        view=view
    )

@bot.tree.command(name="verifiedlist", description="Show all users who verified and their Roblox details")
async def verifiedlist(i: discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Owners only"))

    try:
        data = supabase.table("verify_logs") \
            .select("*") \
            .order("timestamp", desc=True) \
            .execute().data
    except:
        return await safe_send(i, emb("⚠️ ERROR", "Failed to fetch verification logs"))

    if not data:
        return await safe_send(i, emb("📭 EMPTY", "No one has verified yet"))

    text = ""
    for x in data:
        text += (
            f"👤 <@{x['discord_id']}>\n"
            f"🆔 Roblox ID: `{x['roblox_id']}`\n"
            f"🧑 Username: **{x['username']}**\n"
            f"✨ Display: {x['display_name']}\n"
            f"🕒 `{x['timestamp']}`\n"
            f"----------------------\n"
        )

    await safe_send(i, emb("📜 VERIFIED USERS LIST", text[:4000], 0x3498db))

@bot.tree.command(name="verifycheck", description="Check which Roblox IDs a Discord user verified")
async def verifycheck(i: discord.Interaction, discord_id: str):

    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Owners only"))

    try:
        data = supabase.table("verify_logs") \
            .select("*") \
            .eq("discord_id", discord_id) \
            .order("timestamp", desc=True) \
            .execute().data
    except:
        return await safe_send(i, emb("⚠️ ERROR", "Failed to fetch logs"))

    if not data:
        return await safe_send(
            i,
            emb("📭 NO DATA", f"No verification found for `{discord_id}`")
        )

    txt = f"👤 Discord User: <@{discord_id}>\n\n"

    for x in data:
        txt += (
            f"🆔 Roblox ID: `{x['roblox_id']}`\n"
            f"🧑 Username: **{x['username']}**\n"
            f"✨ Display: {x['display_name']}\n"
            f"🕒 `{x['timestamp']}`\n"
            f"----------------------\n"
        )

    await safe_send(i, emb("🔍 USER VERIFICATION HISTORY", txt[:4000], 0x9b59b6))

@bot.tree.command(name="blacklist", description="Manage verify blacklist")
@app_commands.choices(mode=[
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="remove", value="remove"),
    app_commands.Choice(name="list", value="list"),
])
async def blacklist(i: discord.Interaction, mode: app_commands.Choice[str], user_id: str = None):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Owner only command"))

    # =============================
    # ADD BLACKLIST + REMOVE ACCESS
    # =============================
    if mode.value == "add" and user_id:
        u, d = roblox_info(user_id)

        supabase.table("blacklist_users").upsert({
            "user_id": user_id
        }).execute()

        try:
            supabase.table("access_users").delete().eq("user_id", user_id).execute()
        except:
            pass

        return await safe_send(
            i,
            emb(
                "🚫 BLACKLISTED",
                f"**Roblox ID:** `{user_id}`\n"
                f"**Username:** `{u}`\n"
                f"**Display Name:** `{d}`\n\n"
                f"User successfully **Blacklisted & Removed From Whitelist**",
                0xff0000
            )
        )

    # =============================
    # REMOVE FROM BLACKLIST
    # =============================
    if mode.value == "remove" and user_id:
        u, d = roblox_info(user_id)

        supabase.table("blacklist_users").delete().eq("user_id", user_id).execute()

        return await safe_send(
            i,
            emb(
                "✅ BLACKLIST REMOVED",
                f"**Roblox ID:** `{user_id}`\n"
                f"**Username:** `{u}`\n"
                f"**Display Name:** `{d}`\n\n"
                f"User removed from blacklist",
                0x00ff00
            )
        )

    # =============================
    # LIST BLACKLIST
    # =============================
    if mode.value == "list":
        data = supabase.table("blacklist_users").select("user_id").execute().data

        if not data:
            return await safe_send(i, emb("📛 BLACKLISTED USERS", "None"))

        txt = ""
        for x in data:
            uid = x["user_id"]
            u, d = roblox_info(uid)

            txt += (
                f"• **Username:** {u}\n"
                f"  Display: {d}\n"
                f"  ID: `{uid}`\n\n"
            )

        return await safe_send(
            i,
            emb(
                "📛 BLACKLISTED USERS",
                txt,
                0xffaa00
            )
        )


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

    supabase.table("kick_flags").upsert({
        "user_id": user_id,
        "reason": reason
    }).execute()

    await safe_send(i, emb(
        "👢 PLAYER KICKED",
        f"**ID:** `{user_id}`\n**Username:** `{username}`\n**Display Name:** `{display}`\n**Reason:** {reason}",
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


# ================== WHOIS ==================
@bot.tree.command(name="whois")
async def whois(i: discord.Interaction, user_id: str):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION","Owner only"))

    try:
        await i.response.defer()

        # ROBLOX DATA
        u, d = roblox_info(user_id)
        if not u: u = "Unknown"
        if not d: d = "Unknown"

        # ===== BAN CHECK =====
        data = supabase.table("bans").select("*").eq("user_id", user_id).execute().data
        ban_status = "🟢 Not Banned"
        reason = "—"

        if data:
            b = data[0]
            if b.get("perm"):
                ban_status = "🔴 Permanent Ban"
                reason = b.get("reason","No Reason")
            else:
                if time.time() < float(b.get("expire",0)):
                    mins = int((float(b["expire"]) - time.time())/60)
                    ban_status = f"⏱ Temp Ban ({mins}m left)"
                    reason = b.get("reason","No Reason")

        # ===== ACCESS CHECK =====
        ac = supabase.table("access_users").select("user_id").eq("user_id",user_id).execute().data
        access = "✅ Whitelisted" if ac else "❌ Not Whitelisted"

        # ===== BLACKLIST CHECK =====
        blk = supabase.table("blacklist_users").select("user_id").eq("user_id", user_id).execute().data
        blacklist_status = "🚫 Blacklisted" if blk else "🟢 Not Blacklisted"

        desc = (
            f"**Roblox ID:** `{user_id}`\n"
            f"**Username:** `{u}`\n"
            f"**Display Name:** `{d}`\n\n"
            f"**Ban Status:** {ban_status}\n"
            f"**Reason:** {reason}\n\n"
            f"**Access:** {access}\n"
            f"**Blacklist:** {blacklist_status}"
        )

        await i.followup.send(embed=emb("🔍 WHOIS RESULT", desc, 0x3498db))

    except Exception as e:
        print("WHOIS ERROR:", e)
        try:
            await i.followup.send(embed=emb("❌ ERROR","Whois run karte time error aaya",0xff0000))
        except:
            pass

        
# ================== STATS ==================
START_TIME = time.time()

@bot.tree.command(name="stats")
async def stats(i: discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION","Owner only"))

    data = supabase.table("bans").select("*").execute().data
    perm = sum(1 for x in data if x["perm"])
    temp = sum(1 for x in data if not x["perm"] and time.time() < float(x["expire"]))

    access_users = len(supabase.table("access_users").select("user_id").execute().data)

    a = supabase.table("bot_settings").select("value").eq("key","access_enabled").execute().data
    access_status = "🟢 OFF (Everyone Allowed)"
    if a and a[0]["value"]=="true":
        access_status = "🔐 ON (Whitelist Enabled)"

    m = supabase.table("bot_settings").select("value").eq("key","maintenance").execute().data
    maintenance_status = "🟢 OFF"
    if m and m[0]["value"]=="true":
        maintenance_status = "🛠 ON"

    uptime = int(time.time() - START_TIME)
    hrs = uptime // 3600
    mins = (uptime % 3600)//60

    desc = (
        f"🚫 Permanent Bans: `{perm}`\n"
        f"⏱ Active TempBans: `{temp}`\n\n"
        f"🔐 Access Users: `{access_users}`\n"
        f"Access System: {access_status}\n\n"
        f"Maintenance: {maintenance_status}\n\n"
        f"🤖 Bot Uptime: `{hrs}h {mins}m`"
    )

    await safe_send(i, emb("📊 SYSTEM STATS", desc, 0x2ecc71))


# ================== OWNER ==================
@bot.tree.command(name="owner", description="Manage bot owners")
@app_commands.choices(action=[
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="remove", value="remove"),
    app_commands.Choice(name="list", value="list"),
])
async def owner_cmd(i: discord.Interaction, action: app_commands.Choice[str], user_id: str = None):

    if i.user.id != OWNER_ID:
        return await safe_send(i, emb("❌ DENIED", "Only MAIN owner can manage owners"))

    if action.value == "add" and user_id:
        supabase.table("bot_admins").upsert({
            "user_id": user_id
        }).execute()
        return await safe_send(i, emb("👑 OWNER ADDED", f"`{user_id}` is now owner", 0x00ff00))

    if action.value == "remove" and user_id:
        supabase.table("bot_admins").delete().eq("user_id", user_id).execute()
        return await safe_send(i, emb("🗑 OWNER REMOVED", f"`{user_id}` removed", 0xff0000))

    if action.value == "list":
        data = supabase.table("bot_admins").select("*").execute().data
        txt = f"**MAIN OWNER:** `{OWNER_ID}`\n\n**EXTRA OWNERS:**\n"
        txt += "\n".join(f"• `{x['user_id']}`" for x in data) or "None"
        return await safe_send(i, emb("👑 OWNER LIST", txt))


# ================== FLASK ==================
app = Flask(__name__)

@app.route("/ping")
def ping():
    return "pong"


@app.route("/maintenance")
def mcheck():
    try:
        r = supabase.table("bot_settings").select("value").eq("key","maintenance").execute()
        return "true" if r.data and r.data[0]["value"]=="true" else "false"
    except Exception as e:
        print("MAINT ERROR:", e)
        return "false"   # fail safe = don't kick


@app.route("/access/<uid>")
def acheck(uid):
    try:
        r = supabase.table("bot_settings").select("value").eq("key","access_enabled").execute()

        # Access system OFF = allow everyone
        if r.data and r.data[0]["value"]=="false":
            return "true"

        u = supabase.table("access_users").select("user_id").eq("user_id",uid).execute()
        return "true" if u.data else "false"

    except Exception as e:
        print("ACCESS ERROR:", e)
        return "true"   # fail safe whitelist if API down


@app.route("/check/<uid>")
def bcheck(uid):
    try:
        d = supabase.table("bans").select("*").eq("user_id", uid).execute().data
        if not d:
            return "false"

        b = d[0]

        if b["perm"]:
            return "true"

        if b["expire"] and time.time() < float(b["expire"]):
            return "true"

        supabase.table("bans").delete().eq("user_id", uid).execute()
        return "false"

    except Exception as e:
        print("BAN CHECK ERROR:", e)
        return "false"   # fail safe = no ban if DB fails


@app.route("/baninfo/<uid>")
def info(uid):
    try:
        r = supabase.table("bans").select("*").eq("user_id", uid).execute().data
        if not r:
            return jsonify({"ban": False})

        b = r[0]

        if b["perm"]:
            return jsonify({
                "ban": True,
                "perm": True,
                "reason": b.get("reason","No Reason")
            })

        left = int((float(b["expire"]) - time.time()) / 60)

        return jsonify({
            "ban": True,
            "perm": False,
            "reason": b.get("reason","No Reason"),
            "minutes": left
        })

    except Exception as e:
        print("BANINFO ERROR:", e)
        return jsonify({"ban": False})   # safe fallback


@app.route("/kickcheck/<uid>")
def kickcheck(uid):
    try:
        r = supabase.table("kick_flags").select("*").eq("user_id", uid).execute().data
        if not r:
            return jsonify({"kick": False})

        reason = r[0].get("reason","No Reason")

        supabase.table("kick_flags").delete().eq("user_id", uid).execute()

        return jsonify({"kick": True, "reason": reason})

    except Exception as e:
        print("KICKCHECK ERROR:", e)
        return jsonify({"kick": False})   # safe fallback

# ================== KEEP ALIVE ==================
def keep_alive():
    while True:
        try:
            requests.get(f"{RENDER_URL}/ping", timeout=5)
        except:
            pass
        time.sleep(25)

threading.Thread(target=lambda: app.run("0.0.0.0", 10000)).start()
threading.Thread(target=keep_alive, daemon=True).start()

bot.run(DISCORD_TOKEN)
