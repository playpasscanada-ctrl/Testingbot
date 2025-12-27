import os, json, time, threading, requests
from datetime import datetime

import discord
from discord import app_commands
from discord import ui   # ⬅️ ye add karo
from discord.ext import commands

from flask import Flask, jsonify
from supabase import create_client, Client

def get_roblox_info(user_id):
    try:
        user = requests.get(
            f"https://users.roblox.com/v1/users/{user_id}",
            timeout=5
        ).json()

        return {
            "username": user.get("name", "Unknown"),
            "display": user.get("displayName", "Unknown")
        }

    except Exception as e:
        print("ROBLOX LOOKUP ERROR:", e)
        return {
            "username": "Unknown",
            "display": "Unknown"
        }

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

# ================== DISCORD INTENTS ==================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # <--- YE LINE ADD KARNA ZAROORI HAI
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

        # ==================================================
    # 🔥 ATTITUDE AUTO-REPLY SYSTEM (Saksham Tag/Name)
    # ==================================================
    OWNER_ID = 804687084249284618  # Tumhari ID
    
    # Check: Agar message me "Saksham" hai ya Tumhe Tag kiya hai
    if "saksham" in msg.content.lower() or str(OWNER_ID) in msg.content:
        
        # Khud ko reply nahi karna (Agar tumne khud likha to reply nahi aayega)
        if msg.author.id != OWNER_ID:
            import random
            
            # Mast Attitude Replies
            replies = [
                f"Oye {msg.author.mention}! 🤨\nKya kaam hai Saksham se? Kyu 'Saksham Saksham' laga rakha hai? Shanti rakh thodi.",
                f"Sun {msg.author.mention}, Saksham abhi busy hai. 🤫\nJo bolna hai yahi likh de, spam mat kar.",
                f"Bhai {msg.author.mention}, kya dikkat hai? 😒\nFans ki line peeche hai, dhakka-mukki mat kar. Message drop kar aur wait kar.",
                f"Kya hua {msg.author.mention}? 🙄\nSaksham ka naam lene se pehle appointment li thi kya? Chupchap message likh aur nikal."
            ]
            
            await msg.reply(random.choice(replies))
            return  # 🛑 YAHI RUK JAYEGA (Verify code nahi chalega iske baad)
            
    # ==================================================


    # --- ONLY THIS CHANNEL ---
    if msg.channel.id != 1451973498200133786:
        return

    REVIEW_CHANNEL_ID = 1450514760276774967
    OWNER_ID = 804687084249284618

    user_id = msg.content.strip()

    if not user_id.isdigit():
        await msg.delete()
        await msg.channel.send(
            f"{msg.author.mention} ❌ Sirf Roblox User ID bhejo!",
            delete_after=5
        )
        return

    # 1. Pehle Roblox Info Fetch Karo (Alag Try/Except)
    try:
        data = requests.get(
            f"https://users.roblox.com/v1/users/{user_id}",
            timeout=5
        ).json()

        if 'errors' in data:
            raise Exception("Invalid Roblox ID")

        username = data.get("name", "Unknown")
        display = data.get("displayName", "Unknown")

    except Exception as e:
        await msg.reply(f"❌ Invalid Roblox ID ya Roblox API down hai. Error: `{e}`")
        return

    # 2. Main Logic (Database & Checks)
    try:
        # =========================
        # ⚠️ BLACKLIST CHECK
        # =========================
        blk = (
            supabase.table("blacklist_users")
            .select("user_id")
            .eq("user_id", user_id)
            .execute()
            .data
        )
        if blk:
            embed = discord.Embed(
                title="🚫 Verification Denied",
                description="You are blacklisted from this system.",
                color=0xe74c3c
            )
            await msg.reply(embed=embed)
            return

        # =========================
        # 🎯 LIMIT + OWNER APPROVAL SYSTEM
        # =========================
        already = (
            supabase.table("access_users")
            .select("user_id")
            .eq("discord_id", str(msg.author.id))
            .execute()
            .data
        )

        if already:
            approved = (
                supabase.table("multi_access")
                .select("discord_id")
                .eq("discord_id", str(msg.author.id))
                .execute()
                .data
            )

            if not approved:
                embed = discord.Embed(
                    title="❌ Verification Limit Reached",
                    description="You reached max verification limit.\nPlease wait for admin approval.",
                    color=0xe74c3c
                )
                await msg.reply(embed=embed)

                ch = bot.get_channel(REVIEW_CHANNEL_ID)
                if ch:
                    # 👇👇 YAHAN UPDATE KIYA HAI (DETAILS ADDED) 👇👇
                    req = discord.Embed(
                        title="⚠️ MULTI VERIFY REQUEST",
                        description=f"**User:** {msg.author.mention}\n**Discord ID:** `{msg.author.id}`",
                        color=0xffa500
                    )
                    
                    # Nayi Details:
                    req.add_field(name="🆔 Requested ID", value=f"`{user_id}`", inline=False)
                    req.add_field(name="👤 Username", value=f"**{username}**", inline=True)
                    req.add_field(name="✨ Display Name", value=f"{display}", inline=True)
                    
                    # Avatar Photo:
                    req.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")

                    view = discord.ui.View()

                    async def approve(interaction: discord.Interaction):
                        if interaction.user.id != OWNER_ID:
                            return await interaction.response.send_message(
                                "Only owner can approve.", ephemeral=True
                            )

                        supabase.table("multi_access").upsert({
                            "discord_id": str(msg.author.id),
                            "approved": True
                        }).execute()

                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title="🟢 ACCESS GRANTED",
                                description=f"{msg.author.mention} can now verify unlimited Roblox accounts.",
                                color=0x2ecc71
                            ),
                            view=None
                        )

                    async def deny(interaction: discord.Interaction):
                        if interaction.user.id != OWNER_ID:
                            return await interaction.response.send_message(
                                "Only owner can deny.", ephemeral=True
                            )

                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title="🔴 ACCESS DENIED",
                                description=f"{msg.author.mention} will stay limited.",
                                color=0xe74c3c
                            ),
                            view=None
                        )

                    approve_btn = discord.ui.Button(style=discord.ButtonStyle.green, label="Give Access")
                    deny_btn = discord.ui.Button(style=discord.ButtonStyle.red, label="Deny Access")

                    approve_btn.callback = approve
                    deny_btn.callback = deny

                    view.add_item(approve_btn)
                    view.add_item(deny_btn)

                    await ch.send(embed=req, view=view)

                return

        # =========================
        # ✅ ALREADY VERIFIED CHECK
        # =========================
        exist = (
            supabase.table("access_users")
            .select("*")
            .eq("user_id", user_id)
            .execute()
            .data
        )

        if exist:
            embed = discord.Embed(
                title="✅ Already Verified",
                description="You are already verified & whitelisted.",
                color=0x2ecc71
            )
            await msg.reply(embed=embed)
            return

        # =========================
        # AUTO ADD TO WHITELIST
        # =========================
        supabase.table("access_users").insert({
            "user_id": user_id,
            "username": username,
            "display_name": display,
            "discord_id": str(msg.author.id)
        }).execute()

        # =========================
        # SAVE VERIFY LOG
        # =========================
        supabase.table("verify_logs").insert({
            "discord_id": str(msg.author.id),
            "roblox_id": user_id,
            "username": username,
            "display_name": display,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()

        # =========================
        # USER SUCCESS EMBED
        # =========================
        embed = discord.Embed(
            title="✅ Verified & Whitelisted",
            color=0x2ecc71
        )
        embed.add_field(name="Roblox ID", value=f"`{user_id}`", inline=False)
        embed.add_field(name="Username", value=username, inline=True)
        embed.add_field(name="Display Name", value=display, inline=True)
        embed.set_footer(text="Access Granted")

        await msg.reply(embed=embed)

        # =========================
        # LOG CHANNEL
        # =========================
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

    except Exception as e:
        print(f"ERROR AAYA HAI: {e}")
        await msg.reply(f"❌ System Error: `{e}`\nAdmin ko contact karein.")
                        
# ================== BAN SYSTEM (UPDATED WITH ADMIN NAME) ==================

@bot.tree.command(name="ban")
async def ban(i:discord.Interaction, user_id:str, reason:str):
    if not owner(i): 
        return

    # Defer isliye taaki API call me time lage to error na aaye
    await i.response.defer()

    u, d = roblox_info(user_id)

    # Database me Executor (Admin) bhi save kar rahe hain
    supabase.table("bans").upsert({
        "user_id": user_id,
        "perm": True,
        "reason": reason,
        "expire": None,
        "executor": str(i.user.id)  # <-- Ye nayi cheez hai
    }).execute()

    # Log Action
    try:
        log_action("ban", user_id, u, d, i.user.id)
    except:
        pass

    await i.followup.send(embed=emb(
        "🔨 BANNED",
        f"**ID:** `{user_id}`\n**User:** `{u}` ({d})\n**Reason:** {reason}\n**Banned By:** {i.user.mention}",
        0xff0000
    ))

@bot.tree.command(name="tempban")
async def tempban(i:discord.Interaction, user_id:str, minutes:int, reason:str):
    if not owner(i): 
        return

    await i.response.defer()

    u, d = roblox_info(user_id)

    supabase.table("bans").upsert({
        "user_id": user_id,
        "perm": False,
        "reason": reason,
        "expire": time.time() + minutes * 60,
        "executor": str(i.user.id)  # <-- Ye nayi cheez hai
    }).execute()

    try:
        log_action("tempban", user_id, u, d, i.user.id)
    except:
        pass

    await i.followup.send(embed=emb(
        "⏱ TEMPBAN",
        f"**ID:** `{user_id}`\n**User:** `{u}` ({d})\n**Time:** `{minutes} min`\n**Reason:** {reason}\n**Banned By:** {i.user.mention}",
        0xffa500
    ))

@bot.tree.command(name="list")
async def listb(i:discord.Interaction):
    if not owner(i): 
        return
    
    await i.response.defer()
    
    try:
        data = supabase.table("bans").select("*").execute().data
        
        if not data:
            return await i.followup.send(embed=emb("🚫 BANNED USERS", "No banned users found."))

        txt = ""
        now = time.time()

        for x in list(data):
            # Expired bans hatao
            if not x["perm"] and x.get("expire") and now > float(x["expire"]):
                supabase.table("bans").delete().eq("user_id", x["user_id"]).execute()
                continue
            
            u, n = roblox_info(x["user_id"])

            # Time Logic
            if x["perm"]:
                t = "PERM"
            else:
                try:
                    left = int((float(x['expire']) - now) / 60)
                    t = f"{left}m"
                except:
                    t = "Unknown"

            # Reason fetch
            reason = x.get("reason", "No Reason")
            
            # Executor (Admin) Fetch logic
            admin_txt = ""
            if x.get("executor"):
                try:
                    # Discord se naam nikal rahe hain
                    admin_obj = await bot.fetch_user(int(x["executor"]))
                    admin_txt = f" | 👮 By: {admin_obj.name}"
                except:
                    admin_txt = " | 👮 By: Unknown"

            # Final Line
            txt += f"• `{x['user_id']}` | **{u}** ({n})\n   ⏳ `{t}` | 📝 `{reason}`{admin_txt}\n\n"

            # Embed Limit Check
            if len(txt) > 3500:
                txt += "\n... (List truncated)"
                break

        await i.followup.send(embed=emb("🚫 BANNED USERS LIST", txt or "None"))

    except Exception as e:
        await i.followup.send(embed=emb("❌ ERROR", f"List error: `{e}`"))

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

# ================== MULTI-VERIFY MANAGEMENT ==================
@bot.tree.command(name="multiaccess", description="Manage users who can verify UNLIMITED accounts")
@app_commands.choices(mode=[
    app_commands.Choice(name="Add Permission", value="add"),
    app_commands.Choice(name="Remove Permission", value="remove"),
    app_commands.Choice(name="List Users", value="list"),
])
@app_commands.describe(discord_id="Discord User ID (Required for Add/Remove)")
async def multiaccess(i: discord.Interaction, mode: app_commands.Choice[str], discord_id: str = None):
    
    # 1. OWNER CHECK
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Only Owner can manage multi-access."))

    # ================= ADD USER =================
    if mode.value == "add":
        if not discord_id:
            return await safe_send(i, emb("❌ ERROR", "Discord ID dena zaroori hai!"))

        # Save to Supabase
        try:
            supabase.table("multi_access").upsert({
                "discord_id": discord_id,
                "approved": True
            }).execute()

            await safe_send(i, emb(
                "✅ ACCESS GRANTED",
                f"User <@{discord_id}> (`{discord_id}`)\n\nAb ye user **Unlimited Roblox IDs** verify kar sakta hai.",
                0x2ecc71
            ))
        except Exception as e:
            await safe_send(i, emb("❌ DB ERROR", f"```{e}```"))

    # ================= REMOVE USER =================
    elif mode.value == "remove":
        if not discord_id:
            return await safe_send(i, emb("❌ ERROR", "Discord ID dena zaroori hai!"))

        try:
            supabase.table("multi_access").delete().eq("discord_id", discord_id).execute()

            await safe_send(i, emb(
                "🗑 ACCESS REVOKED",
                f"User <@{discord_id}> (`{discord_id}`)\n\nAb ye user **sirf 1 ID** verify kar payega.",
                0xff0000
            ))
        except Exception as e:
            await safe_send(i, emb("❌ DB ERROR", f"```{e}```"))

    # ================= LIST USERS =================
    elif mode.value == "list":
        try:
            data = supabase.table("multi_access").select("*").execute().data

            if not data:
                return await safe_send(i, emb("📂 MULTI-ACCESS LIST", "No users found."))

            txt = ""
            for x in data:
                did = x['discord_id']
                txt += f"• <@{did}> (`{did}`)\n"

            await safe_send(i, emb("📂 MULTI-ACCESS ALLOWED USERS", txt, 0x3498db))
        
        except Exception as e:
            await safe_send(i, emb("❌ DB ERROR", f"```{e}```"))

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

@bot.tree.command(
    name="verifiedlist",
    description="Show paginated verified Roblox users"
)
async def verifiedlist(i: discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Owners only"))

    await i.response.defer()   # NO EPHEMERAL + SAFE

    try:
        logs = (
            supabase.table("verify_logs")
            .select("*")
            .order("timestamp", desc=True)
            .execute()
            .data
        )

        access = supabase.table("access_users").select("user_id").execute().data
        access_ids = {x["user_id"] for x in access}

    except Exception as e:
        return await i.followup.send(
            embed=emb("⚠️ ERROR", f"Failed to fetch logs\n`{e}`")
        )

    if not logs:
        return await i.followup.send(
            embed=emb("📭 EMPTY", "No verified users found")
        )

    seen = set()
    entries = []

    for x in logs:
        rid = x["roblox_id"]

        # ignore duplicates
        if rid in seen:
            continue

        # only users who STILL HAVE ACCESS
        if rid not in access_ids:
            continue

        seen.add(rid)

        entries.append(
            f"👤 <@{x['discord_id']}>\n"
            f"🆔 Roblox ID: `{x['roblox_id']}`\n"
            f"🧑 Username: **{x['username']}**\n"
            f"✨ Display: {x['display_name']}\n"
            f"🕒 `{x['timestamp']}`\n"
            f"────────────────────\n"
        )

    if not entries:
        return await i.followup.send(
            embed=emb("📛 CLEAN", "No currently whitelisted verified users")
        )

    # ================= PAGINATION =================
    PAGES = []
    chunk = []

    for e in entries:
        chunk.append(e)
        if len(chunk) == 5:
            PAGES.append("".join(chunk))
            chunk = []

    if chunk:
        PAGES.append("".join(chunk))


    class VerifyPages(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=120)
            self.page = 0

        async def update(self, interaction):
            embed = emb(
                f"📜 VERIFIED USERS LIST ({self.page+1}/{len(PAGES)})",
                PAGES[self.page],
                0x3498db
            )
            await interaction.response.edit_message(embed=embed, view=self)

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


    view = VerifyPages()

    first = emb(
        f"📜 VERIFIED USERS LIST (1/{len(PAGES)})",
        PAGES[0],
        0x3498db
    )

    await i.followup.send(embed=first, view=view)

# ================== USER INFO (GOD MODE) ==================
@bot.tree.command(name="userinfo", description="Get MAXIMUM details of a Discord User (Discord + Roblox + DB)")
@app_commands.describe(user="Tag the player (@Username)")
async def userinfo(i: discord.Interaction, user: discord.Member):
    
    await i.response.defer()

    try:
        # ================= 1. DISCORD DEEP DIVE =================
        now = datetime.utcnow()
        
        # --- Dates & Age ---
        created_at = user.created_at.replace(tzinfo=None)
        acc_age = now - created_at
        age_str = f"{acc_age.days // 365} Years, {acc_age.days % 365} Days"
        
        joined_at = user.joined_at.replace(tzinfo=None)
        join_str = joined_at.strftime("%d %B %Y")
        
        # --- Join Position (Server Rank) ---
        # Note: Requires intents.members = True
        try:
            sorted_members = sorted(i.guild.members, key=lambda m: m.joined_at or now)
            join_pos = sorted_members.index(user) + 1
            total_members = len(i.guild.members)
            join_rank = f"#{join_pos} / {total_members}"
        except:
            join_rank = "Unknown (Intents Error)"

        # --- Roles & Perms ---
        roles = [r.mention for r in user.roles if r.name != "@everyone"]
        roles.reverse()
        role_count = len(roles)
        top_roles = ", ".join(roles[:5]) + (f" (+{role_count-5} more)" if role_count > 5 else "")
        
        key_perms = []
        if user.guild_permissions.administrator: key_perms.append("👑 ADMIN")
        if user.guild_permissions.ban_members: key_perms.append("🔨 BAN")
        if user.guild_permissions.kick_members: key_perms.append("👢 KICK")
        if user.guild_permissions.manage_guild: key_perms.append("⚙️ MANAGER")
        perm_str = " | ".join(key_perms) if key_perms else "User"

        # --- Badges & Status ---
        is_bot = "🤖 YES" if user.bot else "👤 NO"
        is_booster = f"🚀 Yes (Since {user.premium_since.strftime('%b %Y')})" if user.premium_since else "❌ No"
        nick = user.nick if user.nick else "None"

        # ================= 2. SUPABASE (DB) DEEP SCAN =================
        
        # A. Multi-Access (VIP) Check
        multi_data = supabase.table("multi_access").select("*").eq("discord_id", str(user.id)).execute().data
        access_level = "🔓 UNLIMITED (VIP)" if multi_data else "🔒 LIMITED (Standard)"

        # B. Fetch All Linked Accounts
        acc_data = supabase.table("access_users").select("*").eq("discord_id", str(user.id)).execute().data
        
        roblox_list = ""
        alert_list = ""
        total_accs = 0
        risk_score = 0  # 0 = Safe, 100 = Critical
        
        if acc_data:
            total_accs = len(acc_data)
            
            # Risk Logic: More accounts = Slight risk increase (Alt farming check)
            if total_accs > 2: risk_score += 10
            if total_accs > 5: risk_score += 20

            for acc in acc_data:
                rid = acc['user_id']
                # Database me purana username ho sakta hai, koshish karo naya fetch karne ki (Optional)
                # Agar slow ho raha ho to 'roblox_info(rid)' hata kar seedha acc['username'] use karna
                try:
                    u, d = roblox_info(rid) 
                except:
                    u, d = acc.get('username','Unknown'), acc.get('display_name','Unknown')

                # BAN & BLACKLIST CHECK
                ban_chk = supabase.table("bans").select("*").eq("user_id", rid).execute().data
                blk_chk = supabase.table("blacklist_users").select("*").eq("user_id", rid).execute().data
                
                status_icon = "🟢"
                note = ""

                if ban_chk:
                    status_icon = "🔴"
                    reason = ban_chk[0].get('reason', 'No reason')
                    alert_list += f"🚨 **BANNED:** `{u}` ({reason})\n"
                    risk_score += 50
                    note = "[BANNED]"

                if blk_chk:
                    status_icon = "⚫"
                    alert_list += f"🚫 **BLACKLIST:** `{u}`\n"
                    risk_score += 100
                    note = "[BLACKLISTED]"

                roblox_list += f"{status_icon} **{d}** (`@{u}`)\n   🆔 `{rid}` {note}\n"

            # Trim list if too long
            if len(roblox_list) > 900:
                roblox_list = roblox_list[:900] + "\n... (More hidden)"
        else:
            roblox_list = "❌ No verified accounts linked."
        
        # C. Calculate Final Risk Status
        if risk_score == 0: risk_status = "🟢 SAFE"
        elif risk_score < 40: risk_status = "🟡 MODERATE (Multi-Accounting)"
        elif risk_score < 80: risk_status = "🟠 HIGH RISK (Active Bans)"
        else: risk_status = "🔴 CRITICAL (Blacklisted)"

        # ================= 3. BUILD THE EMBED =================
        embed = discord.Embed(color=user.color)
        embed.set_author(name=f"{user.name} ({user.display_name})", icon_url=user.avatar.url if user.avatar else None)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        
        # Banner Image (Agar user ke paas hai)
        if user.banner:
            embed.set_image(url=user.banner.url)

        # --- SECTION 1: DISCORD PROFILE ---
        embed.add_field(name="🏷️ Identity", value=(
            f"**ID:** `{user.id}`\n"
            f"**Nickname:** `{nick}`\n"
            f"**Bot:** {is_bot}\n"
            f"**Booster:** {is_booster}"
        ), inline=True)

        embed.add_field(name="📅 History", value=(
            f"**Age:** `{age_str}`\n"
            f"**Joined:** `{join_str}`\n"
            f"**Join Rank:** `{join_rank}`"
        ), inline=True)

        embed.add_field(name=f"🛡️ Roles & Perms ({role_count})", value=(
            f"**Permissions:** {perm_str}\n"
            f"**Top Roles:** {top_roles}"
        ), inline=False)

        # --- SECTION 2: SYSTEM SECURITY ---
        embed.add_field(name="⚙️ Verification Profile", value=(
            f"**Access Level:** {access_level}\n"
            f"**Linked Accounts:** `{total_accs}`\n"
            f"**Risk Analysis:** {risk_status}"
        ), inline=False)

        # --- SECTION 3: ROBLOX ACCOUNTS ---
        embed.add_field(name="🎮 Roblox Connections", value=roblox_list, inline=False)

        # --- SECTION 4: ALERTS (Only if dangerous) ---
        if alert_list:
            embed.add_field(name="⚠️ SECURITY ALERTS", value=alert_list, inline=False)

        # Footer
        embed.set_footer(text=f"Requested by {i.user.name} • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

        await i.followup.send(embed=embed)

    except Exception as e:
        await i.followup.send(embed=emb("❌ ERROR", f"Failed to fetch profile: `{e}`"))
    
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

    val = "true" if mode.value=="on" else "false"
    
    # DB Update
    supabase.table("bot_settings").update(
        {"value": val}
    ).eq("key","maintenance").execute()
    
    # 🔥 LOG SAVE KARO
    try:
        log_action(f"maintenance_{mode.value}", "-", "-", "-", i.user.id)
    except:
        pass

    await safe_send(i, emb(
        "🛠 MAINTENANCE",
        f"System Maintenance is now **{mode.value.upper()}**"
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

def safe_fetch(table):
    for _ in range(3):
        try:
            x = supabase.table(table).select("*").execute()
            return x.data or []
        except:
            time.sleep(0.3)
    return []

@bot.tree.command(name="stats")
async def stats(i: discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION","Owner only"))

    await i.response.defer()

    try:
        now = time.time()

        bans       = safe_fetch("bans")
        access     = safe_fetch("access_users")
        blacklist  = safe_fetch("blacklist_users")
        logs       = safe_fetch("verify_logs")
        kicks      = safe_fetch("kick_flags")
        settings   = supabase.table("bot_settings").select("*").execute().data or []

        perm = 0
        temp = 0

        for b in bans:
            if b.get("perm"):
                perm += 1
            else:
                if b.get("expire") and now < float(b["expire"]):
                    temp += 1

        access_status = "🟢 OFF (Everyone Allowed)"
        maintenance_status = "🟢 OFF"

        for s in settings:
            if s["key"] == "access_enabled" and s["value"] == "true":
                access_status = "🔐 ON (Whitelist Enabled)"
            if s["key"] == "maintenance" and s["value"] == "true":
                maintenance_status = "🛠 ON"

        uptime = int(time.time() - START_TIME)
        hrs = uptime // 3600
        mins = (uptime % 3600) // 60

        embed = discord.Embed(
            title="⚙️ SYSTEM CONTROL PANEL",
            description="Premium Secure Control Dashboard",
            color=0x2ecc71
        )

        embed.add_field(
            name="🚫 Ban System",
            value=(
                f"**Permanent Bans:** `{perm}`\n"
                f"**Active TempBans:** `{temp}`\n"
                f"**Blacklisted Users:** `{len(blacklist)}`"
            ),
            inline=False
        )

        embed.add_field(
            name="👥 User Access",
            value=(
                f"**Whitelisted Users:** `{len(access)}`\n"
                f"**Verification Logs:** `{len(logs)}`\n"
                f"**Unique Verifiers:** `{len(set(x['discord_id'] for x in logs))}`\n"
                f"**Kick Flags Pending:** `{len(kicks)}`"
            ),
            inline=False
        )

        embed.add_field(
            name="🛠 System Status",
            value=(
                f"**Access System:** {access_status}\n"
                f"**Maintenance:** {maintenance_status}"
            ),
            inline=False
        )

        embed.add_field(
            name="🤖 Bot Status",
            value=(
                f"**Uptime:** `{hrs}h {mins}m`\n"
                f"**Health:** 🟢 Stable & Optimized"
            ),
            inline=False
        )

        embed.set_footer(text="RoboPal • Secure Moderation Engine")
        embed.timestamp = datetime.utcnow()

        await i.followup.send(embed=embed)

    except Exception as e:
        await i.followup.send(
            embed=emb("❌ ERROR", f"Stats failed:\n```{e}```", 0xff0000)
        )
        
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

@bot.tree.command(name="profile", description="Full profile + verification + moderation history of a Roblox user")
async def profile(i: discord.Interaction, user_id: str):

    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Owner only command"))

    await i.response.defer()

    try:
        # Fetch Roblox Info
        data = requests.get(f"https://users.roblox.com/v1/users/{user_id}", timeout=5).json()
        username = data.get("name","Unknown")
        display = data.get("displayName","Unknown")
    except:
        return await safe_send(i, emb("⚠️ ERROR", "Invalid Roblox ID / Roblox API Down"))

    
    # ===== ACCESS CHECK =====
    access = supabase.table("access_users").select("*").eq("user_id", user_id).execute().data
    access_text = "🟢 Whitelisted" if access else "🔴 Not Whitelisted"


    # ===== BLACKLIST =====
    blk = supabase.table("blacklist_users").select("*").eq("user_id", user_id).execute().data
    blacklist_text = "🚫 Blacklisted" if blk else "🟢 Not Blacklisted"


    # ===== BAN CHECK =====
    bans = supabase.table("bans").select("*").eq("user_id", user_id).execute().data
    ban_text = "🟢 Not Banned"

    if bans:
        b = bans[0]

        if b["perm"]:
            ban_text = f"🔴 Permanent Ban\nReason: `{b['reason']}`"
        else:
            import time
            left = int((float(b["expire"]) - time.time())/60)
            ban_text = f"⏱ Tempban | `{left} min left`\nReason: `{b['reason']}`"


    # ===== LAST VERIFY LOG =====
    logs = (
        supabase.table("verify_logs")
        .select("*")
        .eq("roblox_id", user_id)
        .order("timestamp", desc=True)
        .limit(1)
        .execute()
        .data
    )

    if logs:
        v = logs[0]
        verifier = f"<@{v['discord_id']}>"
        vtime = v["timestamp"].replace("T"," ").split(".")[0]
        verify_text = (
            f"👤 Verified By: {verifier}\n"
            f"🕒 Time: `{vtime}`"
        )
    else:
        verify_text = "❌ Never Verified"


    # ===== FINAL PREMIUM EMBED =====
    desc = (
        f"👤 **User Profile**\n"
        f"🆔 ID: `{user_id}`\n"
        f"🧑 Username: **{username}**\n"
        f"✨ Display: **{display}**\n\n"

        f"🔐 **Access:** {access_text}\n"
        f"📛 **Blacklist:** {blacklist_text}\n"
        f"🚫 **Ban Status:**\n{ban_text}\n\n"

        f"📜 **Verification Info**\n{verify_text}"
    )

    await i.followup.send(
        embed = emb("📂 USER PROFILE — PREMIUM", desc, 0x3498db)
    )

@bot.tree.command(name="multiverify", description="Users who verified multiple Roblox accounts")
async def multiverify(i: discord.Interaction):

    # ---- ALWAYS DEFERS INSTANTLY (NO FAIL) ----
    try:
        await i.response.defer(thinking=True)
    except:
        pass

    # ---- OWNER ONLY CHECK ----
    if not owner(i):
        try:
            return await i.followup.send(embed=emb("❌ NO PERMISSION","Owner only"), ephemeral=True)
        except:
            return

    # ---- SAFE SUPABASE FETCH ----
    try:
        logs = supabase.table("access_users").select("*").execute().data
    except Exception as e:
        return await i.followup.send(embed=emb("❌ Database Error", str(e)), ephemeral=True)

    if not logs:
        return await i.followup.send(embed=emb("ℹ️ INFO","No verified users found"))

    users = {}

    for x in logs:
        did = x.get("discord_id")
        rid = x.get("user_id")
        uname = x.get("username","Unknown")
        dname = x.get("display_name","Unknown")

        if not did or not rid:
            continue

        if did not in users:
            users[did] = {
                "roblox_ids": set(),
                "entries": {}
            }

        users[did]["roblox_ids"].add(rid)
        users[did]["entries"][rid] = (uname, dname)

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

            for rid, info in data["entries"].items():
                uname, dname = info
                block += f"🆔 `{rid}` | {uname} ({dname})\n"

            block += "────────────────────\n"
            result_blocks.append(block)

    if not result_blocks:
        return await i.followup.send(embed=emb("✅ CLEAN","No one verified multiple different accounts."))

    PAGES = []
    temp = []

    for b in result_blocks:
        temp.append(b)
        if len(temp) == 3:
            PAGES.append("".join(temp))
            temp = []

    if temp:
        PAGES.append("".join(temp))


    # -------- SAFE PAGINATION --------
    class MVPages(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=180)
            self.page = 0

        async def refresh(self, interaction):
            e = emb(
                f"🔎 MULTI ACCOUNT VERIFIERS ({self.page+1}/{len(PAGES)})",
                PAGES[self.page],
                0xffa500
            )
            try:
                await interaction.response.edit_message(embed=e, view=self)
            except:
                try:
                    await interaction.edit_original_response(embed=e, view=self)
                except:
                    pass

        @discord.ui.button(label="⬅ Back", style=discord.ButtonStyle.gray)
        async def back(self, interaction: discord.Interaction, btn: discord.ui.Button):
            if self.page > 0:
                self.page -= 1
            await self.refresh(interaction)

        @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.gray)
        async def next(self, interaction: discord.Interaction, btn: discord.ui.Button):
            if self.page < len(PAGES)-1:
                self.page += 1
            await self.refresh(interaction)

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

@bot.tree.command(name="fakeban", description="Fake ban control panel")
@app_commands.describe(
    action="add / remove / list",
    userid="Roblox User ID",
    message="Custom message (optional)"
)
async def fakeban(i: discord.Interaction, action: str, userid: str=None, message: str=None):

    if not owner(i):
        return await i.response.send_message(embed=emb("❌ NO PERMISSION", "Owner only"), ephemeral=False)

    await i.response.defer()

    try:
        if action.lower() == "add":
            if not userid:
                return await i.followup.send(embed=emb("❌ ERROR","User ID required"))

            # Already exists?
            chk = supabase.table("fake_warnings").select("user_id").eq("user_id", userid).execute().data
            if chk:
                return await i.followup.send(embed=emb("⚠️ ALREADY PENDING","This player already has a fake warning pending"))

            # Get username + display automatically
            info = get_roblox_info(userid)   # <-- Tumhara function already hoga
            uname = info["username"]
            dname = info["display"]

            supabase.table("fake_warnings").insert({
                "user_id": userid,
                "username": uname,
                "display_name": dname,
                "message": message or "🚫 Account Action Required\n\nYour account has been temporarily restricted...\nDuration: 3 Days\nReference: #SEC-9043X"
            }).execute()

            return await i.followup.send(embed=emb(
                "🚨 FAKE BAN ADDED",
                f"👤 **{dname}** (`{uname}`)\n🆔 `{userid}`\n\nFake ban queued successfully",
                0xff0000
            ))

        # ================= REMOVE =================
        elif action.lower() == "remove":
            supabase.table("fake_warnings").delete().eq("user_id", userid).execute()

            return await i.followup.send(embed=emb(
                "🧹 REMOVED",
                f"User `{userid}` removed from fake queue",
                0x2ecc71
            ))

        # ================= LIST =================
        elif action.lower() == "list":
            data = supabase.table("fake_warnings").select("*").execute().data

            if not data:
                return await i.followup.send(embed=emb("📭 EMPTY","No pending fake bans"))

            text = ""
            for x in data:
                text += f"👤 **{x['display_name']}** (`{x['username']}`)\n🆔 `{x['user_id']}`\n-------------------\n"

            return await i.followup.send(embed=emb("📜 PENDING FAKE BANS", text[:4000], 0x3498db))

        else:
            return await i.followup.send(embed=emb("❌ Invalid Action","Use `add / remove / list`"))

    except Exception as e:
        return await i.followup.send(embed=emb("❌ ERROR", f"```{e}```"))

@bot.tree.command(name="logs", description="View admin logs with filters + pagination")
@app_commands.choices(filter=[
    app_commands.Choice(name="All Actions", value="all"),
    app_commands.Choice(name="Maintenance (On/Off)", value="maintenance"),  # <-- NEW
    app_commands.Choice(name="Stop System (On/Off)", value="stop"),        # <-- NEW
    app_commands.Choice(name="Ban", value="ban"),
    app_commands.Choice(name="Tempban", value="tempban"),
    app_commands.Choice(name="Unban", value="unban"),
    app_commands.Choice(name="Kick", value="kick"),
    app_commands.Choice(name="Access Add", value="access_add"),
    app_commands.Choice(name="Access Remove", value="access_remove"),
    app_commands.Choice(name="Multi-Access Granted", value="multi_add"),
    app_commands.Choice(name="Multi-Access Revoked", value="multi_remove"),
    app_commands.Choice(name="Blacklist Add", value="blacklist_add"),
    app_commands.Choice(name="Blacklist Remove", value="blacklist_remove"),
])
async def logs(i: discord.Interaction, filter: app_commands.Choice[str]):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Owner Only"))

    await i.response.defer()

    try:
        # Query Logic Updated for Partial Matching (like 'maintenance%')
        if filter.value == "all":
            data = supabase.table("admin_logs").select("*").order("timestamp", desc=True).limit(100).execute().data
        else:
            # .ilike use kar rahe hain taaki 'maintenance' filter 'maintenance_on' aur 'maintenance_off' dono pakad le
            data = supabase.table("admin_logs").select("*").ilike("action", f"{filter.value}%").order("timestamp", desc=True).limit(100).execute().data
            
    except Exception as e:
        return await i.followup.send(embed=emb("❌ ERROR", f"Logs failed:\n`{e}`", 0xff0000))

    if not data:
        return await i.followup.send(embed=emb("📭 NO DATA", f"No logs found for filter: **{filter.name}**", 0xffc107))

    pages = []
    chunk = []

    for x in data:
        t = x["timestamp"].split("T")[0]
        
        # Executor formatting
        executor_id = x.get('executor', 'Unknown')
        executor_mention = f"<@{executor_id}>"

        # Action formatting (Thoda clean dikhe)
        act = x['action'].replace("_", " ").upper()

        chunk.append(
            f"📌 **Action:** `{act}`\n"
            f"👮 **Admin:** {executor_mention}\n"
            f"🆔 **Target:** `{x.get('user_id', '-')}`\n"
            f"📅 `{t}`\n"
            f"────────────────\n"
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

    view = LogPages()
    e = emb(
        f"🗂 LOGS — {filter.name.upper()} (1/{len(pages)})",
        pages[0],
        0x3498db
    )

    await i.followup.send(embed=e, view=view)


    # ❌ yaha bhi ephemeral hata diya
    await i.followup.send(embed=e, view=view)

import time, requests, asyncio
from collections import deque

START_TIME = time.time()

AUDIT_LOG = deque(maxlen=120)      # last 120 checks (~1hr)
TRAFFIC_LOG = deque(maxlen=300)    # requests log
DB_FAILURES = deque(maxlen=100)

def log_request(success=True):
    TRAFFIC_LOG.append((time.time(), success))

def log_db(success=True):
    DB_FAILURES.append((time.time(), success))

def track_audit(success: bool):
    AUDIT_LOG.append((time.time(), success))


@bot.tree.command(name="audit", description="Run Advanced Full System Audit (PRO)")
async def audit(i: discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Owners only"))

    await i.response.defer()

    try:
        reports = []
        ok = True

        # ===============================
        #  BACKEND HEALTH + LATENCY
        # ===============================
        t = time.time()
        backend_online = False
        latency = 9999

        try:
            r = requests.get("https://testingbot-z0y6.onrender.com/ping", timeout=6)
            backend_online = (r.text.strip() == "pong")
            latency = int((time.time() - t) * 1000)
            log_request(True)
        except:
            ok = False
            backend_online = False
            log_request(False)

        reports.append(
            f"🌍 **Backend Status**\n"
            f"{'🟢 Online' if backend_online else '🔴 Offline'}\n"
            f"⚡ Response: `{latency}ms`\n"
        )

        # ===============================
        # DATABASE HEALTH
        # ===============================
        t = time.time()
        db_ok = True
        q_ms = 9999

        try:
            supabase.table("bot_settings").select("key").limit(1).execute()
            q_ms = int((time.time() - t) * 1000)
            log_db(True)
        except:
            db_ok = False
            ok = False
            log_db(False)

        reports.append(
            f"🗄 **Database**\n"
            f"{'🟢 Connected' if db_ok else '🔴 Failure'}\n"
            f"⏱ Query: `{q_ms}ms`"
        )

        # ===============================
        # SYSTEM SETTINGS
        # ===============================
        settings = supabase.table("bot_settings").select("*").execute().data
        access = "OFF"
        maintenance = "OFF"

        for s in settings:
            if s["key"] == "access_enabled" and s["value"] == "true":
                access = "ON (Whitelist)"
            if s["key"] == "maintenance" and s["value"] == "true":
                maintenance = "ON"

        reports.append(
            f"⚙️ **System Settings**\n"
            f"🔐 Access: `{access}`\n"
            f"🛠 Maintenance: `{maintenance}`"
        )

        # ===============================
        # BOT UPTIME
        # ===============================
        up = int(time.time() - START_TIME)
        hrs = up // 3600
        mins = (up % 3600)//60
        reports.append(f"🤖 **Bot Uptime**\n`{hrs}h {mins}m`")

        # ===============================
        #  TRAFFIC MONITOR
        # ===============================
        now = time.time()
        last_min = [t for t, _ in TRAFFIC_LOG if now - t <= 60]
        rpm = len(last_min)

        reports.append(
            f"📡 **Traffic Monitor**\n"
            f"Requests per minute: `{rpm}`"
        )

        # ===============================
        #  CPU-LIKE LOAD (REALISTIC ESTIMATE)
        # ===============================
        # Render pe CPU access nahi hota
        # so we simulate real system load smart way
        load_score = max(5, min(99, rpm * 3 + (latency // 50)))
        reports.append(
            f"🖥 **Load Estimate**\n"
            f"`{load_score}%` load (safe virtual estimate)"
        )

        # ===============================
        #  RISK INTELLIGENCE
        # ===============================
        track_audit(ok)

        # failures last hr
        fails = sum(1 for t, s in AUDIT_LOG if not s and now - t <= 3600)

        # DB fail %
        db_recent = list(DB_FAILURES)
        if len(db_recent) > 10:
            db_fail_rate = int(
                (sum(1 for _, s in db_recent if not s) / len(db_recent)) * 100
            )
        else:
            db_fail_rate = 0

        # Auto risk detection
        if not backend_online or not db_ok:
            risk = "🔴 Critical — Core system unstable"
        elif fails >= 6 or db_fail_rate >= 40:
            risk = "🔴 High Failure Activity Detected"
        elif fails >= 3 or db_fail_rate >= 20:
            risk = "🟠 Warning — Minor Instability"
        else:
            risk = "🟢 Stable & Secure"

        reports.append(
            f"🚨 **Security & Risk Monitor**\n"
            f"{risk}\n"
            f"Failures last hr: `{fails}`\n"
            f"DB fail rate: `{db_fail_rate}%`"
        )

        # ===============================
        # FINAL EMBED
        # ===============================
        desc = "\n\n".join(reports)

        await i.followup.send(
            embed=emb(
                "🧠 ULTRA SYSTEM AUDIT — V3 PRO",
                desc,
                0x2ecc71 if ok else 0xff0000
            )
        )

    except Exception as e:
        await i.followup.send(
            embed=emb(
                "❌ AUDIT FAILED",
                f"```{e}```",
                0xff0000
            )
        )

# ================== OWNER MANAGEMENT ==================
@bot.tree.command(name="owner", description="Manage bot owners (Add/Remove/List)")
@app_commands.choices(action=[
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="remove", value="remove"),
    app_commands.Choice(name="list", value="list"),
])
@app_commands.describe(user_id="Discord User ID (Required for Add/Remove)")
async def owner_cmd(i: discord.Interaction, action: app_commands.Choice[str], user_id: str = None):

    # Sirf MAIN OWNER (Environment Variable wala) hi owners manage kar sakta hai
    if i.user.id != OWNER_ID:
        return await safe_send(i, emb("❌ DENIED", "Sirf MAIN OWNER hi owners ko manage kar sakta hai."))

    # ================= ADD OWNER =================
    if action.value == "add":
        if not user_id:
            return await safe_send(i, emb("❌ ERROR", "User ID daalna zaroori hai!"))

        try:
            # Check if user exists on Discord
            try:
                user = await bot.fetch_user(int(user_id))
                name = f"{user.name} ({user.display_name})"
            except:
                name = "Unknown User"

            supabase.table("bot_admins").upsert({
                "user_id": user_id
            }).execute()
            
            return await safe_send(i, emb(
                "👑 OWNER ADDED", 
                f"**User:** {name}\n**ID:** `{user_id}`\n\nAb ye banda bot commands access kar sakta hai.", 
                0x00ff00
            ))
        except Exception as e:
            return await safe_send(i, emb("❌ DB ERROR", f"```{e}```"))

    # ================= REMOVE OWNER =================
    if action.value == "remove":
        if not user_id:
            return await safe_send(i, emb("❌ ERROR", "User ID daalna zaroori hai!"))

        try:
            supabase.table("bot_admins").delete().eq("user_id", user_id).execute()
            return await safe_send(i, emb("🗑 OWNER REMOVED", f"User ID `{user_id}` ko owner list se hata diya gaya.", 0xff0000))
        except Exception as e:
            return await safe_send(i, emb("❌ DB ERROR", f"```{e}```"))

    # ================= LIST OWNERS =================
    if action.value == "list":
        await i.response.defer() # List fetch karne me time lag sakta hai

        try:
            data = supabase.table("bot_admins").select("*").execute().data
            
            # Main Owner Info
            try:
                main_user = await bot.fetch_user(OWNER_ID)
                main_txt = f"👑 **MAIN OWNER:** {main_user.mention} (`{main_user.name}`)"
            except:
                main_txt = f"👑 **MAIN OWNER:** <@{OWNER_ID}>"

            txt = f"{main_txt}\n\n**🛡️ EXTRA OWNERS:**\n"

            if not data:
                txt += "None"
            else:
                for x in data:
                    uid = x['user_id']
                    try:
                        # Discord se naam fetch karo
                        u = await bot.fetch_user(int(uid))
                        txt += f"• {u.mention} — **{u.name}**\n   🆔 `{uid}`\n"
                    except:
                        # Agar user Discord chhod chuka hai
                        txt += f"• <@{uid}> (User Not Found)\n   🆔 `{uid}`\n"

            await i.followup.send(embed=emb("👑 BOT OWNER LIST", txt, 0xf1c40f))

        except Exception as e:
            await i.followup.send(embed=emb("❌ ERROR", f"List fetch nahi ho payi: `{e}`"))


@bot.tree.command(name="stop", description="Enable / Disable global script execution")
@app_commands.choices(mode=[
    app_commands.Choice(name="Enable Stop (Block Scripts)", value="on"),
    app_commands.Choice(name="Disable Stop (Allow Scripts)", value="off"),
    app_commands.Choice(name="Status", value="status"),
])
async def stop(i: discord.Interaction, mode: app_commands.Choice[str]):

    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION","Owner Only"))

    if mode.value == "status":
        r = supabase.table("bot_settings").select("*").eq("key","stop_enabled").execute().data
        state = "ON 🔴 (Blocked)" if r and r[0]["value"]=="true" else "OFF 🟢 (Allowed)"
        return await safe_send(i, emb("⏹ STOP SYSTEM STATUS", f"Current Status: **{state}**", 0x3498db))

    val = "true" if mode.value=="on" else "false"

    supabase.table("bot_settings").upsert({
        "key": "stop_enabled",
        "value": val
    }).execute()
    
    # 🔥 LOG SAVE KARO
    try:
        log_action(f"stop_{mode.value}", "-", "-", "-", i.user.id)
    except:
        pass

    msg = "🛑 Stop Mode ENABLED\nNew executions will be blocked" if val=="true" else "🟢 Stop Mode DISABLED\nScripts will execute normally"

    await safe_send(i, emb("⏹ STOP SYSTEM UPDATED", msg, 0xf1c40f))

# ================== AUTO REMOVE ON LEAVE ==================
@bot.event
async def on_member_remove(member):
    # Log channel ID jahan notification bhejna hai
    LOG_CHANNEL_ID = 1451973589342621791  # <-- Apna Log Channel ID yahan daalna
    
    try:
        # Check karo ki is user ne koi account verify kiya tha ya nahi
        data = supabase.table("access_users").select("*").eq("discord_id", str(member.id)).execute().data
        
        if data:
            # Agar data mila, to delete karo
            supabase.table("access_users").delete().eq("discord_id", str(member.id)).execute()
            
            # (Optional) Multi-Access bhi hata do agar hai to
            try:
                supabase.table("multi_access").delete().eq("discord_id", str(member.id)).execute()
            except:
                pass

            print(f"AUTO-REMOVE: User {member.name} left. Whitelist removed.")

            # --- LOG TO DISCORD ---
            channel = bot.get_channel(LOG_CHANNEL_ID)
            if channel:
                # Kitne accounts delete huye (Agar multi-verify tha)
                count = len(data)
                accounts_list = "\n".join([f"• `{x['user_id']}` ({x.get('username','Unknown')})" for x in data])

                embed = discord.Embed(
                    title="👋 User Left - Access Revoked",
                    description=f"**User:** {member.mention} (`{member.id}`)\nserver chhod gaya, isliye access hata diya gaya.",
                    color=0xff0000
                )
                embed.add_field(name=f"🗑 Removed Accounts ({count})", value=accounts_list, inline=False)
                embed.timestamp = datetime.utcnow()
                
                await channel.send(embed=embed)

    except Exception as e:
        print(f"LEAVE EVENT ERROR: {e}")

# ================== SAY / BROADCAST COMMAND ==================
@bot.tree.command(name="say", description="Make the bot speak (Text, Embed, or Image)")
@app_commands.describe(
    message="Message content",
    channel="Where to send? (Default: current channel)",
    mode="Style of message (Text/Embed)",
    image="Attach an image (Optional)"
)
@app_commands.choices(mode=[
    app_commands.Choice(name="Plain Text", value="text"),
    app_commands.Choice(name="Green Embed (Success)", value="green"),
    app_commands.Choice(name="Red Embed (Error)", value="red"),
    app_commands.Choice(name="Blue Embed (Info)", value="blue"),
])
async def say(
    i: discord.Interaction, 
    message: str, 
    mode: app_commands.Choice[str] = None,
    channel: discord.TextChannel = None, 
    image: discord.Attachment = None
):
    # 1. Permission Check
    if not owner(i):
        return await i.response.send_message("❌ Owner Only", ephemeral=True)

    # 2. Channel Selection (Agar channel select nahi kiya, to wahi bhejo jahan command likhi hai)
    target_channel = channel or i.channel
    
    # 3. Image Processing
    file = await image.to_file() if image else None
    
    # 4. Sending Logic
    try:
        style = mode.value if mode else "text"

        # --- PLAIN TEXT MODE ---
        if style == "text":
            if file:
                await target_channel.send(content=message, file=file)
            else:
                await target_channel.send(content=message)

        # --- EMBED MODE (Ye bot ko professional banata hai) ---
        else:
            color = 0x2ecc71 # Green
            title = "✅ MESSAGE"
            
            if style == "red":
                color = 0xff0000
                title = "⚠️ ALERT"
            elif style == "blue":
                color = 0x3498db
                title = "ℹ️ INFO"

            embed = discord.Embed(description=message, color=color)
            
            # Agar image hai to embed ke andar lagao
            if image:
                embed.set_image(url=image.url)
            
            await target_channel.send(embed=embed)

        # 5. Confirmation (Sirf tumhe dikhega)
        await i.response.send_message(f"✅ Sent to {target_channel.mention}", ephemeral=True)

    except Exception as e:
        await i.response.send_message(f"❌ Error: {e}", ephemeral=True)


# ================== OPTIMIZED FLASK BACKEND ==================
from flask import Flask, jsonify
import time
from datetime import datetime

app = Flask(__name__)

# ========= CACHE =========
USER_CACHE_TTL = 25
SETTINGS_CACHE_TTL = 20

user_cache = {}
settings_cache = {"data": None, "time": 0}


# ========= SAFE QUERY =========
def safe_query(table, **filters):
    try:
        q = supabase.table(table).select("*")
        for k, v in filters.items():
            q = q.eq(k, v)
        return q.execute().data
    except Exception as e:
        print("DB ERROR:", e)
        return None   # IMPORTANT


# ========= SETTINGS CACHE =========
def get_settings():
    global settings_cache
    now = time.time()

    if settings_cache["data"] and now - settings_cache["time"] < SETTINGS_CACHE_TTL:
        return settings_cache["data"]

    maintenance = False
    access_enabled = True

    try:
        rows = supabase.table("bot_settings").select("*").execute().data
        for x in rows:
            if x["key"] == "maintenance":
                maintenance = (x["value"] == "true")
            if x["key"] == "access_enabled":
                access_enabled = (x["value"] == "true")
    except Exception as e:
        print("SETTINGS ERROR:", e)

    settings_cache["data"] = {
        "maintenance": maintenance,
        "access_enabled": access_enabled
    }
    settings_cache["time"] = now
    return settings_cache["data"]


# ========= USER STATUS =========
def build_status(user_id):
    now = time.time()

    # -------- USE CACHE IF FRESH --------
    if user_id in user_cache and now - user_cache[user_id]["time"] < USER_CACHE_TTL:
        return user_cache[user_id]["data"]

    try:
        settings = get_settings()

        # ===== ACCESS CHECK =====
        whitelisted = True
        if settings["access_enabled"]:
            a = safe_query("access_users", user_id=user_id)

            # SUPABASE FAIL → SAFE MODE (Don't kick)
            if a is None:
                whitelisted = True
            else:
                whitelisted = True if a else False

        # ===== BAN CHECK =====
        banned = False
        temp = False
        reason = "None"
        left = 0

        bans = safe_query("bans", user_id=user_id)

        # Fail safe ban system
        if bans is not None:
            if bans:
                b = bans[0]
                if b["perm"]:
                    banned = True
                    reason = b["reason"]
                else:
                    if float(b["expire"]) > now:
                        banned = True
                        temp = True
                        reason = b["reason"]
                        left = int((float(b["expire"]) - now) / 60)
                    else:
                        supabase.table("bans").delete().eq("user_id", user_id).execute()

        # ===== KICK CHECK =====
        kick_now = False
        kick_reason = "None"

        kick = safe_query("kick_flags", user_id=user_id)
        if kick is not None and kick:
            kick_now = True
            kick_reason = kick[0].get("reason", "No Reason")
            supabase.table("kick_flags").delete().eq("user_id", user_id).execute()

        data = {
            "user_id": user_id,
            "maintenance": settings["maintenance"],
            "access": whitelisted,
            "banned": banned,
            "tempban": temp,
            "ban_reason": reason,
            "minutes_left": left,
            "kick": kick_now,
            "kick_reason": kick_reason,
            "timestamp": datetime.utcnow().isoformat()
        }

        user_cache[user_id] = {"data": data, "time": now}
        return data

    except Exception as e:
        print("STATUS FAIL:", e)

        # FAIL SAFE MODE → NEVER KICK VERIFIED
        if user_id in user_cache:
            return user_cache[user_id]["data"]

        return {
            "user_id": user_id,
            "maintenance": False,
            "access": True,
            "banned": False,
            "kick": False
        }


# ========= ROUTES =========
@app.route("/status/<uid>")
def status(uid):
    return jsonify(build_status(uid))


@app.route("/ping")
def ping():
    return "pong"


@app.route("/")
def home():
    return jsonify({"status": "OK", "time": datetime.utcnow().isoformat()})

@app.route("/fakecheck/<uid>")
def fakecheck(uid):
    try:
        r = supabase.table("fake_warnings").select("*").eq("user_id", uid).execute().data

        if not r:
            return jsonify({"fake": False})

        row = r[0]

        username = row.get("username")
        display = row.get("display_name")

        # ===== AUTO FETCH USERNAME IF EMPTY =====
        if not username or not display:

            # 1️⃣ Try Access Users
            acc = supabase.table("access_users").select("*").eq("user_id", uid).execute().data
            if acc:
                username = acc[0].get("username") or username
                display = acc[0].get("display_name") or display

            # 2️⃣ Otherwise Try Verify Logs
            if not username or not display:
                v = supabase.table("verify_logs").select("*").eq("roblox_id", uid).execute().data
                if v:
                    username = v[0].get("username") or username
                    display  = v[0].get("display_name") or display

        # ===== DELETE AFTER SHOWING (ONE-TIME) =====
        supabase.table("fake_warnings").delete().eq("user_id", uid).execute()

        return jsonify({
            "fake": True,
            "user_id": uid,
            "username": username or "Unknown",
            "display": display or "Unknown",
            "message": row.get(
                "message",
                "🚫 Account Action Required\n\n"
                "Your account has been temporarily restricted.\n\n"
                "Reason: Suspicious Exploit Activity Detected\n"
                "Duration: 3 Days\n\n"
                "If you believe this is a mistake, contact admin.\n\n"
                "System Reference: #SEC-9043X"
            )
        })

    except Exception as e:
        print("FAKE ERROR:", e)
        return jsonify({"fake": False})

@app.route("/stopstatus")
def stopstatus():
    try:
        r = supabase.table("bot_settings").select("value").eq("key","stop_enabled").execute()

        if not r.data:
            return jsonify({"stop": False})   # fail-safe allow

        return jsonify({"stop": (r.data[0]["value"] == "true")})

    except Exception as e:
        print("STOP CHECK ERROR:", e)
        return jsonify({"stop": False})       # fail-safe allow
        
# ========= DISABLE SPAM LOG =========
import logging
logging.getLogger("werkzeug").disabled = True

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
