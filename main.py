import os, json, time, threading, requests
from datetime import datetime

import discord
from discord import app_commands
from discord import ui   # ⬅️ ye add karo
from discord.ext import commands

from flask import Flask, jsonify
from supabase import create_client, Client

def log_action(action, user_id, username, display, executor):
    import time

    for _ in range(3):   # 3 baar try karega
        try:
            supabase.table("admin_logs").insert({
                "action": action,
                "user_id": user_id,
                "username": username,
                "display": display,
                "executor": str(executor),
                "timestamp": datetime.utcnow().isoformat()
            }).execute()

            print("LOG SAVED:", action, user_id)
            return
        
        except Exception as e:
            print("LOG ERROR:", e)
            time.sleep(0.8)   # Render ko thoda sa saans lene do 😭
    
    print("⚠️ Failed to save log after retries")

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
        # ✅ ALREADY VERIFIED CHECK
        # =========================
        try:
            exist = supabase.table("access_users").select("user_id").eq("user_id", user_id).execute().data
            if exist:
                return await msg.reply("✅ You are already verified & whitelisted.Abe bhosidiwale dobara kyu kr rha hai you motherfucker")
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
    if not owner(i): 
        return

    u, d = roblox_info(user_id)

    supabase.table("bans").upsert({
        "user_id": user_id,
        "perm": True,
        "reason": reason,
        "expire": None
    }).execute()

    # LOG ACTION HERE ✅
    try:
        log_action("ban", user_id, u, d, i.user.id)
    except:
        pass

    await safe_send(
        i,
        emb(
            "🔨 BANNED",
            f"ID: `{user_id}`\nUsername: `{u}`\nDisplay: `{d}`\nReason: {reason}",
            0xff0000
        )
    )

@bot.tree.command(name="tempban")
async def tempban(i:discord.Interaction, user_id:str, minutes:int, reason:str):
    if not owner(i): 
        return

    u, d = roblox_info(user_id)

    supabase.table("bans").upsert({
        "user_id": user_id,
        "perm": False,
        "reason": reason,
        "expire": time.time() + minutes * 60
    }).execute()

    # LOG ACTION HERE ✅
    try:
        log_action("tempban", user_id, u, d, i.user.id)
    except:
        pass

    await safe_send(
        i,
        emb(
            "⏱ TEMPBAN",
            f"ID: `{user_id}`\nUsername: `{u}`\nDisplay: `{d}`\nTime: `{minutes} min`\nReason: {reason}",
            0xffa500
        )
    )

@bot.tree.command(name="unban")
async def unban(i:discord.Interaction, user_id:str):
    if not owner(i):
        return

    # Roblox Info
    username, display = roblox_info(user_id)

    # Delete from bans
    supabase.table("bans").delete().eq("user_id", user_id).execute()

    # LOG ACTION HERE ✅ (inside function)
    try:
        log_action("unban", user_id, username, display, i.user.id)
    except:
        pass

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

        # LOG
        try:
            log_action(
                f"access_{mode.value}",
                "-",
                "-",
                "-",
                i.user.id
            )
        except:
            pass

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

        # LOG
        try:
            log_action(
                "access_add",
                user_id,
                u,
                d,
                i.user.id
            )
        except:
            pass

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
        u, d = roblox_info(user_id)

        supabase.table("access_users").delete().eq("user_id", user_id).execute()

        # LOG
        try:
            log_action(
                "access_remove",
                user_id,
                u,
                d,
                i.user.id
            )
        except:
            pass

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
        data = (
            supabase.table("verify_logs")
            .select("*")
            .order("timestamp", desc=True)
            .execute()
            .data
        )
    except:
        return await safe_send(i, emb("⚠️ ERROR", "Failed to fetch verification logs"))

    if not data:
        return await safe_send(i, emb("📭 EMPTY", "No one has verified yet"))

    seen = set()
    text = ""

    for x in data:
        rid = x["roblox_id"]
        if rid in seen:
            continue
        seen.add(rid)

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
        data = (
            supabase.table("verify_logs")
            .select("*")
            .eq("discord_id", discord_id)
            .order("timestamp", desc=True)
            .execute()
            .data
        )
    except:
        return await safe_send(i, emb("⚠️ ERROR", "Failed to fetch logs"))

    if not data:
        return await safe_send(
            i,
            emb("📭 NO DATA", f"No verification found for `{discord_id}`")
        )

    txt = f"👤 Discord User: <@{discord_id}>\n\n"
    seen = set()

    for x in data:
        rid = x["roblox_id"]
        if rid in seen:
            continue
        seen.add(rid)

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

        # 🔥 LOG ADDED HERE
        try:
            log_action("blacklist_add", user_id, u, d, i.user.id)
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

        # 🔥 LOG ADDED HERE
        try:
            log_action("blacklist_remove", user_id, u, d, i.user.id)
        except:
            pass

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

def safe_query(func):
    for _ in range(3):
        try:
            return func()
        except:
            time.sleep(0.5)
    return None


@bot.tree.command(name="stats")
async def stats(i: discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION","Owner only"))

    await i.response.defer()

    try:
        now = time.time()

        # ===== SINGLE SAFE CALLS =====
        bans = safe_query(lambda: supabase.table("bans").select("*").execute().data) or []
        access = safe_query(lambda: supabase.table("access_users").select("user_id").execute().data) or []
        blacklist = safe_query(lambda: supabase.table("blacklist_users").select("user_id").execute().data) or []
        logs = safe_query(lambda: supabase.table("verify_logs").select("*").execute().data) or []
        kicks = safe_query(lambda: supabase.table("kick_flags").select("*").execute().data) or []

        settings = safe_query(lambda: supabase.table("bot_settings").select("*").execute().data) or []

        # ===== BANS COUNT =====
        perm = sum(1 for x in bans if x["perm"])
        temp = sum(1 for x in bans if not x["perm"] and x["expire"] and now < float(x["expire"]))

        # ===== SETTINGS =====
        access_status = "🟢 OFF (Everyone Allowed)"
        maintenance_status = "🟢 OFF"

        for s in settings:
            if s["key"] == "access_enabled" and s["value"] == "true":
                access_status = "🔐 ON (Whitelist Enabled)"
            if s["key"] == "maintenance" and s["value"] == "true":
                maintenance_status = "🛠 ON"

        # ===== UPTIME =====
        uptime = int(time.time() - START_TIME)
        hrs = uptime // 3600
        mins = (uptime % 3600)//60

        desc = (
            f"🚫 Permanent Bans: `{perm}`\n"
            f"⏱ Active TempBans: `{temp}`\n"
            f"⛔ Blacklisted Users: `{len(blacklist)}`\n\n"

            f"🔐 Whitelisted Users: `{len(access)}`\n"
            f"🧾 Verified Logs: `{len(logs)}`\n"
            f"👨‍👩‍👧 Unique Verifiers: `{len(set(x['discord_id'] for x in logs))}`\n"
            f"🥾 Kick Flags Pending: `{len(kicks)}`\n\n"

            f"🔐 Access System: {access_status}\n"
            f"🛠 Maintenance: {maintenance_status}\n\n"

            f"🤖 Bot Uptime: `{hrs}h {mins}m`\n"
            f"🔌 System: 🟢 Stable & Optimized"
        )

        await i.followup.send(embed=emb("📊 SYSTEM STATS", desc, 0x2ecc71))

    except Exception as e:
        await i.followup.send(embed=emb("❌ ERROR", f"Stats failed:\n```{e}```", 0xff0000))
        
@bot.tree.command(
    name="altcheck",
    description="Check if a user is using multiple Roblox accounts (Support: Discord + Roblox)"
)
@app_commands.describe(
    discord_user="Discord user to check",
    roblox_user_id="Roblox User ID to check"
)
async def altcheck(
    i: discord.Interaction,
    discord_user: discord.User = None,
    roblox_user_id: str = None
):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION","Owner only"))

    await i.response.defer()

    # =========================
    # INVALID (Both Empty)
    # =========================
    if not discord_user and not roblox_user_id:
        return await safe_send(
            i,
            emb("❌ ALT CHECK FAILED", 
                "Please provide **Discord user OR Roblox User ID**",
                0xff0000)
        )

    # =========================
    # DISCORD USER MODE
    # =========================
    if discord_user:
        logs = supabase.table("verify_logs").select("*").eq(
            "discord_id", str(discord_user.id)
        ).execute().data

        if not logs:
            return await safe_send(
                i,
                emb("👤 ALT CHECK",
                    f"{discord_user.mention} ne abhi tak **kuch bhi verify nahi kiya**",
                    0xffff00
                )
            )

        unique = {}
        for x in logs:
            unique[x["roblox_id"]] = x

        count = len(unique)

        txt = "\n".join(
            f"• `{v['roblox_id']}` | **{v['username']}** ({v['display_name']})"
            for v in unique.values()
        )

        status = "🟢 Clean — No ALT Found"
        color = 0x2ecc71

        if count >= 2:
            status = f"🔴 ALT Detected — `{count}` Accounts Linked"
            color = 0xff0000

        desc = (
            f"**Discord:** {discord_user.mention}\n"
            f"**Linked Accounts:** `{count}`\n"
            f"**Status:** {status}\n\n"
            f"{txt}"
        )

        return await safe_send(i, emb("🕵 ALT ACCOUNT CHECK", desc, color))

    # =========================
    # ROBLOX USER MODE
    # =========================
    if roblox_user_id:

        logs = supabase.table("verify_logs").select("*").eq(
            "roblox_id", roblox_user_id
        ).execute().data

        if not logs:
            return await safe_send(
                i,
                emb("👤 ALT CHECK",
                    f"Roblox ID `{roblox_user_id}` ne abhi verify nahi kiya",
                    0xffff00
                )
            )

        user = logs[0]
        discord_ids = list({x["discord_id"] for x in logs})

        status = "🟢 Clean — No Suspicious Activity"
        color = 0x2ecc71

        if len(discord_ids) >= 2:
            status = f"🔴 Suspicious — `{len(discord_ids)}` Discord Accounts linked"
            color = 0xff0000

        desc = (
            f"**Roblox ID:** `{roblox_user_id}`\n"
            f"**Username:** `{user['username']}`\n"
            f"**Display Name:** `{user['display_name']}`\n\n"
            f"**Linked Discord Accounts:** `{len(discord_ids)}`\n"
            f"**Status:** {status}"
        )

        return await safe_send(i, emb("🕵 ALT ACCOUNT CHECK", desc, color))

@bot.tree.command(name="verifyhistory", description="Show global verification logs")
async def verifyhistory(i: discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION","Owner Only"))

    await i.response.defer()

    logs = supabase.table("verify_logs").select("*").order("timestamp", desc=True).execute().data
    
    if not logs:
        return await i.followup.send(embed=emb("📭 EMPTY","No one has verified yet"))

    pages = []
    page = []

    for x in logs:
        t = x.get("timestamp","").replace("T"," ").split(".")[0]
        page.append(
            f"📌 **{x['username']}** ({x['display_name']})\n"
            f"🆔 `{x['roblox_id']}` — <@{x['discord_id']}> — `{t}`\n"
        )

        if len(page) == 10:
            pages.append("\n".join(page))
            page = []

    if page:
        pages.append("\n".join(page))

    class Pager(ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.index = 0
        
        async def update(self, interaction):
            embed = emb(
                f"📜 VERIFICATION HISTORY ({self.index+1}/{len(pages)})",
                pages[self.index],
                0x3498db
            )
            await interaction.response.edit_message(embed=embed, view=self)

        @ui.button(label="⬅️ Back", style=discord.ButtonStyle.secondary)
        async def back(self, interaction, btn):
            if self.index > 0:
                self.index -= 1
            await self.update(interaction)

        @ui.button(label="➡️ Next", style=discord.ButtonStyle.primary)
        async def next(self, interaction, btn):
            if self.index < len(pages)-1:
                self.index += 1
            await self.update(interaction)

    view = Pager()
    await i.followup.send(
        embed=emb(f"📜 VERIFICATION HISTORY (1/{len(pages)})", pages[0], 0x3498db),
        view=view
    )

@bot.tree.command(name="history", description="Full history of a Roblox user")
async def history(i: discord.Interaction, user_id: str):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION","Owner Only"))

    await i.response.defer()

    # Roblox Info
    u, d = roblox_info(user_id)

    # ================= VERIFY LOGS =================
    try:
        logs = supabase.table("verify_logs").select("*").eq("roblox_id", user_id).execute().data
    except:
        logs = []

    verify = "❌ Never Verified"
    if logs:
        verify = ""
        for x in logs[-5:]:
            ts = x.get("timestamp", "Unknown")

            try:
                t = ts.split("T")[0]
            except:
                t = "Unknown"

            verify += f"• `{t}` — <@{x.get('discord_id','Unknown')}>\n"


    # ================= BAN CHECK =================
    try:
        ban = supabase.table("bans").select("*").eq("user_id", user_id).execute().data
    except:
        ban = []

    if ban:
        b = ban[0]
        if b["perm"]:
            ban_text = f"🔴 Permanent — `{b['reason']}`"
        else:
            left = int(max((float(b["expire"]) - time.time())/60 , 0))
            ban_text = f"⏱ Temp Ban ({left}m left)\nReason: `{b['reason']}`"
    else:
        ban_text = "🟢 Not Banned"


    # ================= ACCESS CHECK =================
    try:
        ac = supabase.table("access_users").select("user_id").eq("user_id", user_id).execute().data
        access = "✅ Whitelisted" if ac else "❌ Not Whitelisted"
    except:
        access = "⚠️ Error Checking"


    # ================= BLACKLIST CHECK =================
    try:
        blk = supabase.table("blacklist_users").select("user_id").eq("user_id", user_id).execute().data
        blk_text = "🚫 Blacklisted" if blk else "🟢 Not Blacklisted"
    except:
        blk_text = "⚠️ Error Checking"


    # ================= FINAL EMBED =================
    desc = (
        f"👤 **User Info**\n"
        f"🆔 `{user_id}`\n"
        f"👛 Username: **{u}**\n"
        f"🎭 Display: **{d}**\n\n"
        f"🚫 **Ban Status:** {ban_text}\n"
        f"🔐 **Access:** {access}\n"
        f"📛 **Blacklist:** {blk_text}\n\n"
        f"📜 **Recent Verifications**\n{verify}"
    )

    await i.followup.send(embed=emb("📂 USER HISTORY", desc, 0x9b59b6))

@bot.tree.command(name="multiverify", description="Users who verified multiple DIFFERENT roblox accounts")
async def multiverify(i:discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION","Owner only"))

    await i.response.defer()

    logs = supabase.table("verify_logs").select("*").execute().data
    if not logs:
        return await safe_send(i, emb("ℹ️ INFO","No verification logs found"))

    users = {}

    for x in logs:
        did = x["discord_id"]
        rid = x["roblox_id"]
        uname = x.get("username","Unknown")
        dname = x.get("display_name","Unknown")

        if did not in users:
            users[did] = {
                "roblox_ids": set(),
                "entries": []
            }

        users[did]["roblox_ids"].add(rid)
        users[did]["entries"].append((rid, uname, dname))

    result_blocks = []

    for did, data in users.items():
        if len(data["roblox_ids"]) > 1:

            try:
                user = await bot.fetch_user(int(did))
                name = user.mention
            except:
                name = f"`{did}`"

            block = (
                f"👤 **{name}** — `{did}`\n"
                f"👉 **Different Accounts Verified:** `{len(data['roblox_ids'])}`\n"
            )

            for rid, uname, dname in data["entries"]:
                block += f"🆔 `{rid}` | {uname} ({dname})\n"

            block += "────────────────────\n"
            result_blocks.append(block)

    if not result_blocks:
        return await safe_send(i, emb("✅ CLEAN", "No one verified multiple different accounts."))

    PAGES = []
    temp = []

    for b in result_blocks:
        temp.append(b)
        if len(temp) == 3:
            PAGES.append("".join(temp))
            temp = []

    if temp:
        PAGES.append("".join(temp))


    class MVPages(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=120)
            self.page = 0

        async def update(self, interaction):
            e = emb(
                f"🔎 MULTI ACCOUNT VERIFIERS ({self.page+1}/{len(PAGES)})",
                PAGES[self.page],
                0xffa500
            )
            await interaction.response.edit_message(embed=e, view=self)

        @discord.ui.button(label="⬅ Back", style=discord.ButtonStyle.gray)
        async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.page > 0:
                self.page -= 1
            await self.update(interaction)

        @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.gray)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.page < len(PAGES) - 1:
                self.page += 1
            await self.update(interaction)

        async def on_timeout(self):
            try:
                for c in self.children:
                    c.disabled = True
            except:
                pass


    view = MVPages()
    first = emb(
        f"🔎 MULTI ACCOUNT VERIFIERS (1/{len(PAGES)})",
        PAGES[0],
        0xffa500
    )

    await i.followup.send(embed=first, view=view)

@bot.tree.command(name="logs", description="View admin logs with filters + pagination")
@app_commands.choices(filter=[
    app_commands.Choice(name="All", value="all"),
    app_commands.Choice(name="Ban", value="ban"),
    app_commands.Choice(name="Tempban", value="tempban"),
    app_commands.Choice(name="Unban", value="unban"),
    app_commands.Choice(name="Access Add", value="access_add"),
    app_commands.Choice(name="Access Remove", value="access_remove"),
    app_commands.Choice(name="Blacklist Add", value="blacklist_add"),
    app_commands.Choice(name="Blacklist Remove", value="blacklist_remove"),
])
async def logs(i: discord.Interaction, filter: app_commands.Choice[str]):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Owner Only"))

    # ❌ ephemeral hata diya
    await i.response.defer()

    try:
        if filter.value == "all":
            data = supabase.table("admin_logs").select("*").order("timestamp", desc=True).limit(100).execute().data
        else:
            data = supabase.table("admin_logs").select("*").eq("action", filter.value).order("timestamp", desc=True).limit(100).execute().data
    except Exception as e:
        return await i.followup.send(embed=emb("❌ ERROR", f"Logs failed:\n`{e}`", 0xff0000))

    if not data:
        return await i.followup.send(embed=emb("📭 NO DATA", "No logs found for this filter", 0xffc107))

    pages = []
    chunk = []

    for x in data:
        t = x["timestamp"].split("T")[0]

        chunk.append(
            f"**Action:** `{x['action']}`\n"
            f"👤 **Executor:** <@{x['executor']}>\n"
            f"🆔 `{x['user_id']}`\n"
            f"👛 **Username:** `{x['username']}`\n"
            f"🎭 **Display:** `{x['display']}`\n"
            f"📅 `{t}`\n"
            f"──────────────\n"
        )

        if len(chunk) == 5:
            pages.append("".join(chunk))
            chunk = []

    if chunk:
        pages.append("".join(chunk))


    class LogPages(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=120)
            self.page = 0

        async def update(self, interaction):
            e = emb(
                f"🗂 LOGS — {filter.name.upper()} ({self.page+1}/{len(pages)})",
                pages[self.page],
                0x3498db
            )
            await interaction.response.edit_message(embed=e, view=self)

        @discord.ui.button(label="⏮ Back", style=discord.ButtonStyle.gray)
        async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.page > 0:
                self.page -= 1
            await self.update(interaction)

        @discord.ui.button(label="Next ⏭", style=discord.ButtonStyle.gray)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.page < len(pages) - 1:
                self.page += 1
            await self.update(interaction)

        async def on_timeout(self):
            try:
                for item in self.children:
                    item.disabled = True
            except:
                pass


    view = LogPages()
    e = emb(
        f"🗂 LOGS — {filter.name.upper()} (1/{len(pages)})",
        pages[0],
        0x3498db
    )

    # ❌ yaha bhi ephemeral hata diya
    await i.followup.send(embed=e, view=view)

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


# ================== FLASK OPTIMIZED BACKEND ==================
from flask import Flask, jsonify
import time
from datetime import datetime

app = Flask(__name__)

# ================== PER USER CACHE ==================
CACHE_TTL = 20
cache = {}   # <-- FIX: per user cache


def safe_query(table, **filters):
    try:
        q = supabase.table(table).select("*")
        for k,v in filters.items():
            q = q.eq(k,v)
        return q.execute().data
    except Exception as e:
        print("DB ERROR:",e)
        return None


def build_status(user_id):
    global cache
    now = time.time()

    # ================== PER USER CACHE CHECK ==================
    if user_id in cache:
        if now - cache[user_id]["time"] < CACHE_TTL:
            return cache[user_id]["data"]

    try:
        banned = False
        temp = False
        reason = "None"
        minutes_left = 0

        # ===== BAN CHECK =====
        bans = safe_query("bans", user_id=user_id)
        if bans:
            b = bans[0]
            if b["perm"]:
                banned = True
                reason = b["reason"]
            else:
                if float(b["expire"]) > time.time():
                    banned = True
                    temp = True
                    reason = b["reason"]
                    minutes_left = int((float(b["expire"]) - time.time()) / 60)

        # ===== ACCESS =====
        access = safe_query("access_users", user_id=user_id)
        whitelisted = True if access else False

        # ===== BLACKLIST =====
        blk = safe_query("blacklist_users", user_id=user_id)
        blacklisted = True if blk else False

        # ===== KICK =====
        kick = safe_query("kick_flags", user_id=user_id)
        kick_now = True if kick else False
        kick_reason = kick[0]["reason"] if kick else "None"

        # ===== MAINTENANCE =====
        m = safe_query("bot_settings", key="maintenance")
        maintenance = m and m[0]["value"]=="true"

        data = {
            "user_id": user_id,
            "access": whitelisted,
            "banned": banned,
            "tempban": temp,
            "ban_reason": reason,
            "minutes_left": minutes_left,
            "blacklisted": blacklisted,
            "kick": kick_now,
            "kick_reason": kick_reason,
            "maintenance": maintenance,
            "timestamp": datetime.utcnow().isoformat()
        }

        # ================== CACHE STORE ==================
        cache[user_id] = {
            "data": data,
            "time": now
        }

        return data

    except Exception as e:
        print("STATUS ERROR:",e)
        return {"error":"backend busy"}



# ================== ROUTES ==================
@app.route("/status/<uid>")
def status(uid):
    return jsonify(build_status(uid))


@app.route("/")
def home():
    return jsonify({"status":"OK","uptime":datetime.utcnow().isoformat()})


@app.route("/ping")
def ping():
    return "pong"


# disable render spam logs
import logging
log = logging.getLogger('werkzeug')
log.disabled = True

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
