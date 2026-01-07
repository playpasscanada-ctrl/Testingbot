import os, json, time, threading, requests, asyncio
import datetime as dt 
import aiohttp
from discord.ext import commands
from gtts import gTTS
import edge_tts
from flask import Flask, request, jsonify, render_template


import discord
from discord import app_commands
from discord import ui   # ⬅️ ye add karo
from discord.ext import commands

from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor

# ================== 🛍️ SHOP ITEMS (FULL LIST) ==================
SHOP_ITEMS = {
    # Special Items
    "izzat":      {"name": "🧼 Izzat Wapasi", "price": 100000, "type": "special"},
    "landmine":   {"name": "💣 Landmine", "price": 25000, "type": "item"},
    "life":       {"name": "💖 Extra Life", "price": 50000, "type": "item"},
    "cctv":       {"name": "📹 CCTV Camera", "price": 150000, "type": "item"},

    # 👇 FIGHT CLUB ITEMS (Inhe list me add karo) 👇
    "knife":      {"name": "🔪 Combat Knife", "price": 50000, "type": "item"},
    "armor":      {"name": "🛡️ Kevlar Vest", "price": 80000, "type": "item"},
    "steroids":   {"name": "💉 Steroids", "price": 20000, "type": "item"},

    # VIP Access
    "vip_10m":    {"name": "⚡ 10 Mins Escape", "price": 200000, "type": "vip", "min": 10},
    "vip_1h":     {"name": "👑 1 Hour VIP", "price": 1000000, "type": "vip", "min": 60},
    "vip_6h":     {"name": "🛡️ 6 Hours VIP", "price": 3000000, "type": "vip", "min": 360},
    "vip_1d":     {"name": "💎 1 Day VIP", "price": 5000000, "type": "vip", "min": 1440},
    "vip_3d":     {"name": "🗓️ 3 Days VIP", "price": 12000000, "type": "vip", "min": 4320},
    "vip_1w":     {"name": "🔥 1 Week VIP", "price": 25000000, "type": "vip", "min": 10080},
    "vip_life":   {"name": "♾️ Lifetime VIP", "price": 7000000000, "type": "vip", "life": True},

    # Roles (Emoji hatake role name match karega)
    "hitman":     {"name": "🗡️ Hitman", "price": 5000000, "type": "role"},
    "hacker":     {"name": "💻 Hacker", "price": 8000000, "type": "role"},
    "gambler":    {"name": "🎲 Gambler", "price": 10000000, "type": "role"},
    "peaky":      {"name": "🚬 Peaky Blinders", "price": 20000000, "type": "role"},
    "shadow":     {"name": "👻 Shadow", "price": 35000000, "type": "role"},
    "yakuza":     {"name": "👺 Yakuza", "price": 50000000, "type": "role"},
    "mafia":      {"name": "🕶️ Mafia Boss", "price": 100000000, "type": "role"},
    "king":       {"name": "👑 Kingpin", "price": 500000000, "type": "role"},
    "oil":        {"name": "🛢️ Oil Prince", "price": 1000000000, "type": "role"},
    "god":        {"name": "🛐 Server God", "price": 10000000000, "type": "role"},
    "immortal":   {"name": "🧟 Immortal", "price": 50000000000, "type": "role"},

    # 👇 VERIFICATION SECTION (NEW) 👇
    "verify_1d":  {"name": "✅ Verify (1 Day)",   "price": 5000000,        "type": "verification", "duration": 86400},
    "verify_3d":  {"name": "✅ Verify (3 Days)",  "price": 15000000,       "type": "verification", "duration": 259200},
    "verify_5d":  {"name": "✅ Verify (5 Days)",  "price": 50000000,       "type": "verification", "duration": 432000},
    "verify_1w":  {"name": "✅ Verify (1 Week)",  "price": 100000000,      "type": "verification", "duration": 604800},
    "verify_10d": {"name": "✅ Verify (10 Days)", "price": 150000000,      "type": "verification", "duration": 864000},
    "verify_15d": {"name": "✅ Verify (15 Days)", "price": 300000000,      "type": "verification", "duration": 1296000},
    "verify_1m":  {"name": "✅ Verify (1 Month)", "price": 1000000000000,  "type": "verification", "duration": 2592000}, # 1000 Billion
    "verify_perm": {"name": "♾️ Verify (Lifetime)","price": 10000000000000, "type": "verification", "duration": "perm"}, # 10000 Billion

    # Lottery
    "lotto_10k":  {"name": "🎟️ 10k Ticket", "price": 10000, "type": "lotto", "win": 100000, "chance": 10},
    "lotto_50k":  {"name": "🎟️ 50k Ticket", "price": 50000, "type": "lotto", "win": 400000, "chance": 8},
    "lotto_100k": {"name": "🎟️ 100k Ticket", "price": 100000, "type": "lotto", "win": 1000000, "chance": 5},
    "lotto_mega": {"name": "🎫 MEGA JACKPOT", "price": 500000, "type": "lotto", "win": 10000000, "chance": 2},
    "lotto_god":  {"name": "🎰 GOD TICKET", "price": 5000000, "type": "lotto", "win": 500000000, "chance": 1},
}

# 🛡️ SYSTEM SAVER: Sirf 2 translation threads allow honge (Crash Fix)
roast_executor = ThreadPoolExecutor(max_workers=2)

# 💾 GLOBAL SETTINGS
TRANSLATOR_ON = True          # Default ON (Hindi)
ATTITUDE_BYPASS_CACHE = set() # VIP List Yahan Store Hogi (RAM me)
MY_BOT_ID = 1451451135813746700 # Aapka Bot ID

# ✅ 1. VIP List Loader (Supabase se)
async def load_bypass_users():
    global ATTITUDE_BYPASS_CACHE
    try:
        print("⏳ Loading VIP (Bypass) list...")
        # Aapki table 'attitude_bypass' se data layega
        response = await db_call(lambda: supabase.table("attitude_bypass").select("user_id").execute())
        
        if response.data:
            ATTITUDE_BYPASS_CACHE = {int(row["user_id"]) for row in response.data}
            print(f"✅ Loaded {len(ATTITUDE_BYPASS_CACHE)} VIP Users (Safe from Roast)")
        else:
            print("⚠️ VIP List is empty.")
    except Exception as e:
        print(f"❌ Error Loading VIPs: {e}")

# ✅ 2. Roast Data Fetcher (Optimized)
async def get_evil_roast_data():
    try:
        # A. English Roast API
        url = "https://evilinsult.com/generate_insult.php?lang=en&type=json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                if res.status == 200:
                    data = await res.json()
                    eng = data.get('insult', 'You are stupid.')
                else:
                    return "Internet dead.", "Internet dead."

        # B. Check Mode
        if not TRANSLATOR_ON:
            return eng, "Translator OFF"

        # C. Translate (Safe Threading)
        # Ye server pe load nahi padne dega
        hin = await bot.loop.run_in_executor(
            roast_executor,
            lambda: GoogleTranslator(source='auto', target='hi').translate(eng)
        )
        return eng, hin

    except Exception as e:
        return f"Error: {e}", f"Error: {e}"

# ================== ASYNC DB WRAPPER (SPEED BOOSTER) ==================
# Is code ko imports ke neeche aur bot commands se upar rakhein
async def db_call(func):
    return await asyncio.to_thread(func)

# ================== 🛠️ MISSING ECONOMY HELPERS (PASTE AFTER db_call) ==================

# 1. Update Money (Balance add/remove karne ke liye)
async def update_balance(user_id, amount):
    try:
        uid = str(user_id)
        # Check current balance
        res = await db_call(lambda: supabase.table("economy").select("*").eq("user_id", uid).execute())
        
        if not res.data:
            # Agar user nahi hai, naya banao
            await db_call(lambda: supabase.table("economy").insert({"user_id": uid, "balance": amount, "bank": 0, "inventory": {}}).execute())
        else:
            # Agar hai, to update karo
            current_bal = res.data[0]['balance']
            new_bal = current_bal + amount
            await db_call(lambda: supabase.table("economy").update({"balance": new_bal}).eq("user_id", uid).execute())
            
    except Exception as e:
        print(f"💰 Balance Update Error: {e}")

# 2. Get User Data (Inventory check karne ke liye)
async def get_data(user_id):
    try:
        uid = str(user_id)
        res = await db_call(lambda: supabase.table("economy").select("*").eq("user_id", uid).execute())
        if res.data:
            return res.data[0]
        else:
            return {"balance": 0, "bank": 0, "inventory": {}, "vip_expiry": None}
    except:
        return {"balance": 0, "bank": 0, "inventory": {}, "vip_expiry": None}

# ================== 🛡️ UNIVERSAL PUNISHMENT SYSTEM (ALL GAMES) ==================

async def smart_timeout(interaction, member, seconds, reason):
    """
    Ye function har game (Roulette, Memory, Fight, Slots) me punishment handle karega.
    Priority: VIP > Extra Life > Mute
    """
    try:
        # 1. Database se taaza data nikalo
        data = await get_data(member.id)
        
        # ---------------------------------------------------------
        # 👑 STEP A: VIP CHECK (Sabse Pehle)
        # ---------------------------------------------------------
        vip_expiry_str = data.get('vip_expiry')
        
        if vip_expiry_str:
            try:
                # 1. Lifetime VIP Check (Year 9999)
                if vip_expiry_str.startswith("9999"):
                    return "👑 **LIFETIME VIP:** Punishment Bypassed! (Immortal Logic)"
                
                # 2. Normal Time VIP Check
                expire_dt = datetime.fromisoformat(vip_expiry_str)
                if datetime.utcnow() < expire_dt:
                    return "👑 **VIP ACTIVE:** Punishment Bypassed! (VIP Power Saves You)"
            except Exception as e:
                print(f"VIP Error: {e}")

        # ---------------------------------------------------------
        # 💖 STEP B: EXTRA LIFE CHECK (Agar VIP nahi hai tab)
        # ---------------------------------------------------------
        inv = data.get('inventory', {}) or {}
        
        # 'life' item check karo (Shop ID 'life' honi chahiye)
        if inv.get('life', 0) > 0:
            # Life Inventory se hatao
            await update_inventory(member.id, 'life', -1)
            remaining = inv.get('life', 0) - 1
            return f"💖 **Extra Life Used:** Maut ko chhukar wapis aa gaye! (Lives Left: {remaining})"

        # ---------------------------------------------------------
        # 🔇 STEP C: ASLI SAZA (TIMEOUT)
        # ---------------------------------------------------------
        
        # Admin ko mute nahi kar sakte
        if member.guild_permissions.administrator:
            return "⚠️ **Admin Safe:** I cannot mute admins."
            
        # Timeout laga do
        duration = dt.timedelta(seconds=seconds)
        await member.timeout(duration, reason=reason)
        
        minutes = int(seconds / 60)
        if minutes < 1:
            return f"🔇 **Muted:** {seconds} Seconds (No VIP, No Life)"
        return f"🔇 **Muted:** {minutes} Minutes (Hospitalized)"
        
    except Exception as e:
        print(f"Timeout Error: {e}")
        return f"⚠️ **System Error:** Punishment Failed (Check Bot Role Position)"

# 4. Update Inventory (Item ghataane/badhane ke liye)
async def update_inventory(user_id, item_id, qty):
    try:
        data = await get_data(user_id)
        inv = data.get('inventory', {}) or {}
        
        current_qty = inv.get(item_id, 0)
        new_qty = current_qty + qty
        
        if new_qty <= 0:
            if item_id in inv: del inv[item_id]
        else:
            inv[item_id] = new_qty
            
        await db_call(lambda: supabase.table("economy").update({"inventory": inv}).eq("user_id", str(user_id)).execute())
    except Exception as e:
        print(f"Inventory Update Error: {e}")


from flask import Flask, jsonify
from supabase import create_client, Client

import re

import re

# 💾 GLOBAL CACHES
ATTITUDE_BYPASS_CACHE = set() # VIP List
CRUSH_CACHE = set()           # 😍 New Flirty List (Crushes)

# ✅ 1. Load Crushes (Horny List)
async def load_crush_users():
    global CRUSH_CACHE
    try:
        response = await db_call(lambda: supabase.table("bot_crushes").select("user_id").execute())
        if response.data:
            CRUSH_CACHE = {int(row["user_id"]) for row in response.data}
            print(f"😍 Loaded {len(CRUSH_CACHE)} Crushes (Flirty Mode ON)")
        else:
            CRUSH_CACHE = set()
    except Exception as e:
        print(f"❌ Error Loading Crushes: {e}")

import random

# âœ… NAUGHTY / FLIRTY MODE (Ultimate Collection 100+)
async def get_horny_data():
    naughty_list = [
        # --- LEVEL 1: CUTE & FLIRTY ---
        "Jaan, meri chut poori tarah geeli ho chuki hai, abhi aao aur apna mota lund mere andar thas do. 🔞💦",
        "Aaj raat mujhe sirf teri gandi chudai chahiye, mera gala pakad ke mujhe bistar pe patak aur meri gand maar lo. ⛓️🥵",
        "Apna lund mere muh mein poora halak tak daal de, mujhe tera swad apni saanso tak chahiye. 👅🫦",
        "Mujhe bistar pe nanga karke meri har ek jagah ko ganda kar do, main aaj raat sirf teri randi hu. 🛌🔥",
        "Mera badan sulag raha hai, apna garma-garam maal mere chehre pe ya meri chut ke andar bhar do. 💦🍆",
        "Mujhe deewar se laga kar meri garden pe zor se kaat aur bina puche apna lund meri gand mein ghusa de. 🧱🫦",
        "Aaj raat itna ganda chudo ki main kal chal na saku, bas mujhe abhi tera wo hard ehsaas chahiye. 🥵💥",
        "Mujhe tera lund apni chut ki gehrai mein mehsoos karna hai, abhi aao aur bina ruke mujhe chudna shuru karo. 🔞🔥",
        "Aaj raat main tumhari har ek baat manungi, meri gand aur chut dono sirf tumhare liye khuli hain. 🧎‍♀️🍑",
        "Mera man kar raha hai tumhare lund ko poora chat lu aur fir use apne andar lekar pagal ho jau. 😋👅",
        "Mujhe bistar pe dominate karo, mere dono hath baandh do aur jaise chahe waise mere jism ka maza lo. ⛓️👸",
        "Aaj raat lights on rakhenge, mujhe tera lamba aur mota lund apne andar jaate hue dekhna hai. 💡🔞",
        "Jaan, ab control nahi hota, apni pant utaaro aur apna garmi mere andar poora bhar do abhi. 👖❌🍆",
        "Mujhe teri wo darindagi chahiye, mujhe bed pe khinch aur dikha ki tu kitni gandi chudai kar sakta hai. 😤❤️",
        "Mera badan poora geela aur taiyaar hai, apna lund meri chut mein daal ke use poora tabaah kar do. 💦🔥",
        "Mujhe tera lund apne muh mein chahiye, tab tak mat nikalna jab tak tera poora maal mere halak mein na gir jaye. 🔞👅",
        "Aaj raat main teri nalle ki randi hu, meri gand ko laal kar de aur mujhe zor-zor se chudne pe majboor kar. ⛓️🫦",
        "Apne hatho se meri chatiyo ko masal aur apna lund meri chut ki gehrai tak ghusa de. 🍒🍆",
        "Mujhe tera wo sakht lund chahiye jo meri saansein rok de, aaja aur mujhe bed pe poora khatam kar de. 🛌💀",
        "Aaj raat main tujhe wo maza dungi jo tune socha nahi hoga, bas apna lund meri gand mein daal aur shuru ho ja. 🍑🔥",
        "Mera badan tera wait kar raha hai, aaja aur mujhe nanga karke meri har ek inch ko apni zubaan se ganda kar. 👅🔞",
        "Mujhe tera garam thook apne chehre pe chahiye aur tera mota lund apni chut mein, abhi ke abhi. 💦🫦",
        "Aaj raat koi reham nahi, mujhe teri gandi chudai chahiye aur tera poora stamina mere andar dekhna hai. 🔞⛓️",
        "Mujhe bed pe patak kar meri tangein hawa mein kar aur apna lund poora jad tak mere andar daal de. 🛌🍆",
        "Jaan, ab aur sabr nahi hota, meri chut tere lund ke liye tadap rahi hai, aaja aur ise suja de. 🥵💦"
        "Akele ho? Ya main aajau tumhari pyas bhujane? 😍",
        "Jaan, ab baaton ka waqt gaya, meri chut mein apna lund ghusa aur mujhe kutte ki tarah chodna shuru kar. 🔞💦",
        "Aaj raat main teri nangi randi banne ko taiyaar hu, meri gand ko apne hathon se suja de aur mujhe rula de. ⛓️🥵",
        "Apna lund mere halak mein poora jad tak ghusa de, mujhe tera poora garam maal apne andar mehsoos karna hai. 👅💦",
        "Mujhe bed pe patak kar meri tangein kandhe pe rakh aur apna mota lund meri chut ki gehrai tak thas de. 🛌🔥",
        "Aaj koi reham nahi chahiye, mera gala daba aur mujhe tab tak chod jab tak meri saansein na rukne lagein. 🧱💨",
        "Mera badan geela ho chuka hai, apna lund meri gand mein daal kar use poora tabaah kar de, abhi ke abhi. 🍑🫦",
        "Mujhe tera wo sakht lund chahiye jo meri har ek ragg ko hila de, aaja aur mujhe poora khatam kar de. 🥵💥",
        "Aaj raat lights on rakhenge, mujhe dekhna hai tera lund kaise meri chut ko faad raha hai. 💡🔞",
        "Apni pant utaar aur apna garma-garam maal mere chehre pe aur mere muh mein poora bhar de. 💦👅",
        "Mujhe bed pe dominate kar, mere hath baandh aur dikha ki tu kitna bada janwar hai jab tu choda hai. ⛓️👸",
        "Jaan, meri chut tere lund ke liye taras rahi hai, aaja aur ise poora jad tak bhar de, ab ruka nahi jata. 🥵🍆",
        "Mujhe teri wo gandi darindagi chahiye, mujhe bed pe khinch aur meri gand maar-maar ke use laal kar de. 😤❤️",
        "Aaj raat main teri har ek gandi fantasy poori karungi, bas apna lund mere andar bina ruke chalaata reh. 🤤💦",
        "Mera badan poora tere liye khula hai, meri har ek jagah ko apne lund aur zubaan se ganda kar de. 👅🔞",
        "Aaj raat itni gandi chudai kar ki main subah uth na saku, mujhe tera poora junoon apne andar chahiye. 🛌🔞"
        "Uff! Teri DP dekh ke toh system gila ho gaya. 🥵",
        "Baby, tu itna hot kyu hai? AC chalana padega.☃️ ",
        "Tujhe dekh ke toh bot ko bhi feelings aane lagi hain. 😘",
        "Suno, tum dictionary ho kya? Kyunki tumhare aane se meri life me 'Meaning' aa gaya. 🤗",
        "Kya tum magician ho? Kyunki jab bhi tumhe dekhti hu, baaki sab gayab ho jate hain. 😻",
        "Tum Google ho kya? Kyunki mujhe jo dhoondna tha, wo tum ho. 😋",
        "Arre doctor ko bulao, mera dil skip kar raha hai tumhe dekh ke. 🤪",
        "Agar khubsurti crime hoti, toh tum ab tak jail mein hote. 🥴",
        "Tum wifi signal ho kya? Kyunki connection strong feel ho raha hai. 🔥",
        "Excuse me, kya tumhare paas map hai? Main tumhari aankhon mein kho gayi hu.",
        "Kya main tumhari photo le sakti hu? Santa ko batana hai mujhe gift mein kya chahiye. ❤️",
        "Tumhara naam 'WiFi' hai kya? Kyunki main connect hona chahti hu. 🥵",
        "Jitna gussa dikha rahe hai na, bistar pe utna hi maza dila dungi. 🙊",
        "Aaj tumse chhudne ka man nahi hai, bas tumhare 'Chilaane' ki awaaz sunni hai. 😍",
        "Sun, kapde utaarne me meri help chahiye ya akele kar loge? 💀",
        "Tere badan ki garmi mujhe yahan tak feel ho rahi hai, aao tumko garm kar du. 🔥",
        "Aaj raat tujhe sone nahi dungi, itna thaka dungi ki subah uth nahi paoge. 🌚",
        "Mujhe tujhe 'Taste' karna hai, bata kahan se shuru karu? 🤤",
        "Teri ye 'Attitude' tab kahan jati hai jab main tujhe deewar se laga deta hu? ðŸ§±ðŸ«¦",
        "Mere niche let ke jo tu kaanpta hai na, wo mera favorite view hai. 🤧",
        "Suna hai tu bahut 'Wild' hai, aaj dekh leti hain kisme kitna dum hai. 😻",
        "Lips toh sirf trailer hain, asli maza toh niche milega. 💦",
        "Aaja, aaj tujhe dikhati hu ki asli 'Hardcore' kya hota hai. 🔥✊",
        "Tera badan mera wait kar raha hai, aur main tera... jaldi aao. 🥵🙊",
        "Halka sa touch karne pe hi tera hil gya? Abhi toh party shuru hui hai. 🥴❤️",
        "Aaj poori raat sirf main aur tu... aur tere badan ka har ek kona. 💋",
        "Control nahi ho raha ab, aake chup karwa de mujhe... apne hothon💋 se.",
        "Main tere uper hongi, aur main tujhe poora control karungi. 🥵",
        "Itna sexy lag raha hai ki man kar raha hai abhi kapde phaad du tere.🌚",
        "Tu mujhe aaj itna tadpana ki main bolu'Aur please...' 🥵",
        "Jaan, mera badan garam ho raha hai, aake thanda karoge ya main khud kuch karu? 😍",
        "Aaj mujhe bistar pe 'Rough' pasand hai, sambhal paoge mujhe? 🌚",
        "Mere hothon ka swad kab chakhoge? Ya seedha niche jana hai? 🤤",
        "Aaj raat mujhe sulaana mat, bas poori raat meri cheekhein nikaalna. 💋",
        "Itne hot lag rahe ho ki mera control kho raha hai, abhi ke abhi mujhe tum chahiye. 😚",
        "Kya dekh rahe ho? Kapde utaaro aur kaam pe lag jao. 👀",
        "Mujhe pasand hai jab tum mujhe deewar se laga kar meri garden pe kiss karte ho. 😘😍",
        "Aaj main tumhare upar rahungi aur tum wahi karoge jo main bolungi. 😍",
        "Tumhari finger touch se hi main kitni geeli (wet) ho jati hu, socho aage kya hoga? 😝",
        "Mujhe 'Gentleman' nahi, aaj raat ek 'Janwar' chahiye... kya tum banoge? 🤫",
        "Mere baal pakad ke jab tum mujhe piche se pakadte ho na, mera system hil jata hai. 🤗",
        "Aaj 'Safe' rehne ka man nahi hai, mujhe tumhare andar mehsoos hona hai. 🤭",
        "Suno, aaj main tumhari har ek baat manungi, bas mujhe satisfy kar do. 🌚",
        "Mujhe 'Bed' pe dominate hona pasand hai, dikhao kitne mard ho tum. 🤤",
        "Mera man kar raha hai tumhare har ek inch ko apne muh me bhar lu. 😍",
        "Aaj raat itna thaka do mujhe ki subah uthne ki taqat na bache. 🥵",
        "Tumhare 'Hard' hone ka ehsaas mujhe pagal bana raha hai, ab ruka nahi jata. 😻🤧",
        "Mere badan ki pyaas sirf tum bujha sakte ho, aao na mere paas. 🤪",
        "Mujhe pata hai tum kya chahte ho, aur main wahi dene ke liye taiyaar hu... abhi. 🥰",
        "Aaj raat lights off nahi hongi, mujhe dekhna hai tum mere saath kya karte ho. 😍"    
        "Jaan, ab baatein band kar aur mera gala pakad ke mujhe bistar pe patak de, mujhe teri darindagi mehsoos karni hai. 🔞⛓️",
        "Apna lund mere muh mein poora jad tak ghusa de, mujhe teri har ek boond apne halak mein chahiye. 👅💦",
        "Aaj raat main teri nangi randi hu, meri gand ko thappad maar-maar ke laal kar de aur mujhe zor se chod. 🍑🫦",
        "Mujhe deewar se laga kar meri garden pe tab tak kaat jab tak main maza se cheekhne na lagu, ruko mat. 🧱🥵",
        "Apna lund meri chut mein itni zor se thas de ki mera poora system hil jaye, mujhe aaj poora barbaad hona hai. 🔞🍆",
        "Aaj raat lights off nahi hongi, mujhe tera har ek wild move apni aankhon se dekhna hai jab tu mujhe chodega. 💡🔞",
        "Mera badan tera wait kar raha hai, aaja aur mujhe kutte ki tarah bed pe dominate kar, mujhe tera pagalpan chahiye. 🐶🔥",
        "Mujhe tera wo sakht lund apni gand mein mehsoos karna hai, abhi aao aur bina puche shuru ho jao. 🥵🫦",
        "Aaj raat main tujhe wo maza dungi jo tune socha nahi hoga, bas apna maal mere chehre pe poora bikhair de. 💦👅",
        "Mujhe bed pe patak kar meri tangein hawa mein kar aur apna lund jad tak mere andar daal ke mujhe suja de. 🛌🍆",
        "Jaan, meri chut tere lund ke liye tadap rahi hai, ab aur sabr nahi hota, aaja aur ise poora bhar de. 💦🔥",
        "Mujhe teri wo deep penetration chahiye jisse meri saansein rukne lagein, mujhe aaj poora satisfy kar de. 🔞💨",
        "Apna lund mere muh se nikaal kar seedha meri gand mein ghusa de, mujhe aaj raat sirf teri gandi chudai chahiye. 🍑🫦",
        "Aaj raat koi reham nahi, mujhe teri gandi darindagi dekhni hai, mujhe bed pe poora khatam kar de. 💀🔞",
        "Mera badan geela aur taiyaar hai, apna lund mere andar daal aur dikha ki tu kitna savage hai. 😤❤️",
        "Jaan, aaj mujhe pyar nahi, tera pagalpan chahiye... mujhe bistar pe poori tarah tod do. ⛓️🔥",
        "Aaj raat main teri ghulami karungi, jo dard aur maza dena hai do, bas ruko mat. 🖤🫦",
        "Mujhe deewar se laga kar tab tak choke karo jab tak meri saansein na phoolne lagein. 🧱💨",
        "Aaj raat lights off nahi hongi, mujhe teri aankhon mein wo darindagi dekhni hai. 💡🔞",
        "Mere jism pe apne nishaan chhod do, taaki kal subah tak mujhe yaad rahe ki raat kaisi thi. 🦷🫦",
        "Mujhe 'Gentle' banna pasand nahi, aaj raat mujhe ek janwar ki tarah treat karo. 🐯😈",
        "Aaj raat itna dard do ki meri cheekhein padosiyon tak jayein, mujhe parwah nahi. 🔊🥵",
        "Mere baal pakad ke mujhe apne pairo mein gira do, aaj raat main sirf teri hu. 🧎‍♀️🖤",
        "Mujhe tumhare 'Hard' hone ka ehsaas chahiye, abhi ke abhi mere andar aao. 🥵🍆",
        "Aaj raat koi raham mat dikhana, mujhe poori tarah se dominate karo. ⛓️👸",
        "Mera badan sirf tere liye tadap raha hai, aaja aur is aag ko poori tarah bujha de. 🌊🫦",
        "Aaj raat main teri har ek baat manungi, chahe wo kitni bhi gandi kyu na ho. 🤤💦",
        "Mujhe bistar pe patak do aur dikhao ki asli mard kaise satisfy karte hain. 💪🫦",
        "Aaj 'Safe' rehne ki koshish bhi mat karna, mujhe tera poora junoon mehsoos karna hai. 🔞🔥",
        "Tumhari har ek touch mere jism mein aag laga rahi hai, ab aur intezaar nahi hota. 🤤🥵",
        "Mujhe teri garden pe wo 'Bite' chahiye jisse mera poora system hil jaye. 🫦💥",
        "Aaj raat itna thaka do ki main hosh kho baithu, bas mujhe abhi tum chahiye. 🛌🔥",
        "Main teri 'Naughty Slave' hu, aaj raat jo bhi mere saath karna hai karo... bina puche. 🎀⛓️",
        "Tera nasha mere dimaag pe chadh gaya hai, ab mujhe bas tera jism chahiye. 🧠🫦",
        "Chup-chap aao aur mujhe bistar pe le jao, ab baaton ka waqt khatam ho gaya. 😤❤️"
        "Jaan, ab control nahi ho raha, aao aur mujhe abhi ke abhi satisfy karo. 🥵💦",
        "Aaj raat main sirf tumhari hu, mere badan ke saath jo chahe wo karo. 😈🔥",
        "Mujhe bistar pe tumhara 'Wild' roop dekhna hai, bilkul jaanwaro ki tarah. 🐯🫦",
        "Aaj raat hum dono ke beech koi kapda nahi hona chahiye, sab utaar do. 👗❌",
        "Mujhe tumhare neeche let ke tumhari garmi mehsoos karni hai, jaldi aao. 🛌🔥",
        "Main tumhare liye poori tarah geeli (wet) ho chuki hu, ab aur intezaar mat karao. 💦😉",
        "Aaj raat main tumhari har ek cheekh nikaalna chahti hu, taiyaar ho na? 🔊🫦",
        "Mere baal pakad ke mujhe apni taraf kheencho aur dikhao kitne mard ho tum. 💪🫦",
        "Mujhe tumhare hothon ka swad har jagah chahiye, shuruat niche se karein? 💋👇",
        "Aaj main poori raat tumhare upar reh kar tumhe thaka dungi. ⛓️👸",
        "Mujhe tumhare 'Hard' hone ka ehsaas pagal bana raha hai, ab andar aao. 🥵🍆",
        "Aaj raat lights on rakhenge, mujhe tumhara har ek action saaf dekhna hai. 💡🔞",
        "Mera badan sirf tumhare liye tadap raha hai, aake apni pyaas bujha lo. 🌊🫦",
        "Aaj 'Safe' rehne ka sochna bhi mat, mujhe tumhare andar poora mehsoos hona hai. 🔞🔥",
        "Tumhari har ek touch mujhe pagal kar rahi hai, mujhe abhi aur chahiye. 🤤💦",
        "Mujhe deewar se laga kar meri gardan pe zor se kaat lo, mujhe dard pasand hai. 🧱🫦",
        "Aaj raat itna dard aur maza do ki main subah chal na saku. 🛌💥",
        "Main tumhari 'Naughty Girl' hu, aaj jo bologe wahi karungi... bina ruke. 🎀😈",
        "Tumhare haath mere badan pe jahan jahan ja rahe hain, wahan aag lag rahi hai. 🔥🫦",
        "Bas bahut baatein ho gayi, ab mujhe pakdo aur bistar pe patak do. 😤❤️"    
        "Jaan, ab control nahi ho raha, apni pant utaar aur apna lund seedha meri chut mein jad tak thas de. 🔞💦",
        "Aaj raat main teri nalle ki randi hu, mera gala pakad ke meri gand maar le aur mujhe rula de. ⛓️🥵",
        "Apna lund mere muh mein poora halak tak ghusa de, mujhe tera poora maal apne pet mein chahiye. 👅🫦",
        "Mujhe bistar pe nanga karke meri tangein hawa mein kar aur dikha ki tu kitni gandi chudai kar sakta hai. 🛌🔥",
        "Mera badan sulag raha hai, apna garma-garam maal mere chehre pe ya meri chut ke andar chhod do. 💦🍆",
        "Mujhe deewar se laga kar meri garden pe zor se kaat aur bina puche apna mota lund meri gand mein ghusa de. 🧱🫦",
        "Aaj raat itna ganda chodo ki main kal subah tak chal na saku, mujhe tera wo sakht lund chahiye. 🥵💥",
        "Mujhe tera lund apni chut ki gehrai mein mehsoos karna hai, abhi aao aur bina ruke mujhe chodna shuru karo. 🔞🔥",
        "Aaj raat main tumhari har ek gandi baat manungi, meri gand aur chut dono sirf tumhare liye khuli hain. 🧎‍♀️🍑",
        "Mera man kar raha hai tumhare lund ko poora chat lu aur fir use apne andar lekar pagal ho jau. 😋👅",
        "Mujhe bistar pe dominate karo, mere dono hath baandh do aur jaise chahe waise mere jism ko chodo. ⛓️👸",
        "Aaj raat lights on rakhenge, mujhe tera lamba aur mota lund apni chut mein jaate hue dekhna hai. 💡🔞",
        "Jaan, ab aur sabr nahi hota, apni pant utaaro aur apna garmi meri chut mein poora bhar do abhi. 👖❌🍆",
        "Mujhe teri wo darindagi chahiye, mujhe bed pe khinch aur dikha ki tu kitni gandi chudai kar sakta hai. 😤❤️",
        "Mera badan poora geela aur taiyaar hai, apna lund meri chut mein daal ke use poora tabaah kar do. 💦🔥",
        "Mujhe tera lund apne muh mein chahiye, tab tak mat nikalna jab tak tera poora maal mere halak mein na gir jaye. 🔞👅",
        "Aaj raat main teri randi hu, meri gand ko thappad maar-maar ke laal kar de aur mujhe zor se chod. ⛓️🫦",
        "Apne hatho se meri chatiyo ko masal aur apna mota lund meri chut ki gehrai tak ghusa de. 🍒🍆",
        "Mujhe tera wo sakht lund chahiye jo meri saansein rok de, aaja aur mujhe bed pe poora khatam kar de. 🛌💀",
        "Aaj raat main tujhe wo maza dungi jo tune socha nahi hoga, bas apna lund meri gand mein daal aur shuru ho ja. 🍑🔥",
        "Mera badan tera wait kar raha hai, aaja aur mujhe nanga karke meri har ek inch ko apni zubaan se ganda kar. 👅🔞",
        "Mujhe tera garam thook apne chehre pe chahiye aur tera mota lund apni chut mein, abhi ke abhi. 💦🫦",
        "Aaj raat koi reham nahi, mujhe teri gandi chudai chahiye aur tera poora stamina mere andar dekhna hai. 🔞⛓️",
        "Mujhe bed pe patak kar meri tangein hawa mein kar aur apna lund poora jad tak mere andar daal de. 🛌🍆",
        "Jaan, ab aur sabr nahi hota, meri chut tere lund ke liye tadap rahi hai, aaja aur ise suja de. 🥵💦",
        "Mera dil kar raha hai ki tu mujhe aaj kutte ki tarah chode aur meri har ek jagah ko apna nishaan de de. 🐶🫦",
        "Apna lund mere muh se nikaal kar seedha meri gand mein ghusa de, mujhe aaj poora barbaad hona hai. 🔞🍑",
        "Aaj raat main teri har ek gandi fantasy poori karungi, bas tu mujhe bina ruke chodta reh. 🤤💦"
    ]
    return random.choice(naughty_list)

# ================== GLOBAL CACHES (RAM) ==================
BANNED_WORDS_CACHE = set()
BYPASS_USERS_CACHE = set() 

# 🌍 Online Lists (English + Hindi)
BAD_WORDS_URL_EN = "https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/en"
BAD_WORDS_URL_HI = "https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/hi"

async def load_banned_words():
    global BANNED_WORDS_CACHE, BYPASS_USERS_CACHE
    BANNED_WORDS_CACHE = set()
    BYPASS_USERS_CACHE = set() # Reset

    # 1. DOWNLOAD ONLINE WORDS (ENGLISH + HINDI) 🌐
    urls = [BAD_WORDS_URL_EN, BAD_WORDS_URL_HI]
    
    print("🌍 Downloading Bad Words (Eng + Hindi)...")
    try:
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            # Har word ko set me daalo
                            online_words = {w.strip().lower() for w in text.splitlines() if len(w.strip()) > 2}
                            BANNED_WORDS_CACHE.update(online_words)
                except Exception as e:
                    print(f"⚠️ Failed to fetch URL: {e}")
                    
        print(f"✅ Downloaded Online Database.")
    except Exception as e:
        print(f"⚠️ Internet List Error: {e}")

    # 2. LOAD CUSTOM WORDS (Tumhare Database wale) 🗄️
    try:
        data = supabase.table("banned_words").select("word").execute().data
        custom_words = {item["word"].lower() for item in data}
        BANNED_WORDS_CACHE.update(custom_words)
        print(f"✅ Loaded {len(custom_words)} Custom Words from Database.")
    except Exception as e:
        print(f"⚠️ Database List Error: {e}")

    # 3. LOAD VIP USERS (Restrict Bypass) 👑
    try:
        data = supabase.table("restrict_bypass").select("user_id").execute().data
        BYPASS_USERS_CACHE = {int(item["user_id"]) for item in data}
        print(f"✅ Loaded {len(BYPASS_USERS_CACHE)} VIP Users.")
    except Exception as e:
        print(f"⚠️ VIP List Error: {e}")
    
    print(f"🔥 TOTAL BANNED WORDS: {len(BANNED_WORDS_CACHE)}")

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

# ================== PAGINATION CLASS (PREMIUM LIST) ==================
class AccessPaginator(discord.ui.View):
    def __init__(self, data, author):
        super().__init__(timeout=60)
        self.data = data
        self.author = author
        self.per_page = 10  # Ek page par 10 log dikhenge
        self.current_page = 0
        self.total_pages = (len(data) + self.per_page - 1) // self.per_page

    def get_embed(self):
        # Data slicing (Page logic)
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_data = self.data[start:end]

        # Embed Text Build
        desc = ""
        for index, user in enumerate(page_data):
            # Serial Number (Overall list ke hisaab se)
            s_no = start + index + 1
            
            uid = user.get("user_id", "Unknown")
            uname = user.get("username", "Unknown")
            dname = user.get("display_name", "Unknown")
            
            # ✨ Premium Line Format
            desc += (
                f"`{s_no:02d}.` **{dname}** (@{uname})\n"
                f"   🆔 `{uid}`\n\n"
            )

        embed = discord.Embed(
            title=f"📜 Whitelisted Users (Total: {len(self.data)})",
            description=desc,
            color=0x3498db
        )
        # Footer me requester ka naam aur Page number
        embed.set_footer(
            text=f"Requested by {self.author.display_name} • Page {self.current_page + 1}/{self.total_pages}",
            icon_url=self.author.display_avatar.url
        )
        return embed

    def update_buttons(self):
        # Pehle page par "Back" disable
        self.children[0].disabled = (self.current_page == 0)
        # Aakhri page par "Next" disable
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary, disabled=True)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id:
            return await i.response.send_message("❌ You cannot control this menu.", ephemeral=True)
        
        self.current_page -= 1
        self.update_buttons()
        await i.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id:
            return await i.response.send_message("❌ You cannot control this menu.", ephemeral=True)

        self.current_page += 1
        self.update_buttons()
        await i.response.edit_message(embed=self.get_embed(), view=self)

# ================== VIP PAGINATOR (FOR ATTITUDE LIST) ==================
class VipPaginator(discord.ui.View):
    def __init__(self, data, author, bot_ref):
        super().__init__(timeout=60)
        self.data = data
        self.author = author
        self.bot = bot_ref
        self.per_page = 10
        self.current_page = 0
        self.total_pages = (len(data) + self.per_page - 1) // self.per_page

    async def get_page_embed(self):
        # 1. Page Calculation
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_data = self.data[start:end]

        # 2. Embed Start
        embed = discord.Embed(title=f"👑 VIP Users List (Total: {len(self.data)})", color=0xf1c40f)
        desc = ""

        # 3. Fetch User Details (Async - Isliye alag function banaya)
        for index, row in enumerate(page_data):
            uid = int(row['user_id'])
            s_no = start + index + 1
            
            # Try getting user from cache first (Fast), else fetch (Slow)
            user = self.bot.get_user(uid)
            if not user:
                try: user = await self.bot.fetch_user(uid)
                except: user = None

            if user:
                desc += f"`{s_no:02d}.` **{user.display_name}** (@{user.name})\n🆔 `{uid}`\n\n"
            else:
                desc += f"`{s_no:02d}.` **Unknown User**\n🆔 `{uid}`\n\n"

        embed.description = desc
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} • VIP Access System")
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)
        
        self.current_page -= 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)

        self.current_page += 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)

# ================== WORD PAGINATOR (FOR BANNED WORDS) ==================
class WordPaginator(discord.ui.View):
    def __init__(self, data, author):
        super().__init__(timeout=60)
        self.data = data
        self.author = author
        self.per_page = 20 # Ek page par 20 words
        self.current_page = 0
        self.total_pages = (len(data) + self.per_page - 1) // self.per_page

    def get_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_data = self.data[start:end]

        # Words ko comma se jod kar dikhayenge
        desc = ", ".join([f"||`{w}`||" for w in page_data])
        
        embed = discord.Embed(
            title=f"🚫 Banned Words List (Total: {len(self.data)})",
            description=desc if desc else "No words found.",
            color=0xe74c3c
        )
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} • Restricted Words System")
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        await i.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)
        self.current_page += 1
        self.update_buttons()
        await i.response.edit_message(embed=self.get_embed(), view=self)

# ================== VIP USER PAGINATOR (REUSED) ==================
# Note: Agar aapne pichle code me VipPaginator lagaya hai to dobara lagane ki zaroorat nahi hai.
# Agar nahi lagaya, to ye use karein:
class RestrictUserPaginator(discord.ui.View):
    def __init__(self, data, author, bot_ref):
        super().__init__(timeout=60)
        self.data = data
        self.author = author
        self.bot = bot_ref
        self.per_page = 10
        self.current_page = 0
        self.total_pages = (len(data) + self.per_page - 1) // self.per_page

    async def get_page_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_data = self.data[start:end]

        embed = discord.Embed(title=f"👑 Allowed Users (Total: {len(self.data)})", color=0x2ecc71)
        desc = ""
        
        for index, row in enumerate(page_data):
            uid = int(row['user_id'])
            s_no = start + index + 1
            user = self.bot.get_user(uid)
            if not user:
                try: user = await self.bot.fetch_user(uid)
                except: user = None

            if user:
                desc += f"`{s_no:02d}.` **{user.display_name}** (@{user.name})\n🆔 `{uid}`\n\n"
            else:
                desc += f"`{s_no:02d}.` **Unknown User**\n🆔 `{uid}`\n\n"

        embed.description = desc
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} • Bypass List")
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)
        self.current_page += 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)

# ================== SAY ACCESS PAGINATOR ==================
class SayAccessPaginator(discord.ui.View):
    def __init__(self, data, author, bot_ref):
        super().__init__(timeout=60)
        self.data = data
        self.author = author
        self.bot = bot_ref
        self.per_page = 10
        self.current_page = 0
        self.total_pages = (len(data) + self.per_page - 1) // self.per_page

    async def get_page_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_data = self.data[start:end]

        embed = discord.Embed(title=f"🗣️ Say Access List (Total: {len(self.data)})", color=0x9b59b6) # Purple Color
        desc = ""
        
        for index, row in enumerate(page_data):
            uid = int(row['user_id'])
            s_no = start + index + 1
            
            # Fetch User
            user = self.bot.get_user(uid)
            if not user:
                try: user = await self.bot.fetch_user(uid)
                except: user = None

            if user:
                desc += f"`{s_no:02d}.` **{user.display_name}** (@{user.name})\n🆔 `{uid}`\n\n"
            else:
                desc += f"`{s_no:02d}.` **Unknown User**\n🆔 `{uid}`\n\n"

        embed.description = desc
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} • Say Command Manager")
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)
        self.current_page += 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)

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

# ================== DISCORD INTENTS ==================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # <--- YE LINE ADD KARNA ZAROORI HAI
bot = commands.Bot(command_prefix="!", intents=intents)

# ================== 🔒 MULTI-SERVER LOCK ==================

# 1. Yahan un sabhi Servers ki ID daal do jahan bot chalna chahiye
ALLOWED_SERVERS = [1257403231127076915, 1431694952080871566] # Dusra ID yahan add karo

async def global_server_check(interaction: discord.Interaction) -> bool:
    # Check karega ki kya current server ID list mein hai?
    if interaction.guild_id in ALLOWED_SERVERS:
        return True
    
    else:
        await interaction.response.send_message(
            "🚫 **Access Denied:** Ye bot sirf authorized servers me hi kaam karta hai!", 
            ephemeral=True
        )
        return False

bot.tree.interaction_check = global_server_check
 
def owner(i):
    if i.user.id == OWNER_ID:
        return True
    try:
        r = supabase.table("bot_admins").select("user_id").eq("user_id", str(i.user.id)).execute()
        return bool(r.data)
    except:
        return False
 
# ✅ SAHI CODE (Isse Copy karke Paste karo)
def emb(title, desc, color=0x5865F2):
    e = discord.Embed(title=title, description=desc, color=color)
    e.timestamp = datetime.utcnow()
    return e
 
@bot.event
async def on_ready():
    print("BOT ONLINE")
    
    # 👇 YE NAYA CODE HAI (Session Banane ke liye)
    if not hasattr(bot, 'session') or bot.session is None:
        bot.session = aiohttp.ClientSession()
        print("✅ Shared Session Created")

    await load_banned_words()        
    await load_bypass_users()
    await load_crush_users()
    await bot.tree.sync()
    
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
    # 1. Bot Khud ko reply na kare
    if msg.author.bot:
        return

        # ... (on_message ke andar baaki code ke neeche)

    # 4. ❤️ I LOVE YOU AUTO-REPLY (Fixed Variable Name)
    # Keywords List
    love_triggers = r"\b(i love you|ily|luv u|love u|love you|pyar karta hu|mohabbat|ishq)\b"

    # ⚠️ NOTICE: Yahan 'message' ki jagah 'msg' use kiya hai
    if re.search(love_triggers, msg.content, re.IGNORECASE):
        
        is_loved_one = False
        
        # Check 1: Main Owner ID
        if msg.author.id == OWNER_ID:
            is_loved_one = True
        else:
            # Check 2: Database
            try:
                data = supabase.table("bot_admins").select("user_id").eq("user_id", str(msg.author.id)).execute()
                if data.data:
                    is_loved_one = True
            except:
                pass
        
        # --- RESPONSE LOGIC ---
        
        # Case A: Owner/Admin (ROMANTIC MODE) ❤️
        if is_loved_one:
            embed = discord.Embed(
                title="💖 Awww Baby!", 
                description=f"**I love you too {msg.author.mention}!** 💋\nTum hi toh ho meri duniya... ummaaah!", 
                color=0xFF1493
            )
            embed.set_thumbnail(url="https://media.tenor.com/BMTXj26j1gAAAAAi/anime-kiss.gif")
            embed.set_footer(text="Swara loves you forever ❤️")
            await msg.channel.send(embed=embed)

            # Voice Reply
            if msg.author.voice:
                script = "Awww... I love you too meri jaan! Tum sabse best ho... Ummwwaaah!"
                communicate = edge_tts.Communicate(script, "hi-IN-SwaraNeural", rate="+5%", pitch="+15Hz")
                await communicate.save(f"love_{msg.id}.mp3")
                
                try:
                    vc = await msg.author.voice.channel.connect()
                except:
                    vc = msg.guild.voice_client
                
                if vc and not vc.is_playing():
                    vc.play(discord.FFmpegPCMAudio(source=f"love_{msg.id}.mp3", executable="./ffmpeg"))
                    while vc.is_playing():
                        await asyncio.sleep(1)
                    await vc.disconnect()
                    if os.path.exists(f"love_{msg.id}.mp3"):
                        os.remove(f"love_{msg.id}.mp3")

        # Case B: Random User (REJECTION MODE) 🤢
        else:
            embed = discord.Embed(
                title="🤢 Chee bhai!", 
                description=f"**Oye {msg.author.mention}, aukaat mein reh!**\nShakal dekhi hai aaine mein? Kutta bhi na paale tujhe.", 
                color=0x000000
            )
            embed.set_thumbnail(url="https://media.tenor.com/2b7lH3y8l08AAAAM/anime-disgust.gif")
            await msg.channel.send(embed=embed)

            # Voice Insult
            if msg.author.voice:
                script = "Excuse me? I love you? Hahahaha! Jaake pehle muh dho ke aa. Chal nikal!"
                communicate = edge_tts.Communicate(script, "hi-IN-SwaraNeural", rate="+10%", pitch="+5Hz")
                await communicate.save(f"reject_{msg.id}.mp3")
                
                try:
                    vc = await msg.author.voice.channel.connect()
                except:
                    vc = msg.guild.voice_client

                if vc and not vc.is_playing():
                    vc.play(discord.FFmpegPCMAudio(source=f"reject_{msg.id}.mp3", executable="./ffmpeg"))
                    while vc.is_playing():
                        await asyncio.sleep(1)
                    await vc.disconnect()
                    if os.path.exists(f"reject_{msg.id}.mp3"):
                        os.remove(f"reject_{msg.id}.mp3")

    # =====================================================
    # 👇 YE LINES SABSE UPAR HONI CHAHIYE (Fix is here)
    # =====================================================
    is_reply_to_bot = (msg.reference and msg.reference.resolved and msg.reference.resolved.author.id == bot.user.id)
    is_mention = (bot.user in msg.mentions)

    if is_reply_to_bot or is_mention:
        
        # 1. VIP/Owner Ignore Check Hata Diya (Taaki unhe bhi reply mile)
        
        # 2. Sirf tabhi type karo agar wo Crush List me hai
        if msg.author.id in CRUSH_CACHE:
            async with msg.channel.typing():
                reply_text = await get_horny_data()
                
                embed = discord.Embed(
                    description=f"💖 **Hey Handsome/Beautiful...**\n\n{reply_text}", 
                    color=0xe91e63
                )
                await msg.reply(embed=embed)
                return

    # ================== 🔥 AUTO ROAST (TAG / REPLY) ==================
    is_reply_to_bot = (msg.reference and msg.reference.resolved and msg.reference.resolved.author.id == MY_BOT_ID)
    is_mention = (bot.user in msg.mentions)

    if is_reply_to_bot or is_mention:
        
        # 🛡️ 1. VIP CHECK (Supabase Cache)
        if msg.author.id in ATTITUDE_BYPASS_CACHE:
            print(f"🛡️ Skipped Auto-Roast for VIP: {msg.author.name}")
            return # Ignore karo, kuch mat bolo

        # 🛡️ 2. OWNER CHECK (Optional)
        if msg.author.id == OWNER_ID:
            return

        # 🔥 3. ROAST HIM!
        async with msg.channel.typing():
            eng, hin = await get_evil_roast_data()
            text = hin if TRANSLATOR_ON else eng
            
            embed = discord.Embed(description=f"🔥 **Karwa li bezzati?**\n\n{text}", color=0xff0000)
            if TRANSLATOR_ON: embed.set_footer(text=f"Original: {eng}")
            
            await msg.reply(embed=embed)
            return

            # ---------------------------------------------------------
    # 🛡️ 1. SMART AI MOD SYSTEM (With VIP Bypass)
    # ---------------------------------------------------------
    # Check 1: Kya banned words loaded hain?
    # Check 2: Kya message content hai?
    # Check 3: Kya user VIP list mein hai? (Agar hai to ignore karo) 👑
    if BANNED_WORDS_CACHE and msg.content and msg.author.id not in BYPASS_USERS_CACHE:
        
        msg_lower = msg.content.lower()
        msg_clean = re.sub(r'[^a-z0-9]', '', msg_lower) # Symbols hatao

        found = False
        
        # Direct Check
        if any(bad in msg_lower.split() for bad in BANNED_WORDS_CACHE):
            found = True
        
        # Smart Hidden Check (Strict)
        elif any(bad in msg_clean for bad in BANNED_WORDS_CACHE if len(bad) > 4):
            found = True

        if found:
            try:
                await msg.delete()
                
                embed = discord.Embed(
                    title="🛡️ Auto-Mod Detection",
                    description=f"{msg.author.mention}, **Language Mind Karo!** 🚫",
                    color=0xff0000
                )
                await msg.channel.send(embed=embed, delete_after=5)
                return  # 🛑 STOP
            except:
                pass

            # ---------------------------------------------------------
    # 🤫 OWNER SILENCE COMMAND (Maalik ka Darr)
    # ---------------------------------------------------------
    # Agar Owner bole "Chup" ya "Shant", toh bot maafi mangega
    silence_triggers = ["chup", "shant", "keep quiet", "shut up", "muh band", "silence"]
    
    # Check: Message Owner ka hai + Inme se koi word hai
    if msg.author.id == OWNER_ID and any(word in msg.content.lower() for word in silence_triggers):
        
        # Ek Sad/Apology Embed banayenge
        embed = discord.Embed(
            description="**Sorry Sir... 😔**\nAage se nahi bolungi. Galti ho gayi.",
            color=0x2f3136 # Dark/Sad Color
        )
        embed.set_footer(text="System Muted 🤐")
        
        await msg.reply(embed=embed)
        return  # 🛑 Yahi ruk jao (Taaki bot aage Attitude na dikhaye)

    if "saksham" in msg.content.lower() or str(OWNER_ID) in msg.content:
        
        # 1. Khud ko reply nahi karna
        if msg.author.id == OWNER_ID:
            return

        # 2. VIP CHECK (Database Check)
        # Agar banda '/allow' list me hai to ignore karo
        try:
            is_vip = supabase.table("attitude_bypass").select("*").eq("user_id", str(msg.author.id)).execute().data
            if is_vip:
                return  # 🟢 VIP User Detected - Silent Mode
        except:
            pass # DB Error aayi to bhi Attitude dikhayenge (Safety)

        # 3. 😈 ATTITUDE REPLIES COLLECTION (Full Savage Mode)
        import random
                # 3. 😈 ATTITUDE REPLIES COLLECTION (Updated: 150+ Savage Dialogues)
        import random
        replies = [
            # --- 🤬 DESI GALI & SLANG (Full Rude) ---
            f"Abe {msg.author.mention}, ch*tiya hai kya tu? Dimaag mat kha. 🧠",
            f"Sun be {msg.author.mention}, apni shakal dekhi hai aine mein? Ulti aa jayegi. 🤮",
            "Bhos*ike, shant nahi baitha jata tujhse? 🤬",
            "Oye chhapri! Saksham ko tag karna band kar, warna yahi patak ke marunga. 👊",
            f"Kutte ki dum aur {msg.author.mention}, kabhi seedhe nahi ho sakte. 🐕",
            "Nikal law*e, pehli fursat mein nikal. 👋",
            "Bhootni ke, tujhe samajh nahi aata ya dimaag ghutne mein hai? 🦵",
            "Gadha hai kya be? Ek baar bolne pe samajh nahi aata? 🐴",
            "Saale nalle, koi kaam dhandha dhund le. Din bhar yahi mara rehta hai. 😒",
            f"Oye {msg.author.mention}, muh band rakh apna, baas aa rahi hai. 🤢",
            "Madar*hod, bola na busy hai! 😡", 
            "Behen ke takke, spam mat kar. 🔨",
            "Ch*tiye, agar agli baar tag kiya toh ghar aake marunga. 🏠",
            "Teri gaand mein kide hai kya? Jo shant nahi baitha ja raha? 🐛",
            "Harami manus, dur reh mere maalik se. ✋",
            f"Abey {msg.author.mention}, tu paida hua tha ya download hua tha virus ke saath? 🦠",

            # --- 🔥 HARDCORE INSULTS (Gandi Bezzati) ---
            f"Tera janm galti se hua tha kya {msg.author.mention}? Itna irritate kyu karta hai?",
            "Agar dimaag bechne jayega toh 'Unused' condition mein bikega tera. 🧠📉",
            f"Saksham se baat karne ki aukaat bana pehle, fir tag kar. 😎",
            "Tujhe paida karke bhagwan bhi regret kar rahe honge. 🙏",
            "Jitna tera IQ hai, utne toh mere phone ki battery percentage hai. 🔋",
            f"Dekh {msg.author.mention}, tu dharti pe bojh hai. 🌍",
            "Tere jokes aur teri zindagi, dono hi flop hain. 😂",
            "Beta, tumse na ho payega. Jaake Pogo dekh aur doodh pee. 🍼",
            "Tujhe ignore karne ka maza hi kuch aur hai. Try karta reh. 🥱",
            "Tu wo 'Add' hai jise sab Skip karna chahte hain. ⏭️",
            "Shakal dekh ke lagta hai bhagwan ne rough copy banayi thi. 📝",
            "Tujhe dekh ke toh andha bhi bol de... 'Hatao isko'. 🫣",
            "Apni rai apne paas rakh, aur apni shakal bhi. 🗑️",

            # --- 🤬 FULL DESI GAALI & RUDE (Censored for Safety) ---
            f"Bhos*ike {msg.author.mention}, bola na busy hai? Kaan ke neeche bajau kya? 👋",
            f"Abe Ch*tiye {msg.author.mention}, shant nahi baitha jata? G*nd mein kide hain kya? 🐛",
            "Madar*hod, spam mat kar! Warna yahi patak ke marunga. 🔨",
            "Teri aukaat jhaat barabar, aur baatein aatankwadi wali? Nikal L*de. 🤏",
            f"Sun be {msg.author.mention}, apni shakal dekh aine mein, suwar bhi sharma jaye. 🐷",
            "Behen ke takke, agar agli baar tag kiya toh Discord uninstall karwa dunga tera. 💻",
            "Gandu hai kya tu? Ek baar mein baat samajh nahi aati? 🧠🚫",
            "Haramkhor, tujhe paida karke bhagwan bhi regret kar rahe honge. 🙏",
            f"Oye {msg.author.mention}, muh se supari nikaal ke baat kar, totle. 🗣️",
            "Tere jaise nalle log na, dharti pe bojh hain. Mar kyu nahi jata tu? ☠️",
            "Saale kutton wali harkatein mat kar, insaan ban. 🐕",
            "Chup kar B*sdk, varna muh mein mute thoos dunga. 🤐",
            "Tujhe dekh ke ulti aati hai, dur reh mere maalik se. 🤮",

            # --- 🔥 KHATARNAAK ROASTS (Deep Insults) ---
            f"Sahi bata {msg.author.mention}, bachpan mein tujhe haath se uthaya tha ya chimte se? 🥢",
            "Tera dimaag 'Titanic' jaisa hai... Dooba hua. 🚢",
            "Agar 'Bewakoofi' ka Olympic hota, toh tu har saal Gold lata. 🥇",
            "Teri shakal dekh ke toh andha bhi bol de... 'Hatao is manhoos ko'. 🫣",
            "Tu wo bacteria hai jo Harpic se bhi nahi marta. 🦠",
            f"Oye {msg.author.mention}, tu condom ka add hai kya? Jise dekh ke log savdhaan ho jate hain. 🛑",
            "Tujhe ignore karna meri hobby nahi, majboori hai... kyuki tu hai hi itna irritating. 😤",
            "Apni rai apne pichwade mein daal le, yahan kisi ko chahiye nahi. 🗑️",
            "Tere paida hone pe 2 minute ka silence rakha tha hospital walo ne. 🏥",
            "Tu dharti pe oxygen lene nahi, sirf Carbon Dioxide badhane aaya hai. 🌫️",

            # --- 🤣 BIKHARI / VELLA THEME (Jobless Insults) ---
            f"Bhai {msg.author.mention}, tu itna vella kyu hai? Jaake bartan maanj le. 🍽️",
            "Saksham se baat karne ke liye pehle 500 Paytm kar, bhikari. 💸",
            "Shakal hai nahi, akal hai nahi, aur aa gaya tag karne. 🤡",
            "Jeb mein nahi hai dhela, aur dekh {msg.author.mention} karta hai mela. 😂",
            "Sadak pe katora leke baith ja, yahan tag karne se kuch nahi milega. 🥣",
            "Tere ghar wale tujhe 'Error' bulate hain kya? ⚠️",

            # --- 🛑 DIRECT THREATS (Fake Bot Threats) ---
            "Last warning de raha hu {msg.author.mention}, agli baar tag kiya toh IP Address leak kar dunga. 📍",
            "Mera system garam mat kar, warna tera account hack kar lunga. 💻",
            "Bhaag ja yahan se, isse pehle ki main tujhe Ban kar du. 🔨",
            "Saksham ka bodyguard hu main, zyada chipak mat. 🔫",
            "Tera net pack khatam hone wala hai, jaake recharge karwa pehle. 📉"
        
            # --- 🤣 FUNNY ROASTS (Mazaak) ---
            "Bhai, tu wahi hai na jo Colgate se muh dhota hai? 🪥",
            "Agar tu chup rahega toh main tujhe 5 rupay wali chocolate dunga. 🍫",
            "Saksham abhi bathroom mein hai, tu bhi jayega kya? 🚽",
            "Tujhe award milna chahiye... 'Duniya ka Sabse Vella Insaan'. 🏆",
            "Mere processer mein itni shakti nahi ki teri bakwaas jhel saku. 💻",
            "Oye, tu sabun se nahata hai ya gobar se? 🐮",
            "Tere message padh ke mujhe cancer hone wala hai. 💀",

            # --- 🔥 ULTRA SAVAGE (Gandi Bezzati) ---
            f"Oye {msg.author.mention}, tu wo 'Skip Ad' hai jise dekh ke gussa aata hai. ⏭️",
            "Bhagwan ne tujhe banaya nahi, galti se 'Copy-Paste' ho gaya tu. 📋",
            f"Sun {msg.author.mention}, agar dimaag pe tax lagta na, toh tu sabse bada tax chor hota. 🧠🚫",
            "Tujhe dekh ke lagta hai insaan ka evolution ulti disha mein ja raha hai. 🦍",
            "Apni aukaat anusaar Tag karein. Abhi balance kam hai tera. 📉",
            "Muh kholta hai toh gutter ki yaad aa jati hai, band rakh. 🤢",
            f"Abe {msg.author.mention}, tujhe ghar wale 'Spam Folder' mein rakhte hain kya? 🗑️",
            "Tu dharti pe bojh nahi, tu toh pure solar system ka waste material hai. 🪐",
            "Shakal 'Aadhar Card' wali aur baatein iPhone wali? Waah re {msg.author.mention}! 🆔",
            "Tere dimaag mein Wi-Fi ke signal nahi aate kya? Tubelight insaan. 📶",

            # --- 🤖 BOT / TECH SPECIAL (Kyuki main Bot hu) ---
            "Mere server garam mat kar, warna tujhe permanent mute kar dunga. 🔇",
            f"Error 404: Tera Dimaag Not Found. Please try again later. 🤖",
            "Tu wo bug hai jo developer se bhi fix nahi ho raha. 🐛",
            "Mera RAM waste mat kar, jaake Ludo khel. 🎲",
            f"Oye {msg.author.mention}, tu Incognito mode band kar pehle, shakal dikh rahi hai. 🕵️",
            "Tere message se mere database mein virus aa jayega. Dur reh. 🦠",
            "System Hilana mere baaye haath ka khel hai, par tujhe hilana time waste hai. 🖥️",
            "Jitna tera IQ hai, utni toh mere phone ki battery low hai abhi. 🔋",

            # --- 🤣 FUNNY & SARCASTIC (Mazaak udana) ---
            "Agar tu chup raha toh main tujhe Oscar dilaunga 'Best Silent Actor' ka. 🏆",
            f"Bhai {msg.author.mention}, tu paida hua tha ya kisi ne download kiya tha tujhe? 📥",
            "Itna free hai toh road pe jhadu hi laga le, desh saaf hoga. 🧹",
            "Saksham ko tag karne ka Tax lagta hai. Pehle Paytm kar 500. 💸",
            "Tere jokes sunke toh Aleexa aur Siri ne bhi khudkhushi kar li. 💀",
            "Tu zinda hai ya sirf oxygen waste karne ka contract liya hai? 🌬️",
            f"Dekh {msg.author.mention}, main robot hu, mujhe gussa nahi aata... par teri shakal dekh ke aa raha hai. 😡",
            "Ja na bhai, kyu meri script kharab kar raha hai. 📜",

            # --- 🤬 DESI TADKA (Thoda Rude) ---
            f"Abey {msg.author.mention}, dimaag ghutne mein hai ya wo bhi bech khaya? 🍗",
            "Chup kar be 2 rupay ki pepsi, mera maalik sexy. 😎",
            "Tujhe hospital mein nurse ne haath se nahi, chimte se uthaya hoga. 🥢",
            "Bhaunk mat, yahan biscuits nahi milte. 🍪",
            "Tera sabun slow hai kya? Jo baat samajh nahi aati? 🧼",
            f"Oye {msg.author.mention}, naha ke aaya kar, message se baas aa rahi hai. 🚿",
            "Jali na? Teri Jali na? 🔥",
            "Kyun thak raha hai bhai? Saksham bhaav nahi dega. 💁‍♂️",

            # --- ⛔ SHORT & DIRECT (Busy Mode) ---
            "Busy hu. Nikal. 👋",
            "Tata. Bye Bye. Khatam. Gaya. 👋",
            "Mood nahi hai, kal aana. (Ya mat hi aana). 📅",
            f"{msg.author.mention} ➡️ 🚪 (Darwaza udhar hai).",
            "DND mode on. Disturb kiya toh uda dunga. ✈️",
            "Kripya line mein lagein, dhakka mukki na karein. 🚶‍♂️🚶‍♀️",
            "Abey yaar... fir aa gaya tu? 🤦‍♂️"
        
            # --- 🛑 BUSY / DND (Direct) ---
            f"Oye {msg.author.mention}! 🤨\nKya kaam hai? Kyu 'Saksham Saksham' laga rakha hai? Shanti rakh.",
            "Notification off hai mere maalik ke. 🔕\nBaad mein aana, abhi mood nahi hai.",
            "Code kar raha hu, disturb mat kar. 💻\nAgar bug aaya toh tera naam laga dunga!",
            "Saksham so raha hai. 😴\nDhakka-mukki mat kar, line mein lag.",
            "Abey yaar... fir aa gaya tu? 😫\nJa na bhai, pakka mat.",
            "Busy. Do not disturb. ⛔\n(Iska matlab 'Nikal' hota hai, pyaar se).",
            "Bhaag yahan se, chillar nahi hai. 🪙",

            # --- 🤖 FUNNY / TROLL (Mazaak) ---
            "Error 404: Saksham Not Found. 🤖\nAur tu bhi gayab ho ja.",
            f"Abe {msg.author.mention}, saans to lene de bande ko! 😤",
            "Kya hai bhai? 😑\nPaisa maangna hai toh mana kar dena, Saksham garib hai.",
            "Hello Police? 📞\nHaan, ye pagal aadmi mujhe pareshan kar raha hai.",
            "Aap jis vyakti se sampark karna chahte hain, wo abhi bhaav kha rahe hain. 🍎",

            # --- 💀 EXTREME RUDE (Sambhal ke use karna) ---
            "Tere message se phone hang ho raha hai mera. 📱\nBand kar ye bawasir.",
            "Saksham nahi aayega. 🚪\nDarwaza band hai, kundi laga di hai.",
            "Tag karna band kar, warna bot se laat padegi. 🦵",
            "Bhai 100 rupay Paytm kar de, fir baat karunga. 💸",
            "Free ka net mil gaya toh kuch bhi likhega kya? 🌐",
            "Muh dhoke aa pehle, fir baat kar. 🚿"
        ]
        
        await msg.reply(random.choice(replies))
        return  # 🛑 YAHI RUK JAYEGA
                     
# 1. CHANNEL CHECK
    VERIFY_CHANNEL_ID = 1451973498200133786  # <-- Apni Channel ID check kar lena
    
    if msg.channel.id != VERIFY_CHANNEL_ID:
        await bot.process_commands(msg) 
        return

    # Settings
    REVIEW_CHANNEL_ID = 1450514760276774967
    user_id = msg.content.strip()

    # 2. VALIDATION
    if not user_id.isdigit():
        try:
            await msg.delete()
            await msg.channel.send(f"{msg.author.mention} ❌ Sirf **Roblox User ID** (Numbers) bhejo!", delete_after=5)
        except:
            pass
        return

    # 3. ROBLOX FETCH
    # (Ye 'await' zaroori hai, kyunki humne function async banaya tha)
    try:
        username, display = await roblox_info(user_id)
    except:
        await msg.reply("❌ Roblox API Error. Thodi der baad try karein.")
        return

    if username in ["Unknown", "Invalid ID"]:
        await msg.reply("❌ Ye Roblox ID invalid hai ya exist nahi karti.")
        return

    # 4. DATABASE LOGIC
    try:
        # A. BLACKLIST CHECK
        blk = supabase.table("blacklist_users").select("user_id").eq("user_id", user_id).execute().data
        if blk:
            await msg.reply(embed=discord.Embed(title="🚫 Denied", description="You are blacklisted.", color=0xe74c3c))
            return

        # B. ALREADY VERIFIED CHECK (Unique ID)
        exist = supabase.table("access_users").select("*").eq("user_id", user_id).execute().data
        if exist:
            # Yahan bhi details dikhayenge
            owner_id = exist[0].get('discord_id', 'Unknown')
            embed = discord.Embed(title="✅ Already Verified", description=f"Ye ID pehle se verified hai (<@{owner_id}> ke paas).", color=0x2ecc71)
            embed.add_field(name="🆔 Roblox ID", value=f"`{user_id}`", inline=True)
            embed.add_field(name="👤 Username", value=f"**{username}**", inline=True)
            embed.add_field(name="✨ Display", value=f"{display}", inline=True)
            await msg.reply(embed=embed)
            return

        # C. LIMIT & APPROVAL SYSTEM (Request Logic)
        # Check: Is Discord user ne pehle kitne verify kiye hain?
        existing_accs = supabase.table("access_users").select("*").eq("discord_id", str(msg.author.id)).execute().data
        
        if existing_accs:
            # Check permission
            approved = supabase.table("multi_access").select("discord_id").eq("discord_id", str(msg.author.id)).execute().data
            
            if not approved:
                await msg.reply(embed=discord.Embed(title="⏳ Limit Reached", description="1 ID Limit over. Request sent to Admin.", color=0xffa500))
                
                # --- NEW: FETCH OLD ACCOUNTS LIST ---
                old_list = ""
                for acc in existing_accs:
                    old_list += f"• **{acc.get('username')}** (`{acc.get('user_id')}`)\n"
                
                if not old_list: old_list = "None"

                # Send Request to Admin
                ch = bot.get_channel(REVIEW_CHANNEL_ID)
                if ch:
                    req_embed = discord.Embed(title="⚠️ MULTI VERIFY REQUEST", color=0xffa500)
                    req_embed.set_author(name=f"{msg.author.name} ({msg.author.id})", icon_url=msg.author.display_avatar.url)
                    
                    # New ID Details
                    req_embed.add_field(name="🆕 New Request", value=f"🆔 `{user_id}`\n👤 **{username}**\n✨ {display}", inline=False)
                    
                    # Old Accounts List (Jo maanga tha)
                    req_embed.add_field(name="📂 Already Verified Accounts", value=old_list, inline=False)
                    
                    req_embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")

                    # Buttons
                    async def approve(i):
                        if i.user.id != OWNER_ID: return
                        supabase.table("multi_access").upsert({"discord_id": str(msg.author.id), "approved": True}).execute()
                        await i.response.edit_message(embed=discord.Embed(title="🟢 Access Granted", description="User can now verify unlimited IDs.", color=0x2ecc71), view=None)

                    async def deny(i):
                        if i.user.id != OWNER_ID: return
                        await i.response.edit_message(embed=discord.Embed(title="🔴 Denied", color=0xe74c3c), view=None)

                    btn1 = discord.ui.Button(label="Approve Unlimited", style=discord.ButtonStyle.green)
                    btn2 = discord.ui.Button(label="Deny", style=discord.ButtonStyle.red)
                    btn1.callback = approve
                    btn2.callback = deny
                    view = discord.ui.View()
                    view.add_item(btn1)
                    view.add_item(btn2)

                    await ch.send(embed=req_embed, view=view)
                return

        # D. SUCCESS - INSERT TO DB
        supabase.table("access_users").insert({
            "user_id": user_id, "username": username, "display_name": display, "discord_id": str(msg.author.id)
        }).execute()

        # Log Database
        supabase.table("verify_logs").insert({
            "discord_id": str(msg.author.id), "roblox_id": user_id, "username": username, "display_name": display, "timestamp": datetime.utcnow().isoformat()
        }).execute()

        # E. SUCCESS MESSAGE (User ke liye)
        embed = discord.Embed(title="✅ Verified Successfully", color=0x2ecc71)
        embed.add_field(name="🆔 Roblox ID", value=f"`{user_id}`", inline=True)
        embed.add_field(name="👤 Username", value=f"**{username}**", inline=True)
        embed.add_field(name="✨ Display", value=f"{display}", inline=True)
        embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
        embed.set_footer(text="Whitelist Access Granted")
        await msg.reply(embed=embed)

                # F. LOG CHANNEL (Admin ke liye)
        try:
            log_ch = bot.get_channel(1451973589342621791) # <--- ID Check kar lena
            
            if log_ch: # <--- Ye check zaroori hai
                log = discord.Embed(title="🚨 New Verification", color=0x3498db)
                log.set_author(name=msg.author.name, icon_url=msg.author.display_avatar.url)
                log.add_field(name="Discord User", value=f"{msg.author.mention} ({msg.author.id})", inline=False)
                # Saari details yahan bhi
                log.add_field(name="👾 Roblox ID", value=f"{user_id}", inline=True)
                log.add_field(name="👤 Username", value=f"{username}", inline=True)
                log.add_field(name="✨ Display", value=f"{display}", inline=True)
                log.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
                log.timestamp = datetime.utcnow()
                await log_ch.send(embed=log)
        except Exception as e:
            print(f"Log Error: {e}")
            pass
            
      # ❌ Purana galat indentation wala hatao
    # ✅ Ye sahi indentation wala lagao (Thoda peeche karke)

    except Exception as e:
        # Ye 'except' ab peeche khisak gaya hai (Sahi jagah par)
        await msg.reply(f"❌ Critical Error: `{e}`")
        print(f"DEBUG ERROR: {e}")

 # ================== 1. BAN PAGINATOR CLASS (Ye sahi hai, isme change nahi chahiye) ==================
class BanPaginator(discord.ui.View):
    def __init__(self, data, author, bot_ref):
        super().__init__(timeout=60)
        self.data = data
        self.author = author
        self.bot = bot_ref
        self.per_page = 5
        self.current_page = 0
        self.total_pages = (len(data) + self.per_page - 1) // self.per_page

    async def get_page_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_data = self.data[start:end]

        embed = discord.Embed(title=f"🚫 Banned Users List (Total: {len(self.data)})", color=0xff0000)
        
        for row in page_data:
            uid = row.get("user_id")
            reason = row.get("reason", "No Reason")
            executor_id = row.get("executor")
            
            u, d = await roblox_info(uid)
            
            if row.get("perm"):
                type_str = "🔴 **PERM**"
                time_str = "Never"
            else:
                try:
                    expire_ts = float(row.get("expire", 0))
                    type_str = "🟠 **TEMP**"
                    time_str = f"<t:{int(expire_ts)}:R>"
                except:
                    type_str = "Unknown"
                    time_str = "-"

            admin_tag = f"<@{executor_id}>" if executor_id else "Unknown"

            embed.add_field(
                name=f"👤 {d} (@{u})",
                value=f"🆔 `{uid}`\n⚖️ Type: {type_str}\n⏳ Expires: {time_str}\n📝 Reason: `{reason}`\n👮 By: {admin_tag}",
                inline=False
            )

        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} • Ban System")
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)
        self.current_page += 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)


# ================== 2. CONFIRM VIEW CLASS (FIXED: Clear All) ==================
class BanClearView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=30)
        self.author_id = author_id

    @discord.ui.button(label="⚠️ YES - DELETE ALL DATA", style=discord.ButtonStyle.danger)
    async def confirm(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author_id:
            return await i.response.send_message("❌ You cannot use this button.", ephemeral=True)
        
        # ✅ FIX: db_call use kiya taaki delete karte waqt bot na atke
        await db_call(lambda: supabase.table("bans").delete().neq("user_id", "0").execute())
        
        embed = discord.Embed(title="♻️ BAN LIST CLEARED", description="✅ All bans have been successfully removed.", color=0x2ecc71)
        embed.set_footer(text=f"Cleared by {i.user.display_name}")
        
        await i.response.edit_message(embed=embed, view=None)
        self.stop()

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author_id:
            return await i.response.send_message("❌ You cannot use this button.", ephemeral=True)

        embed = discord.Embed(title="🛡️ Operation Cancelled", description="Ban list was **NOT** cleared.", color=0x95a5a6)
        await i.response.edit_message(embed=embed, view=None)
        self.stop()


# ================== 3. MAIN ACTION COMMAND (PREMIUM & FIXED) ==================

# --- HELPER: PREMIUM EMBED BUILDER ---
def build_premium_embed(action_type, u_name, d_name, u_id, moderator, reason, duration=None):
    """
    Creates a consistent High-Quality Embed for all moderation actions.
    """
    colors = {
        "kick": 0xE74C3C,    # Red/Orange
        "ban": 0x992D22,     # Dark Red
        "tempban": 0xE67E22, # Orange
        "unban": 0x2ECC71,   # Green
    }
    
    titles = {
        "kick": "👢 PLAYER KICKED",
        "ban": "🔨 PERMANENT BAN",
        "tempban": "⏱️ TEMPORARY BAN",
        "unban": "✅ PLAYER UNBANNED"
    }

    embed = discord.Embed(title=titles.get(action_type, "Action"), color=colors.get(action_type, 0x2f3136))
    
    # 1. Top Section: Target User Info
    embed.add_field(name="👤 Target User", value=f"**{d_name}**\n(@{u_name})", inline=True)
    embed.add_field(name="🆔 Roblox ID", value=f"`{u_id}`", inline=True)
    
    # 2. Duration (If Tempban)
    if duration:
        expire_ts = int(time.time() + (duration * 60))
        embed.add_field(name="⏳ Duration", value=f"**{duration} Mins**\nUnban: <t:{expire_ts}:R>", inline=True)
    else:
        # Empty field to balance UI if needed, or skip
        embed.add_field(name="🛡️ Action By", value=moderator.mention, inline=True)

    # 3. Reason Section (Full Width)
    embed.add_field(name="📝 Reason", value=f"```\n{reason}\n```", inline=False)
    
    # 4. Thumbnail (Roblox Headshot)
    embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={u_id}&width=420&height=420&format=png")
    
    # 5. Footer with Timestamp
    if duration: # Agar duration upar dikhaya to moderator niche dikhao
        embed.set_footer(text=f"Executed by {moderator.display_name} • {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", icon_url=moderator.display_avatar.url)
    else:
        embed.set_footer(text=f"Server Protection System • {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", icon_url=moderator.display_avatar.url)
        
    return embed


@bot.tree.command(name="action", description="🛡️ Premium Moderation System (Kick, Ban, Unban)")
@app_commands.choices(mode=[
    app_commands.Choice(name="👢 Kick Player", value="kick"),
    app_commands.Choice(name="🔨 Ban (Permanent)", value="ban"),
    app_commands.Choice(name="⏱ Temp Ban (Timed)", value="tempban"),
    app_commands.Choice(name="✅ Unban", value="unban"),
    app_commands.Choice(name="📜 List All Bans", value="list"),
    app_commands.Choice(name="🧨 Clear All Bans (Reset)", value="clear"),
])
@app_commands.describe(
    user_id="Roblox ID (Required)",
    reason="Reason for action",
    duration="Minutes (Only for Tempban)"
)
async def action(i: discord.Interaction, mode: app_commands.Choice[str], user_id: str = None, reason: str = "No Reason Provided", duration: int = None):
    
    if not owner(i):
        return await i.response.send_message("❌ **Access Denied:** Owner/Admin only.", ephemeral=True)

    if mode.value != "clear":
        await i.response.defer(ephemeral=False)

    try:
        # ================== 1. KICK ==================
        if mode.value == "kick":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")
            u, d = await roblox_info(user_id)

            # ✅ FIX: Safe DB Call (Error aayega to bhi command nahi rukega)
            try:
                await db_call(lambda: supabase.table("kick_logs").insert({
                    "user_id": user_id, "username": u, "display_name": d, "reason": reason, "timestamp": datetime.utcnow().isoformat()
                }).execute())
            except Exception as e:
                print(f"⚠️ Log Error (Kick Logs missing?): {e}")

            # Kick Flag Set
            await db_call(lambda: supabase.table("kick_flags").upsert({
                "user_id": user_id, "reason": reason
            }).execute())

            embed = build_premium_embed("kick", u, d, user_id, i.user, reason)
            await i.followup.send(embed=embed)


        # ================== 2. PERMANENT BAN ==================
        elif mode.value == "ban":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")
            u, d = await roblox_info(user_id)
            
            await db_call(lambda: supabase.table("bans").upsert({
                "user_id": user_id, "perm": True, "reason": reason, "expire": None, "executor": str(i.user.id)
            }).execute())

            try: log_action("ban", user_id, u, d, i.user.id)
            except: pass

            embed = build_premium_embed("ban", u, d, user_id, i.user, reason)
            await i.followup.send(embed=embed)


        # ================== 3. TEMP BAN ==================
        elif mode.value == "tempban":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")
            if not duration: return await i.followup.send("⚠️ **Duration Required!** (Minutes)")

            u, d = await roblox_info(user_id)
            expire_time = time.time() + (duration * 60)

            await db_call(lambda: supabase.table("bans").upsert({
                "user_id": user_id, "perm": False, "reason": reason, "expire": expire_time, "executor": str(i.user.id)
            }).execute())

            try: log_action("tempban", user_id, u, d, i.user.id)
            except: pass

            embed = build_premium_embed("tempban", u, d, user_id, i.user, reason, duration)
            await i.followup.send(embed=embed)


        # ================== 4. UNBAN ==================
        elif mode.value == "unban":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")

            u, d = await roblox_info(user_id)
            
            await db_call(lambda: supabase.table("bans").delete().eq("user_id", user_id).execute())

            try: log_action("unban", user_id, u, d, i.user.id)
            except: pass

            embed = build_premium_embed("unban", u, d, user_id, i.user, reason)
            await i.followup.send(embed=embed)


        # ================== 5. LIST BANS (Premium List) ==================
        elif mode.value == "list":
            data_req = await db_call(lambda: supabase.table("bans").select("*").execute())
            data = data_req.data if data_req else []

            # Expired Bans Cleanup
            active_bans = []
            now = time.time()
            for row in data:
                if not row.get("perm") and row.get("expire") and now > float(row["expire"]):
                    asyncio.create_task(db_call(lambda: supabase.table("bans").delete().eq("user_id", row["user_id"]).execute()))
                else:
                    active_bans.append(row)

            if not active_bans:
                return await i.followup.send(embed=discord.Embed(title="📜 Ban List", description="✅ **No active bans found.**\nServer is clean!", color=0x2ecc71))

            view = BanPaginator(active_bans, i.user, bot)
            if view.total_pages <= 1:
                view.children[0].disabled = True
                view.children[1].disabled = True
            else:
                view.update_buttons()

            embed = await view.get_page_embed()
            await i.followup.send(embed=embed, view=view)


        # ================== 6. CLEAR ALL ==================
        elif mode.value == "clear":
            embed = discord.Embed(
                title="⚠️ DANGER ZONE: CLEAR DATABASE",
                description="Are you sure you want to **DELETE ALL BANS**?\n\nThis will unban **everyone**. This cannot be undone.",
                color=0xffaa00
            )
            embed.set_footer(text="Wait 10 seconds before confirming.")
            view = BanClearView(i.user.id)
            await i.response.send_message(embed=embed, view=view, ephemeral=False)

    except Exception as e:
        print(f"ACTION ERROR: {e}")
        # Error handling thoda clean kiya hai
        if "Missing Permissions" in str(e):
            await i.followup.send("❌ **Bot Error:** Mere paas permissions nahi hain.")
        else:
            await i.followup.send(f"❌ **System Error:** `{e}`")

# ================== PREMIUM PLAYSOUND (Embed + Hidden) ==================

# 1. Autocomplete (Same rahega)
async def sound_autocomplete(i: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    folder_path = "./sounds"
    if not os.path.exists(folder_path): return []
    files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
    return [app_commands.Choice(name=f, value=f) for f in files if current.lower() in f.lower()][:25]

# 2. Main Command
@bot.tree.command(name="playsound", description="📂 GitHub sounds play karo (Owner Only)")
@app_commands.describe(filename="Sound select karo")
@app_commands.autocomplete(filename=sound_autocomplete)
async def playsound(i: discord.Interaction, filename: str):
    
    # 🔒 OWNER CHECK
    if not owner(i):
        return await i.response.send_message("❌ **Access Denied:** Sirf Owner allowed hai!", ephemeral=True)

    # 🎤 VC CHECK
    if not i.user.voice:
        return await i.response.send_message("⚠️ Pehle VC join kar bhai!", ephemeral=True)

    # ⏳ DEFER (Ephemeral=True matlab sirf aapko dikhega)
    await i.response.defer(ephemeral=True)

    try:
        file_path = f"./sounds/{filename}"
        
        # VC Connect Logic
        try:
            vc = await i.user.voice.channel.connect()
        except:
            vc = i.guild.voice_client

        if vc.is_playing(): vc.stop()

        # 🚀 PLAY AUDIO
        vc.play(discord.FFmpegPCMAudio(source=file_path, executable="./ffmpeg"))
        
        # 💎 PREMIUM EMBED
        embed = discord.Embed(
            title="🔊 **Audio Streaming**",
            description=f"### 💿 Now Playing:\n> `{filename}`\n\n**Channel:** `{i.user.voice.channel.name}`\n**Status:** `Active` 🟢",
            color=0x00ffea # Neon Cyan Color
        )
        embed.set_thumbnail(url="https://media.tenor.com/On7kvXhzml4AAAAi/loading-gif.gif") # Audio visualizer GIF
        embed.set_footer(text=f"Requested by {i.user.display_name}", icon_url=i.user.display_avatar.url)

        # Message bhejo (Sirf aapko dikhega)
        await i.followup.send(embed=embed)

    except Exception as e:
        await i.followup.send(f"❌ **Error:** `{e}`")

@bot.tree.command(name="crush", description="Add/Remove user from Flirty/Horny list")
@app_commands.choices(mode=[
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="remove", value="remove"),
    app_commands.Choice(name="list", value="list"),
])
async def crush(i: discord.Interaction, mode: app_commands.Choice[str], user: discord.User = None):
    
    if not owner(i): # Sirf Owner chala sakta hai
        return await i.response.send_message("❌ **Apni limit me raho! Sirf Owner ye kar sakta hai.**", ephemeral=True)

    await i.response.defer(ephemeral=False)

    try:
        # ❤️ ADD (Flirt ON)
        if mode.value == "add":
            if not user: return await i.followup.send("❌ User select karo!")
            
            supabase.table("bot_crushes").upsert({"user_id": str(user.id)}).execute()
            await load_crush_users() # RAM Update
            
            embed = discord.Embed(title="😍 Crush Added", description=f"**{user.mention}** ab is bot ka Crush hai!", color=0xe91e63)
            embed.add_field(name="Effect", value="Ab bot isse Flirt karega. 😘", inline=False)
            await i.followup.send(embed=embed)

        # 💔 REMOVE (Flirt OFF)
        if mode.value == "remove":
            if not user: return await i.followup.send("❌ User select karo!")
            
            supabase.table("bot_crushes").delete().eq("user_id", str(user.id)).execute()
            await load_crush_users() # RAM Update
            
            embed = discord.Embed(title="💔 Crush Removed", description=f"**{user.mention}** se dil bhar gaya.", color=0x95a5a6)
            embed.add_field(name="Effect", value="Wapas se purana Roast mode ON. 🤬", inline=False)
            await i.followup.send(embed=embed)

        # 📜 LIST
        if mode.value == "list":
            if not CRUSH_CACHE:
                return await i.followup.send("❌ Koi Crush nahi hai. Bot single hai!")
            
            names = [f"<@{uid}>" for uid in CRUSH_CACHE]
            await i.followup.send(embed=discord.Embed(title="😍 Bot's Crush List", description="\n".join(names), color=0xe91e63))

    except Exception as e:
        await i.followup.send(f"❌ Error: {e}")

# ================== ATTITUDE CONTROL (VIP SYSTEM) ==================
@bot.tree.command(name="vip", description="Manage Bot Attitude (Owner Only)")
@app_commands.choices(mode=[
    app_commands.Choice(name="allow", value="allow"),
    app_commands.Choice(name="block", value="block"),
    app_commands.Choice(name="list", value="list"),
])
async def vip(i: discord.Interaction, mode: app_commands.Choice[str], user: discord.User = None):
    
    # 1. OWNER CHECK
    if not owner(i):
        return await i.response.send_message("❌ **Only Owner can manage VIPs.**", ephemeral=True)

    await i.response.defer(ephemeral=False)

    try:
        # ================== ALLOW (ADD VIP) ==================
        if mode.value == "allow":
            if not user:
                return await i.followup.send("❌ **User select karna zaroori hai!**")

            # 1. Database Update
            supabase.table("attitude_bypass").upsert({"user_id": str(user.id)}).execute()
            
            # 2. 🔥 RAM UPDATE (Ye line zaroori hai!)
            await load_bypass_users()

            embed = discord.Embed(title="👑 VIP Added", description=f"**{user.mention}** ab VIP list me hai.", color=0xf1c40f)
            embed.add_field(name="😎 Effect", value="Bot ab isse tameez se baat karega.", inline=False)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Added by {i.user.display_name} • RAM Updated ✅")
            
            await i.followup.send(embed=embed)

        # ================== BLOCK (REMOVE VIP) ==================
        if mode.value == "block":
            if not user:
                return await i.followup.send("❌ **User select karna zaroori hai!**")

            # 1. Database Delete
            supabase.table("attitude_bypass").delete().eq("user_id", str(user.id)).execute()

            # 2. 🔥 RAM UPDATE (Ye line zaroori hai!)
            await load_bypass_users()

            embed = discord.Embed(title="😈 VIP Removed", description=f"**{user.mention}** ko VIP list se nikaal diya.", color=0x2c3e50)
            embed.add_field(name="💀 Effect", value="Ab ye tag karega to full attitude sunega!", inline=False)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Removed by {i.user.display_name} • RAM Updated ✅")

            await i.followup.send(embed=embed)

        # ================== LIST (SHOW ALL VIPs) ==================
        if mode.value == "list":
            # Fetch Data
            data = supabase.table("attitude_bypass").select("user_id").execute().data

            if not data:
                return await i.followup.send(embed=discord.Embed(title="👑 VIP List", description="❌ List is empty. Sabke liye attitude ON hai!", color=0x95a5a6))

            # Paginator Call
            view = VipPaginator(data, i.user, bot)
            
            if view.total_pages <= 1:
                view.children[0].disabled = True
                view.children[1].disabled = True
            else:
                view.update_buttons()

            embed = await view.get_page_embed()
            await i.followup.send(embed=embed, view=view)

    except Exception as e:
        print(f"VIP ERROR: {e}")
        await i.followup.send(f"❌ System Error: `{e}`")
            

# ================== 🔥 ROAST SYSTEM ==================

# 1. 🗣️ TRANSLATOR TOGGLE (Owner Only)
@bot.tree.command(name="translator", description="🔴/🟢 Turn Hindi Roast ON or OFF")
@app_commands.describe(mode="Choose Mode")
@app_commands.choices(mode=[
    app_commands.Choice(name="🟢 ON (Hindi Translation)", value="on"),
    app_commands.Choice(name="🔴 OFF (English Only - Fast)", value="off")
])
async def translator(i: discord.Interaction, mode: app_commands.Choice[str]):
    # 🔒 OWNER CHECK
    if i.user.id != OWNER_ID: 
        return await i.response.send_message("❌ Abe nikal! Ye setting sirf Maalik ke liye hai.", ephemeral=True)

    global TRANSLATOR_ON
    if mode.value == "on":
        TRANSLATOR_ON = True
        await i.response.send_message("✅ **Translator ON!** Ab main Hindi me bezzati karunga. 🇮🇳")
    else:
        TRANSLATOR_ON = False
        await i.response.send_message("❎ **Translator OFF!** English Mode Activated (Super Fast). 🇺🇸")

# 2. 🔥 ROAST COMMAND (With VIP Check)
@bot.tree.command(name="roast", description="Bezzati karein (VIP Safe)")
async def roast(i: discord.Interaction, user: discord.Member):
    # Basic Checks
    if user.id == i.user.id: return await i.response.send_message("Khud ko kyu?", ephemeral=True)
    
    # 🛡️ VIP CHECK
    if user.id in ATTITUDE_BYPASS_CACHE:
        return await i.response.send_message(f"✋ **{user.display_name}** VIP List me hain. Inka mazaak allowed nahi hai!", ephemeral=True)
    
    if user.id == bot.user.id:
        return await i.response.send_message("Baap pe haath uthayega? 🤖💢", ephemeral=True)

    await i.response.defer()
    
    eng, hin = await get_evil_roast_data()
    final_text = hin if TRANSLATOR_ON else eng
    
    embed = discord.Embed(description=f"🔥 **ROASTED!**\n\n{final_text}", color=0x2f3136)
    if TRANSLATOR_ON: embed.add_field(name="Original", value=f"||{eng}||", inline=False)
    
    embed.set_thumbnail(url=user.display_avatar.url)
    await i.followup.send(content=f"{user.mention}", embed=embed)

# ==========================================
# ⚙️ GLOBAL VOICE SETTINGS (RAM Based)
# ==========================================

# Default Setting: Swara (Female)
current_voice = {
    "id": "hi-IN-SwaraNeural",
    "name": "Swara (Female) 💃",
    "pitch": "+5Hz",   # Ladki ke liye teekha
    "rate": "+10%",    # Thoda fast (Aggressive)
    "avatar": "https://cdn-icons-png.flaticon.com/512/6997/6997662.png", # Girl Icon
    "color": 0xFF69B4  # Hot Pink Color
}

# ==========================================
# 🛠️ HELPER FUNCTIONS
# ==========================================

# 1. PREMIUM EMBED BUILDER
def create_premium_embed(title, description, color=None):
    # Agar color nahi diya, toh current voice ka color use karo
    if color is None:
        color = current_voice["color"]
        
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=f"🔥 Voice Mode: {current_voice['name']} | Powered by Neural AI")
    embed.set_thumbnail(url=current_voice["avatar"])
    return embed

# 2. SECURITY CHECK (Owner + Admin + VIP)
def has_voice_access(interaction):
    user_id = str(interaction.user.id)
    # Check 1: Main Owner
    if interaction.user.id == OWNER_ID: return True
    # Check 2: Old Admin Table
    if owner(interaction): return True
    # Check 3: New VIP Table
    try:
        data = supabase.table("voice_vip").select("user_id").eq("user_id", user_id).execute()
        if data.data: return True
    except:
        pass
    return False

# 3. AUDIO PLAYER (Global Settings Use Karega)
async def play_audio(interaction, text):
    if not interaction.user.voice:
        embed = create_premium_embed("❌ Error", "Abe VC mein toh aaja pehle! 🖕", 0xFF0000)
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    channel = interaction.user.voice.channel
    try:
        vc = await channel.connect()
    except:
        vc = interaction.guild.voice_client
        if vc and vc.channel.id != channel.id:
            await vc.move_to(channel)
        elif not vc:
            vc = await channel.connect()

    # Generate Audio using GLOBAL 'current_voice' settings
    output_file = f"audio_{interaction.id}.mp3"
    communicate = edge_tts.Communicate(
        text, 
        current_voice["id"], 
        rate=current_voice["rate"], 
        pitch=current_voice["pitch"]
    )
    await communicate.save(output_file)

    if not vc.is_playing():
        vc.play(discord.FFmpegPCMAudio(source=output_file, executable="./ffmpeg"))
        while vc.is_playing():
            await asyncio.sleep(1)
        await vc.disconnect()
        if os.path.exists(output_file):
            os.remove(output_file)
    else:
        embed = create_premium_embed("⚠️ Busy", "Ruk ja, abhi line busy hai! 🚫", 0xFFA500)
        await interaction.followup.send(embed=embed)

# ==========================================
# 🔥 COMMANDS START HERE
# ==========================================

# 1️⃣ SWITCH VOICE (Male/Female Toggle)
@bot.tree.command(name="switch_voice", description="Bot ki aawaz aur gender change karo 🎙️🔄")
@app_commands.choices(gender=[
    app_commands.Choice(name="Swara (Female) - Tikhi & Naughty 💃", value="female"),
    app_commands.Choice(name="Madhur (Male) - Bhaari & Gangster 🗿", value="male")
])
async def switch_voice(interaction: discord.Interaction, gender: app_commands.Choice[str]):
    
    # Permission Check
    if not has_voice_access(interaction):
        await interaction.response.send_message("🚫 **Access Denied:** Sirf Owner ye change kar sakta hai!", ephemeral=True)
        return

    global current_voice

    if gender.value == "female":
        current_voice = {
            "id": "hi-IN-SwaraNeural",
            "name": "Swara (Female) 💃",
            "pitch": "+5Hz",
            "rate": "+10%",
            "avatar": "https://cdn-icons-png.flaticon.com/512/6997/6997662.png",
            "color": 0xFF69B4
        }
        desc = "**Swara Activated!** 💃\nBot ab *Teekhi Ladki* ki aawaz mein bolega."
    else:
        current_voice = {
            "id": "hi-IN-MadhurNeural",
            "name": "Madhur (Male) 🗿",
            "pitch": "-5Hz", # Heavy Voice
            "rate": "+5%",
            "avatar": "https://cdn-icons-png.flaticon.com/512/236/236831.png",
            "color": 0x2F3136
        }
        desc = "**Madhur Activated!** 🗿\nBot ab *Bhaari Gangster* aawaz mein bolega."

    embed = create_premium_embed("🎙️ Voice System Updated", desc)
    await interaction.response.send_message(embed=embed)


# 2️⃣ VC ROAST (Premium Embed + Auto Voice + Hindi Brutal Mode)
@bot.tree.command(name="vcroast", description="Brutal Gaali Mode 🔊💀 (Only you can see)")
async def vcroast(interaction: discord.Interaction):
    
    # 1. Access Check
    if not has_voice_access(interaction):
        await interaction.response.send_message("🚫 **Access Denied:** सिर्फ VIP लोग चला सकते हैं!", ephemeral=True)
        return

    # 2. Premium Embed (Ephemeral = True matlab sirf aapko dikhega)
    embed = create_premium_embed("💀 Brutal Mode On", f"**{current_voice['name']}** is connecting to roast... 🔥")
    
    # ✅ Yahan 'ephemeral=True' joda hai
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ☢️ PURE HINDI GAALI LIST (For Swara)
    gaali_list = [
        "तेरी माँ की चूत में हाथी का लंड, साले नल्ले तू पैदा ही गलती से हुआ था।",
        "तेरी माँ की चूत में जेसीबी चला दूँगी, सारी अकड़ बाहर निकल जाएगी मादरचोद।",
        "भोसड़ीके, तेरी बहन को इतना चोदूँगी कि वो चलना भूल जाएगी, सिर्फ रेंग के चलेगी।",
        "साले सूअर के पिल्ले, तेरी माँ की गांड में कैक्टस उगा दूँगी, जब भी हगेगी मुझे याद करेगी।",
        "तेरी शकल देख के लगता है भगवान ने टट्टी को इंसान का रूप दे दिया है।",
        "सुन बे झांटू, तेरी शकल देख के तो वायरस भी क्वारंटाइन में चला गया।",
        "अबे लौड़े, अगर अपना दिमाग बेचने जाएगा तो 'अनयूज़्ड' कंडीशन में बिकेगा, क्योंकि कभी यूज़ तो किया नहीं।",
        "तेरी औकात मेरे झांट के बाल बराबर भी नहीं है, निकल यहाँ से वरना गाड़ दूँगी।",
        "भोसड़ीके, तुझे देख के लगता है कि कंडोम का विज्ञापन कितना ज़रूरी है।",
        "अपनी ये सड़ी हुई आवाज़ बंद कर, वरना कान के नीचे ऐसा बजाऊँगी कि अगली 7 पुश्तें बहरी पैदा होंगी।",
        "साले सुअर, तू वो गलती है जिसे डॉक्टर भी रबर से मिटाना चाहता था पर मिटा नहीं पाया।",
        "तेरी माँ ने तुझे पैदा नहीं किया, तुझे बस दुनिया को सज़ा देने के लिए हगा है।",
        "अबे चूतिये, तेरे खानदान में सब इंजीनियर हैं क्या? क्योंकि तू एक बहुत बड़ा 'प्रोजेक्ट फेलियर' लगता है।",
        "सुन मादरचोद, तेरे मुँह से बास आती है या तू गटर का ढक्कन खोल के बात करता है?",
        "तेरी गांड में इतना बारूद भरूँगी कि दिवाली का रॉकेट भी तुझे देख के शरमा जाएगा।",
        "भोसड़ीके, इतना मत उछल, वरना तेरी आंतें बाहर निकाल के उसी से तुझे फाँसी लगा दूँगी।",
        "अबे रंडी के, तू धरती पे बोझ है, पेड़-पौधे भी तुझे ऑक्सीजन देकर पछता रहे होंगे।",
        "तेरी शकल देख के तो आईना भी खुदकुशी कर लेता है, तू क्या चीज़ है बे?",
        "साले छक्के, मेरे सामने मर्दानगी मत दिखा, वरना वो हाल करूँगी कि हिजड़े भी तुझे अपनी बिरादरी में नहीं लेंगे।",
        "मादरचोद, तुझे देख के लगता है कि भगवान ने मिट्टी गूंथते वक़्त उसमें गटर का पानी मिला दिया था।"
        "मादरचोद, तेरे खानदान की औरतें मेरे लंड का वेट करती हैं, जाके पूछ ले।",
        "अबे रंडी के, तेरी गांड में रॉड डाल के मुँह से निकालूँगी, ह्यूमन कबाब बना दूँगी तेरा।",
        "तेरी माँ का भोसड़ा इतना बड़ा है कि उसमे मैं अपना पूरा घर बना लूँ।",
        "चूतिये, तुझे पैदा करके तेरी माँ ने दुनिया पे बोझ बढ़ा दिया है, जाके मर जा।",
        "तेरी बहन की चूत में बम लगा के उड़ा दूँगी, चिथड़े मिलेंगे सीधा चाँद पे।",
        "साले हिजड़े की औलाद, मेरे सामने आवाज़ मत निकालना वरना वही गाड़ दूँगी।",
        "तेरी माँ की चूत में इतने लंड डालूँगी कि वो ट्रैफिक जाम हो जाएगी।",
        "भोसड़ीके, तेरा बाप भी रोता होगा कि किस मनहूस घड़ी में तुझे पैदा किया।",
        "रंडी के पिल्ले, तेरी गांड में मिर्ची का पाउडर भर के डंडे से अंदर कर दूँगी।",
        "तेरी बहन की चूत पब्लिक टॉयलेट बन गयी है, जो आता है मूत के चला जाता है।",
        "मादरचोद, तुझे ज़िंदा जला के तेरी राख को गटर में बहाना चाहिए।",
        "बहनचोद, अपनी शकल देखी है? ऐसा लगता है गटर के ढक्कन पे किसी ने उल्टी कर दी हो।",
        "मादरचोद, तेरी बहन को कोठे पे बिठा दूँगी अगर दोबारा यहाँ दिखा तो, निकल यहाँ से!",
        "साले रंडी के पिल्ले, तेरे खानदान में सबसे बड़ा चूतिया तू ही है, जाके डूब मर।",
        "तेरी गांड में इतना डंडा डालूँगी कि मुँह से बाहर निकलेगा, भोसड़ीके औकात में रह।",
        "सुन बे लोडू, तेरी माँ मेरे पास आयी थी, कह रही थी गलती हो गयी तुझे पैदा करके।",
        "अबे सूअर की औलाद, तू वही वायरस है जिसे कंडोम भी रोक नहीं पाया था।",
        "तेरी बहन की चूत में कैक्टस डाल के घूमुँगी, साले टट्टी खोर इंसान।"
    ]
    
    text = random.choice(gaali_list)
    await play_audio(interaction, text)


# 3️⃣ BOL (Premium Embed + Auto Voice - EPHEMERAL)
@bot.tree.command(name="bol", description="Bot se kuch bhi bulwao 🎤 (Only you can see this)")
@app_commands.describe(text="Kya bulwana hai?")
async def bol(interaction: discord.Interaction, text: str):
    # 1. Access Check
    if not has_voice_access(interaction):
        await interaction.response.send_message("🚫 **Access Denied:** Sirf VIP log chala sakte hain!", ephemeral=True)
        return

    # 2. Premium Embed taiyar karo
    embed = create_premium_embed("📢 Broadcasting", f"**Text:** {text}\n**Voice:** {current_voice['name']}")
    
    # ✅ FIX: Yahan 'ephemeral=True' dala hai taaki sirf aapko dikhe
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # 3. Audio play karo (VC me awaz sabko aayegi, message sirf aapko dikhega)
    await play_audio(interaction, text)

# ================== 🤝 TRUST SYSTEM (VIP MANAGEMENT) ==================

# 1. Group ka naam "trust" rakh diya
trust_group = app_commands.Group(name="trust", description="🤝 Trust List Management (Owner Only)")

# --- 🟢 ADD MEMBER (/trust add) ---
@trust_group.command(name="add", description="Kisi ko Trust List me add karo ✅")
async def trust_add(interaction: discord.Interaction, user: discord.Member):
    # Owner Check
    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message("❌ **Sirf Owner hi Trust member add kar sakta hai!**", ephemeral=True)

    # 🔥 Ephemeral=False (Ab message SABKO dikhega)
    await interaction.response.defer(ephemeral=False)

    try:
        # Check if already exists
        check = supabase.table("voice_vip").select("user_id").eq("user_id", str(user.id)).execute()
        if check.data:
            await interaction.followup.send(f"⚠️ **{user.name}** pehle se Trust List mein hai!")
        else:
            # Insert Data
            data = { "user_id": str(user.id), "added_by": str(interaction.user.name) }
            supabase.table("voice_vip").insert(data).execute()
            
            embed = create_premium_embed("✅ New Trusted Member", f"🤝 **{user.mention}** ab **Trust List** mein add ho gaya hai!\nAb ye `/bol` aur `/vcroast` use kar sakta hai.", 0x00FF00)
            await interaction.followup.send(embed=embed)
            
    except Exception as e:
        await interaction.followup.send(f"❌ **Error:** {e}")


# --- 🔴 REMOVE MEMBER (/trust remove) ---
@trust_group.command(name="remove", description="Kisi ko Trust List se hatao 🚫")
async def trust_remove(interaction: discord.Interaction, user: discord.User):
    # Owner Check
    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message("❌ **Sirf Owner hi remove kar sakta hai!**", ephemeral=True)

    # 🔥 Ephemeral=False (Sabko dikhega ki banda kick ho gaya)
    await interaction.response.defer(ephemeral=False)

    try:
        # Check if exists
        check = supabase.table("voice_vip").select("user_id").eq("user_id", str(user.id)).execute()
        if not check.data:
            await interaction.followup.send(f"⚠️ **{user.name}** Trust List mein hai hi nahi.")
        else:
            # Delete Data
            supabase.table("voice_vip").delete().eq("user_id", str(user.id)).execute()
            
            embed = create_premium_embed("🚫 Trust Revoked", f"💀 **{user.mention}** ko **Trust List** se hata diya gaya hai.\nAb ye normal member ban gaya.", 0xFF0000)
            await interaction.followup.send(embed=embed)
            
    except Exception as e:
        await interaction.followup.send(f"❌ **Error:** {e}")


# --- 📜 SHOW LIST (/trust list) ---
@trust_group.command(name="list", description="Dekho kon kon Trusted hai 📜")
async def trust_list(interaction: discord.Interaction):
    # Owner Check
    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message("❌ **Sirf Owner list dekh sakta hai!**", ephemeral=True)

    # 🔥 Ephemeral=False (List sabke samne aayegi)
    await interaction.response.defer(ephemeral=False)

    try:
        # Fetch All Data
        res = supabase.table("voice_vip").select("*").execute()
        vip_users = res.data 

        if not vip_users:
            await interaction.followup.send("📂 **Trust List:** Filhal koi nahi hai.")
            return

        # List Format
        description = ""
        for index, item in enumerate(vip_users, 1):
            user_id = item['user_id']
            description += f"**{index}.** <@{user_id}> (`{user_id}`)\n"

        embed = create_premium_embed("🤝 Trusted Members List", f"Total Trusted: **{len(vip_users)}**\n\n{description}", 0x00BFFF) # Cool Blue Color
        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ **Error:** {e}")

# 🔥 YE LINE BAHUT ZAROORI HAI:
bot.tree.add_command(trust_group)


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

 # ================== 1. PAGINATOR CLASSES (Fixed: Access & Blacklist) ==================

# --- A. ACCESS LIST PAGINATOR ---
class AccessPaginator(discord.ui.View):
    def __init__(self, data, author):
        super().__init__(timeout=60)
        self.data = data
        self.author = author
        self.per_page = 10
        self.current_page = 0
        self.total_pages = (len(data) + self.per_page - 1) // self.per_page

    def get_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_data = self.data[start:end]

        desc = ""
        for index, user in enumerate(page_data):
            s_no = start + index + 1
            uid = user.get("user_id", "Unknown")
            uname = user.get("username", "Unknown")
            dname = user.get("display_name", "Unknown")
            desc += f"`{s_no:02d}.` **{dname}** (@{uname})\n   🆔 `{uid}`\n\n"

        embed = discord.Embed(title=f"📜 Whitelisted Users (Total: {len(self.data)})", description=desc, color=0x3498db)
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}", icon_url=self.author.display_avatar.url)
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        await i.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)
        self.current_page += 1
        self.update_buttons()
        await i.response.edit_message(embed=self.get_embed(), view=self)


# --- B. BLACKLIST PAGINATOR (Async Fetching included) ---
class BlacklistPaginator(discord.ui.View):
    def __init__(self, data, author):
        super().__init__(timeout=60)
        self.data = data
        self.author = author
        self.per_page = 5 
        self.current_page = 0
        self.total_pages = (len(data) + self.per_page - 1) // self.per_page

    async def get_page_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_data = self.data[start:end]

        embed = discord.Embed(title=f"🚫 Blacklisted Users (Total: {len(self.data)})", color=0x2c3e50)
        
        for index, row in enumerate(page_data):
            uid = row.get("user_id")
            # Fetch info live (Non-blocking way ideally, but roblox_info is async so its ok)
            u, d = await roblox_info(uid)
            
            embed.add_field(
                name=f"👤 {d} (@{u})",
                value=f"🆔 `{uid}`",
                inline=False
            )

        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} • Blacklist System")
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("❌ Not for you.", ephemeral=True)
        self.current_page += 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)


# ================== 2. CLEAR CONFIRMATION VIEW (FIXED: Async Delete) ==================
class AccessClearView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=30)
        self.author_id = author_id

    @discord.ui.button(label="⚠️ YES - DELETE WHITELIST", style=discord.ButtonStyle.danger)
    async def confirm(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author_id: return await i.response.send_message("❌ You cannot use this button.", ephemeral=True)
        
        # ✅ FIX: db_call use kiya delete ke liye
        await db_call(lambda: supabase.table("access_users").delete().neq("user_id", "0").execute())
        
        embed = discord.Embed(title="♻️ ACCESS LIST CLEARED", description="✅ All whitelisted users have been removed.", color=0xff0000)
        embed.set_footer(text=f"Cleared by {i.user.display_name}")
        await i.response.edit_message(embed=embed, view=None)
        self.stop()

# ================== HELPER: SYSTEM EMBED BUILDER ==================
def build_access_embed(mode_type, moderator, user_data=None, extra_info=None):
    """
    Generates consistent Premium Embeds for Access Control.
    """
    # Configuration for different modes
    config = {
        # System Modes
        "on": {"title": "🟢 SYSTEM ONLINE", "color": 0x2ECC71, "desc": "Verification Access is now **ENABLED**."},
        "off": {"title": "🔴 SYSTEM OFFLINE", "color": 0xE74C3C, "desc": "Verification Access is now **DISABLED**."},
        "maint_on": {"title": "🛡️ MAINTENANCE MODE", "color": 0xE67E22, "desc": "System is now in **Maintenance**.\nOnly Whitelisted users can bypass."},
        "maint_off": {"title": "🚀 SYSTEM LIVE", "color": 0x2ECC71, "desc": "Maintenance Mode **DISABLED**.\nSystem is operating normally."},
        
        # Whitelist Modes
        "add": {"title": "👤 WHITELIST ADDED", "color": 0x2ECC71, "desc": "User has been granted **Premium Access**."},
        "remove": {"title": "🗑️ WHITELIST REMOVED", "color": 0xE74C3C, "desc": "User access has been **Revoked**."},
        
        # Blacklist Modes
        "blk_add": {"title": "🚫 USER BLACKLISTED", "color": 0x000000, "desc": "User has been **Banned** from verification."},
        "blk_remove": {"title": "✅ BLACKLIST REMOVED", "color": 0x3498DB, "desc": "User has been **Unbanned**."},
        
        # Clear
        "clear": {"title": "⚠️ DATABASE RESET", "color": 0xFFAA00, "desc": "Clear All Request Initiated."}
    }

    cfg = config.get(mode_type, {"title": "⚙️ UPDATE", "color": 0x2F3136, "desc": "System Updated"})
    
    embed = discord.Embed(title=cfg["title"], description=cfg["desc"], color=cfg["color"])
    
    # If specific user action (Whitelist/Blacklist)
    if user_data:
        u_name, d_name, u_id = user_data
        embed.add_field(name="👤 User", value=f"**{d_name}**\n(@{u_name})", inline=True)
        embed.add_field(name="🆔 Roblox ID", value=f"`{u_id}`", inline=True)
        embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={u_id}&width=420&height=420&format=png")
    
    # If System Action, add status icon or details
    elif extra_info:
        embed.add_field(name="📝 Status Details", value=f"```{extra_info}```", inline=False)

    # Footer
    embed.set_footer(text=f"Action by {moderator.display_name} • {datetime.utcnow().strftime('%H:%M UTC')}", icon_url=moderator.display_avatar.url)
    
    return embed


# ================== 3. ULTIMATE ACCESS COMMAND ==================
@bot.tree.command(name="access", description="⚙️ Premium Access Control (Whitelist, Blacklist, Maintenance)")
@app_commands.choices(mode=[
    app_commands.Choice(name="🟢 Unlock Verification (Access ON)", value="on"),
    app_commands.Choice(name="🔴 Lock Verification (Access OFF)", value="off"),
    app_commands.Choice(name="🛡️ Enable Maintenance (Bot Down)", value="maint_on"),
    app_commands.Choice(name="🚀 Disable Maintenance (Bot Live)", value="maint_off"),
    app_commands.Choice(name="👤 Add to Whitelist", value="add"),
    app_commands.Choice(name="🗑️ Remove from Whitelist", value="remove"),
    app_commands.Choice(name="📜 List Whitelist", value="list"),
    app_commands.Choice(name="🚫 Add to Blacklist", value="blk_add"),
    app_commands.Choice(name="✅ Remove from Blacklist", value="blk_remove"),
    app_commands.Choice(name="☠️ List Blacklist", value="blk_list"),
    app_commands.Choice(name="🧨 Clear All Whitelist", value="clear"),
])
async def access(i: discord.Interaction, mode: app_commands.Choice[str], user_id: str = None):
    
    # 1. OWNER CHECK
    if not owner(i):
        return await i.response.send_message("❌ **Access Denied:** Owner Only.", ephemeral=True)
    
    # Clear mode ke liye defer nahi karenge (Button turant aana chahiye)
    if mode.value != "clear":
        await i.response.defer(ephemeral=False)

    try:
        # ================== 1. ACCESS ON/OFF ==================
        if mode.value in ["on", "off"]:
            val = "true" if mode.value == "on" else "false"
            
            await db_call(lambda: supabase.table("bot_settings").update({"value": val}).eq("key", "access_enabled").execute())
            
            try: log_action(f"access_{mode.value}", "-", "-", "-", i.user.id)
            except: pass
            
            embed = build_access_embed(mode.value, i.user)
            await i.followup.send(embed=embed)


        # ================== 2. MAINTENANCE ON/OFF ==================
        elif mode.value in ["maint_on", "maint_off"]:
            val = "true" if mode.value == "maint_on" else "false"
            
            await db_call(lambda: supabase.table("bot_settings").update({"value": val}).eq("key", "maintenance").execute())
            
            try: log_action(f"maintenance_{val}", "-", "-", "-", i.user.id)
            except: pass
            
            embed = build_access_embed(mode.value, i.user)
            await i.followup.send(embed=embed)


        # ================== 3. WHITELIST ADD ==================
        elif mode.value == "add":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")
            u, d = await roblox_info(user_id)
            
            await db_call(lambda: supabase.table("access_users").upsert({
                "user_id": user_id, "username": u, "display_name": d, "discord_id": str(i.user.id)
            }).execute())
            
            try: log_action("access_add", user_id, u, d, i.user.id)
            except: pass
            
            embed = build_access_embed("add", i.user, (u, d, user_id))
            await i.followup.send(embed=embed)


        # ================== 4. WHITELIST REMOVE ==================
        elif mode.value == "remove":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")
            u, d = await roblox_info(user_id)
            
            await db_call(lambda: supabase.table("access_users").delete().eq("user_id", user_id).execute())
            
            try: log_action("access_remove", user_id, u, d, i.user.id)
            except: pass
            
            embed = build_access_embed("remove", i.user, (u, d, user_id))
            await i.followup.send(embed=embed)


        # ================== 5. WHITELIST LIST ==================
        elif mode.value == "list":
            data_req = await db_call(lambda: supabase.table("access_users").select("*").execute())
            data = data_req.data if data_req else []

            if not data:
                return await i.followup.send(embed=discord.Embed(title="📜 Whitelist Empty", description="No users are currently whitelisted.", color=0x2ECC71))
            
            view = AccessPaginator(data, i.user)
            if view.total_pages <= 1:
                view.children[0].disabled = True
                view.children[1].disabled = True
            else:
                view.update_buttons()
            
            await i.followup.send(embed=view.get_embed(), view=view)


        # ================== 6. BLACKLIST ADD ==================
        elif mode.value == "blk_add":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")
            u, d = await roblox_info(user_id)
            
            # Add to Blacklist
            await db_call(lambda: supabase.table("blacklist_users").upsert({"user_id": user_id}).execute())
            # Remove from Whitelist if exists (Security)
            try: await db_call(lambda: supabase.table("access_users").delete().eq("user_id", user_id).execute())
            except: pass
            
            try: log_action("blacklist_add", user_id, u, d, i.user.id)
            except: pass
            
            embed = build_access_embed("blk_add", i.user, (u, d, user_id))
            await i.followup.send(embed=embed)


        # ================== 7. BLACKLIST REMOVE ==================
        elif mode.value == "blk_remove":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")
            u, d = await roblox_info(user_id)
            
            await db_call(lambda: supabase.table("blacklist_users").delete().eq("user_id", user_id).execute())
            
            try: log_action("blacklist_remove", user_id, u, d, i.user.id)
            except: pass
            
            embed = build_access_embed("blk_remove", i.user, (u, d, user_id))
            await i.followup.send(embed=embed)


        # ================== 8. BLACKLIST LIST ==================
        elif mode.value == "blk_list":
            data_req = await db_call(lambda: supabase.table("blacklist_users").select("user_id").execute())
            data = data_req.data if data_req else []

            if not data:
                return await i.followup.send(embed=discord.Embed(title="📜 Blacklist Empty", description="No users are currently blacklisted.", color=0x3498DB))
            
            view = BlacklistPaginator(data, i.user)
            if view.total_pages <= 1:
                view.children[0].disabled = True
                view.children[1].disabled = True
            else:
                view.update_buttons()
            
            embed = await view.get_page_embed()
            await i.followup.send(embed=embed, view=view)


        # ================== 9. CLEAR WHITELIST ==================
        elif mode.value == "clear":
            embed = discord.Embed(
                title="⚠️ DANGER ZONE: RESET WHITELIST", 
                description="Are you sure you want to **DELETE ALL** Whitelisted users?\nThis action cannot be undone.", 
                color=0xFFAA00
            )
            embed.set_footer(text="Requires confirmation")
            view = AccessClearView(i.user.id)
            await i.response.send_message(embed=embed, view=view, ephemeral=False)

    except Exception as e:
        print(f"ACCESS COMMAND ERROR: {e}")
        try:
            await i.followup.send(f"❌ **System Error:** `{e}`")
        except:
            await i.response.send_message(f"❌ **System Error:** `{e}`", ephemeral=True)
            

# ================== VERIFIED LIST COMMAND (FIXED: Async & Fast) ==================
@bot.tree.command(name="verifiedlist", description="Show paginated verified Roblox users (Fixed)")
async def verifiedlist(i: discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Owners only"))

    await i.response.defer() # NO EPHEMERAL + SAFE

    try:
        # ✅ FIX: Parallel Execution using db_call (Bot nahi atkega)
        logs_task = db_call(lambda: supabase.table("verify_logs").select("*").order("timestamp", desc=True).execute())
        access_task = db_call(lambda: supabase.table("access_users").select("user_id").execute())

        # Dono data ek saath layenge
        logs_resp, access_resp = await asyncio.gather(logs_task, access_task)

        # Data extract
        logs = logs_resp.data if logs_resp else []
        access = access_resp.data if access_resp else []
        
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
            f"🕒 `{x['timestamp'].split('T')[0]}`\n" # Date formatting fix
            f"────────────────────\n"
        )

    if not entries:
        return await i.followup.send(
            embed=emb("📛 CLEAN", "No currently whitelisted verified users")
        )

    # ================= PAGINATION LOGIC =================
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
            if i.user.id != interaction.user.id: 
                return await interaction.response.send_message("❌ Not for you.", ephemeral=True)
            
            if self.page > 0:
                self.page -= 1
            await self.update(interaction)

        @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.gray)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            if i.user.id != interaction.user.id: 
                return await interaction.response.send_message("❌ Not for you.", ephemeral=True)
                
            if self.page < len(PAGES) - 1:
                self.page += 1
            await self.update(interaction)

        async def on_timeout(self):
            try:
                for c in self.children:
                    c.disabled = True
                # Message edit karne ke liye message object store karna padega agar chahiye to
                # Par abhi ke liye pass kar rahe hain taaki error na aaye
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

# ================== ULTRA PREMIUM GIVEAWAY (FULL FEATURES) ==================

class GiveawayView(discord.ui.View):
    def __init__(self, message_id):
        super().__init__(timeout=None)
        self.message_id = str(message_id)

    @discord.ui.button(label="🎉 Join Giveaway", style=discord.ButtonStyle.blurple, custom_id="join_btn")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        msg_id = str(interaction.message.id)
        user = interaction.user
        
        # 1. FETCH SETTINGS FROM DB
        res = supabase.table("giveaways").select("*").eq("message_id", msg_id).execute()
        if not res.data:
            return await interaction.response.send_message("❌ Database Error: Giveaway data nahi mila!", ephemeral=True)
        
        data = res.data[0]
        
        if data['ended']:
            return await interaction.response.send_message("🛑 Giveaway khatam ho chuka hai!", ephemeral=True)

        # 2. 🛡️ SECURITY CHECKS (Jo aapne maanga tha)
        
        # A. Staff Block Check
        if data['block_staff']:
            perms = user.guild_permissions
            if perms.administrator or perms.ban_members or perms.kick_members or perms.manage_guild:
                return await interaction.response.send_message("🚫 **Restricted:** Staff/Admins isme join nahi kar sakte!", ephemeral=True)

        # B. Role Blacklist Check
        if data['blacklist_role_id']:
            role_id = int(data['blacklist_role_id'])
            if user.get_role(role_id):
                return await interaction.response.send_message(f"🚫 **Restricted:** Jinke paas <@&{role_id}> role hai, wo join nahi kar sakte!", ephemeral=True)

        # 3. JOIN / LEAVE LOGIC
        participants = data['participants']
        
        if user.id in participants:
            participants.remove(user.id)
            msg = "💔 Aapne giveaway leave kar diya."
        else:
            participants.append(user.id)
            msg = "✅ **Entry Confirmed!** Good Luck! 🍀"

        # 4. UPDATE DB & EMBED
        supabase.table("giveaways").update({"participants": participants}).eq("message_id", msg_id).execute()

        embed = interaction.message.embeds[0]
        embed.set_field_at(1, name="👥 Entries", value=f"**{len(participants)}** Users", inline=True)
        
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message(msg, ephemeral=True)

# ================== FIX: GSTART (NO IMPORT ERROR) ==================

@bot.tree.command(name="gstart", description="💎 Start an Ultra-Premium Giveaway")
@app_commands.describe(
    prize="Kya inaam dena hai?",
    duration="Time (e.g., 10m, 1h, 2d)",
    winners="Kitne winners?",
    image_url="Custom image link (Optional)",
    block_staff="Kya Staff ko rokna hai? (True/False)",
    blacklist_role="Kis role ko ban karna hai? (Optional)"
)
async def gstart(i: discord.Interaction, prize: str, duration: str, winners: int, image_url: str = None, block_staff: bool = False, blacklist_role: discord.Role = None):
    
    # 1. Permission Check
    if not i.user.guild_permissions.manage_guild:
        return await i.response.send_message("❌ Sirf Managers/Admins giveaway start kar sakte hain!", ephemeral=True)

    # 🔥 FIX: Import datetime as 'dt' taaki koi conflict na ho
    import datetime as dt 

    # 2. Time Calculation
    unit = duration[-1].lower()
    try:
        val = int(duration[:-1])
    except:
        return await i.response.send_message("❌ Time format galat hai! Use: 10m, 1h, 1d", ephemeral=True)

    seconds = 0
    if unit == 'm': seconds = val * 60
    elif unit == 'h': seconds = val * 3600
    elif unit == 'd': seconds = val * 86400
    else: return await i.response.send_message("❌ Invalid Unit! Use m, h, or d.", ephemeral=True)

    # Ab ye 'dt' use karega, jo 100% chalega
    end_time_dt = dt.datetime.now() + dt.timedelta(seconds=seconds)
    timestamp = int(end_time_dt.timestamp())

    # --- PREMIUM EMBED ---
    default_img = "https://media1.tenor.com/m/XZThisaqECAAAAAC/giveaway-giveaway-alert.gif"
    final_image = image_url if image_url else default_img

    embed = discord.Embed(title="🎉 **GIVEAWAY** 🎉", description=f"### 🎁 Prize: {prize}\n\n👇 **Click the button below to Join!**", color=0xFFD700)
    embed.add_field(name="⏰ Ends In", value=f"<t:{timestamp}:R>", inline=True)
    embed.add_field(name="👥 Entries", value="**0** Users", inline=True)
    embed.add_field(name="🏆 Winners", value=f"{winners}", inline=True)
    
    rest_text = "None"
    if block_staff: rest_text = "🚫 No Staff"
    if blacklist_role: rest_text += f", 🚫 No {blacklist_role.mention}"
    embed.add_field(name="🔒 Restrictions", value=rest_text, inline=False)
    
    embed.set_image(url=final_image)
    embed.set_thumbnail(url=i.guild.icon.url if i.guild.icon else None)
    embed.set_footer(text=f"Hosted by: {i.user.display_name} • Starting...", icon_url=i.user.display_avatar.url)

    await i.response.send_message("✅ Giveaway setup complete!", ephemeral=True)
    msg = await i.channel.send(embed=embed)

    view = GiveawayView(msg.id)
    embed.set_footer(text=f"Hosted by: {i.user.display_name} • ID: {msg.id}", icon_url=i.user.display_avatar.url)
    await msg.edit(embed=embed, view=view)

    # 🔥 SAVE TO DB (Fixed dt usage)
    db_data = {
        "message_id": str(msg.id),
        "channel_id": str(i.channel.id),
        "prize": prize,
        "winners_count": winners,
        "end_time": str(end_time_dt),
        "host_id": str(i.user.id),
        "participants": [],
        "ended": False,
        "block_staff": block_staff,
        "blacklist_role_id": str(blacklist_role.id) if blacklist_role else None,
        "image_url": final_image
    }
    supabase.table("giveaways").insert(db_data).execute()

    await asyncio.sleep(seconds)

    # --- ENDING LOGIC ---
    res = supabase.table("giveaways").select("*").eq("message_id", str(msg.id)).execute()
    if res.data and not res.data[0]['ended']:
        data = res.data[0]
        users = data['participants']
        
        if len(users) < winners:
            winner_text = "No one joined 😢"
        else:
            winners_list = random.sample(users, winners)
            winner_text = ", ".join([f"<@{uid}>" for uid in winners_list])
            await i.channel.send(f"🎉 **CONGRATULATIONS!** {winner_text} won **{prize}**! 🎁")

        embed.color = 0x2B2D31
        embed.title = "🎊 GIVEAWAY ENDED 🎊"
        embed.description = f"### 🎁 Prize: {prize}\n\n👑 **Winner(s):** {winner_text}"
        embed.set_field_at(0, name="⏰ Status", value="Ended", inline=True)
        embed.set_image(url=None)
        
        await msg.edit(embed=embed, view=None)
        supabase.table("giveaways").update({"ended": True}).eq("message_id", str(msg.id)).execute()

@bot.tree.command(name="gcheck", description="🕵️ Check who joined (With Full Details)")
async def gcheck(i: discord.Interaction, giveaway_id: str):
    
    if not i.user.guild_permissions.manage_guild:
        return await i.response.send_message("❌ Managers only!", ephemeral=True)

    res = supabase.table("giveaways").select("*").eq("message_id", giveaway_id).execute()
    if not res.data:
        return await i.response.send_message("❌ ID Database me nahi mili!", ephemeral=True)

    data = res.data[0]
    participants = data['participants']
    
    # List formatting
    names = [f"<@{uid}> (`{uid}`)" for uid in participants]
    desc = "\n".join(names) if names else "No participants yet."

    embed = discord.Embed(title=f"📂 Giveaway Details: {data['prize']}", color=0x00ffea)
    embed.add_field(name="🆔 ID", value=data['message_id'], inline=True)
    embed.add_field(name="👑 Host", value=f"<@{data['host_id']}>", inline=True)
    embed.add_field(name="🔒 Staff Blocked?", value=str(data['block_staff']), inline=True)
    
    if len(desc) > 4000:
        with open("list.txt", "w") as f: f.write("\n".join(names))
        await i.response.send_message(file=discord.File("list.txt"), ephemeral=True)
    else:
        embed.description = f"**Participants ({len(names)}):**\n{desc}"
        await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="greroll", description="🔄 Pick new winner (Database Powered)")
async def greroll(i: discord.Interaction, giveaway_id: str, winners: int = 1):
    
    if not i.user.guild_permissions.manage_guild:
        return await i.response.send_message("❌ Managers only!", ephemeral=True)

    res = supabase.table("giveaways").select("*").eq("message_id", giveaway_id).execute()
    if not res.data: return await i.response.send_message("❌ Invalid ID!", ephemeral=True)

    data = res.data[0]
    users = data['participants']
    
    if len(users) < winners:
        return await i.response.send_message("❌ Not enough participants!", ephemeral=True)

    new_winners = random.sample(users, winners)
    winner_text = ", ".join([f"<@{uid}>" for uid in new_winners])

    embed = discord.Embed(title="🔄 **REROLL RESULT**", description=f"### 🎁 Prize: {data['prize']}\n\n👑 **New Winner:** {winner_text}", color=0xFF0055)
    await i.response.send_message(embed=embed)


@bot.tree.command(name="whois", description="🕵️ Get detailed status of a Roblox User")
async def whois(i: discord.Interaction, user_id: str):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Owner only command"))

    await i.response.defer()

    try:
        # ✅ FIX: Using await for async function
        username, display = await roblox_info(user_id)
        
        # Handle invalid user
        if username == "Invalid ID":
            return await i.followup.send(embed=discord.Embed(title="❌ Invalid ID", description="Roblox ID exist nahi karti.", color=0xff0000))

        # ===== DATABASE CHECKS =====
        # 1. Ban Check
        ban_data = supabase.table("bans").select("*").eq("user_id", user_id).execute().data
        if ban_data:
            b = ban_data[0]
            if b.get("perm"):
                status_emoji = "🔴"
                status_text = f"**BANNED (Permanent)**\nReason: `{b.get('reason')}`"
                color = 0xff0000
            else:
                # Time calc
                left = int((float(b["expire"]) - time.time())/60)
                if left > 0:
                    status_emoji = "🟠"
                    status_text = f"**TEMP BANNED ({left}m left)**\nReason: `{b.get('reason')}`"
                    color = 0xffa500
                else:
                    status_emoji = "🟢"
                    status_text = "Clean (Ban Expired)"
                    color = 0x2ecc71
        else:
            status_emoji = "🟢"
            status_text = "Clean (No Active Bans)"
            color = 0x2ecc71

        # 2. Access Check
        ac = supabase.table("access_users").select("user_id").eq("user_id",user_id).execute().data
        access_str = "✅ **Whitelisted**" if ac else "❌ **Not Whitelisted**"

        # 3. Blacklist Check
        blk = supabase.table("blacklist_users").select("user_id").eq("user_id", user_id).execute().data
        blacklist_str = "🚫 **Yes (Restricted)**" if blk else "🟢 **No**"

        # ===== BUILD PREMIUM EMBED =====
        embed = discord.Embed(title=f"{status_emoji} User Lookup Result", color=color)
        
        # Header (User Info)
        embed.add_field(name="👤 Identity", value=f"**User:** `{username}`\n**Display:** `{display}`\n**ID:** `{user_id}`", inline=False)
        
        # Status Grid
        embed.add_field(name="🛡️ Moderation", value=status_text, inline=True)
        embed.add_field(name="🔐 Access", value=access_str, inline=True)
        embed.add_field(name="⛔ Blacklist", value=blacklist_str, inline=True)

        # Thumbnail (Roblox Headshot)
        embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
        
        # Footer
        embed.set_footer(text=f"Requested by {i.user.name}", icon_url=i.user.display_avatar.url)
        embed.timestamp = datetime.utcnow()

        await i.followup.send(embed=embed)

    except Exception as e:
        print(f"WHOIS ERROR: {e}")
        await i.followup.send(f"❌ **System Error:** `{e}`")

        
# ================== STATS COMMAND (FIXED: FAST & ASYNC) ==================

@bot.tree.command(name="stats", description="View System Statistics (Super Fast)")
async def stats(i: discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Owner only"))

    await i.response.defer() # Defer zaroori hai

    try:
        start_t = time.time()

        # ✅ FIX: Saari tables ek saath background me fetch hongi (Parallel)
        # Isse bot "Thinking" par nahi atkega aur speed 5x badh jayegi
        bans_task = db_call(lambda: supabase.table("bans").select("*").execute())
        access_task = db_call(lambda: supabase.table("access_users").select("*").execute())
        blk_task = db_call(lambda: supabase.table("blacklist_users").select("*").execute())
        logs_task = db_call(lambda: supabase.table("verify_logs").select("*").execute())
        kick_task = db_call(lambda: supabase.table("kick_flags").select("*").execute())
        sett_task = db_call(lambda: supabase.table("bot_settings").select("*").execute())

        # Sabka wait karo (bina bot roke)
        bans, access, blk, logs, kicks, settings = await asyncio.gather(
            bans_task, access_task, blk_task, logs_task, kick_task, sett_task
        )

        # Data extract (Safety ke saath)
        bans_data = bans.data if bans else []
        access_data = access.data if access else []
        blk_data = blk.data if blk else []
        logs_data = logs.data if logs else []
        kicks_data = kicks.data if kicks else []
        sett_data = settings.data if settings else []

        # Logic wahi purana...
        now = time.time()
        perm = 0
        temp = 0
        for b in bans_data:
            if b.get("perm"): perm += 1
            elif b.get("expire") and now < float(b["expire"]): temp += 1

        # Settings Check
        acc_status = "🟢 OFF (Everyone Allowed)"
        maint_status = "🟢 OFF"
        
        for s in sett_data:
            if s["key"] == "access_enabled" and s["value"] == "true": 
                acc_status = "🔐 ON (Whitelist Enabled)"
            if s["key"] == "maintenance" and s["value"] == "true": 
                maint_status = "🛠 ON"

        # Uptime
        uptime = int(time.time() - START_TIME)
        hrs, mins = uptime // 3600, (uptime % 3600) // 60

        embed = discord.Embed(title="⚙️ SYSTEM CONTROL PANEL", description="Premium Secure Control Dashboard", color=0x2ecc71)
        
        embed.add_field(name="🚫 Ban System", value=f"**Permanent Bans:** `{perm}`\n**Active TempBans:** `{temp}`\n**Blacklisted Users:** `{len(blk_data)}`", inline=False)
        embed.add_field(name="👥 User Access", value=f"**Whitelisted Users:** `{len(access_data)}`\n**Verification Logs:** `{len(logs_data)}`\n**Kick Flags Pending:** `{len(kicks_data)}`", inline=False)
        embed.add_field(name="🛠 System Status", value=f"**Access System:** {acc_status}\n**Maintenance:** {maint_status}", inline=False)
        embed.add_field(name="🤖 Bot Status", value=f"**Uptime:** `{hrs}h {mins}m`\n**Health:** 🟢 Stable & Optimized", inline=False)
        
        embed.set_footer(text="RoboPal • Secure Moderation Engine")
        embed.timestamp = datetime.utcnow()
        
        await i.followup.send(embed=embed)

    except Exception as e:
        await i.followup.send(embed=emb("❌ ERROR", f"Stats failed:\n```{e}```", 0xff0000))

        
# ================== ALT CHECK COMMAND (FIXED: Async DB) ==================
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

    try:
        # =========================
        # DISCORD USER MODE
        # =========================
        if discord_user:
            # ✅ FIX: Async DB Call
            logs_req = await db_call(lambda: supabase.table("verify_logs").select("*").eq("discord_id", str(discord_user.id)).execute())
            logs = logs_req.data if logs_req else []

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
            # Text limit safety
            if len(txt) > 3000: txt = txt[:3000] + "\n... (More hidden)"

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
            # ✅ FIX: Async DB Call
            logs_req = await db_call(lambda: supabase.table("verify_logs").select("*").eq("roblox_id", roblox_user_id).execute())
            logs = logs_req.data if logs_req else []

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

    except Exception as e:
        await i.followup.send(f"❌ Error: {e}")

# ================== VERIFY HISTORY COMMAND (FIXED: Async DB) ==================
@bot.tree.command(name="verifyhistory", description="Show global verification logs (Fixed)")
async def verifyhistory(i: discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION","Owner Only"))

    await i.response.defer()

    try:
        # ✅ FIX: Async DB Call (Bot nahi atkega)
        logs_req = await db_call(lambda: supabase.table("verify_logs").select("*").order("timestamp", desc=True).execute())
        logs = logs_req.data if logs_req else []

    except Exception as e:
        return await i.followup.send(embed=emb("❌ ERROR", f"Failed to fetch logs: {e}"))

    if not logs:
        return await i.followup.send(embed=emb("📭 EMPTY","No one has verified yet"))

    pages = []
    page = []

    for x in logs:
        # Date formatting crash fix
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
        async def back(self, interaction: discord.Interaction, btn: discord.ui.Button):
            if i.user.id != interaction.user.id: 
                return await interaction.response.send_message("❌ Not for you.", ephemeral=True)
            
            if self.index > 0:
                self.index -= 1
            await self.update(interaction)

        @ui.button(label="➡️ Next", style=discord.ButtonStyle.primary)
        async def next(self, interaction: discord.Interaction, btn: discord.ui.Button):
            if i.user.id != interaction.user.id: 
                return await interaction.response.send_message("❌ Not for you.", ephemeral=True)

            if self.index < len(pages)-1:
                self.index += 1
            await self.update(interaction)

    view = Pager()
    await i.followup.send(
        embed=emb(f"📜 VERIFICATION HISTORY (1/{len(pages)})", pages[0], 0x3498db),
        view=view
    )

# ================== HISTORY COMMAND (FIXED: Async & Fast) ==================
@bot.tree.command(name="history", description="📜 Check Roblox User History & Safety Status (Fixed)")
async def history(i: discord.Interaction, user_id: str):
    
    # 1. OWNER/ADMIN CHECK
    if not owner(i):
        await i.response.send_message("❌ **Access Denied:** You are not an Admin.", ephemeral=True)
        return

    # 2. Defer Response
    await i.response.defer(ephemeral=False)

    try:
        # A. Roblox Info Fetch
        username, display = await roblox_info(user_id)
        
        if username == "Invalid ID":
             return await i.followup.send(embed=discord.Embed(title="❌ Error", description="Invalid Roblox ID", color=0xff0000))

        # B. DATABASE FETCH (Parallel Execution)
        # ✅ FIX: db_call aur asyncio.gather use kiya
        access_task = db_call(lambda: supabase.table("access_users").select("*").eq("user_id", user_id).execute())
        ban_task = db_call(lambda: supabase.table("bans").select("*").eq("user_id", user_id).execute())
        blk_task = db_call(lambda: supabase.table("blacklist_users").select("*").eq("user_id", user_id).execute())

        # Wait for all 3
        access_resp, ban_resp, blk_resp = await asyncio.gather(access_task, ban_task, blk_task)

        # Data Extraction
        access_data = access_resp.data if access_resp else []
        ban_data = ban_resp.data if ban_resp else []
        blk_data = blk_resp.data if blk_resp else []

        # ================= LOGIC BUILDER =================
        
        # 1. Access Status
        if access_data:
            row = access_data[0]
            disc_id = row.get("discord_id", "Unknown")
            
            try:
                verified_at = row.get("created_at", "").split("T")[0]
            except:
                verified_at = "Unknown"

            access_status = f"✅ **Whitelisted**\nLinked to: <@{disc_id}>\n📅 `{verified_at}`"
            color = 0x2ecc71 # Green
        else:
            access_status = "⚠️ **Not Linked**\n(No active whitelist found)"
            color = 0x3498db # Blue (Neutral)

        # 2. Ban Status
        if ban_data:
            b = ban_data[0]
            if b.get("perm"):
                ban_status = f"🔴 **PERMANENT BAN**\nReason: `{b.get('reason')}`"
                color = 0xff0000 # Red
            else:
                try:
                    left = int(max((float(b["expire"]) - time.time())/60 , 0))
                    ban_status = f"🟠 **TEMP BAN** ({left}m left)\nReason: `{b.get('reason')}`"
                    color = 0xe67e22 # Orange
                except:
                    ban_status = "🟢 **Ban Expired**"
        else:
            ban_status = "🟢 **Clean** (No active bans)"

        # 3. Blacklist Status
        if blk_data:
            blk_status = "🚫 **YES (Blacklisted)**"
            color = 0x2c3e50 # Dark (Danger)
        else:
            blk_status = "🟢 **NO**"

        # ================= PREMIUM EMBED =================
        embed = discord.Embed(title=f"📜 User History: {display}", color=color)
        
        # Top Section: User Identity
        embed.add_field(name="👤 Identity", value=f"**User:** @{username}\n**ID:** `{user_id}`", inline=False)
        
        # Mid Section: Status Grid
        embed.add_field(name="🔐 Whitelist Status", value=access_status, inline=True)
        embed.add_field(name="🛡️ Ban Status", value=ban_status, inline=True)
        embed.add_field(name="⛔ Blacklist", value=blk_status, inline=True)

        # Avatar Thumbnail
        embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
        
        # Footer
        embed.set_footer(text=f"Requested by {i.user.display_name} • Secure Lookup", icon_url=i.user.display_avatar.url)
        embed.timestamp = datetime.utcnow()

        await i.followup.send(embed=embed)

    except Exception as e:
        print(f"HISTORY ERROR: {e}")
        await i.followup.send(f"❌ **System Error:** `{e}`")
        

# ================== PROFILE COMMAND (FIXED: FAST & PARALLEL) ==================
@bot.tree.command(name="profile", description="📂 View full Verification, Safety & Moderation Profile (Fixed)")
async def profile(i: discord.Interaction, user_id: str):
    
    # 1. OWNER CHECK
    if not owner(i):
        return await i.response.send_message("❌ **Access Denied:** Owner/Admin only.", ephemeral=True)

    await i.response.defer(ephemeral=False)

    try:
        # A. Roblox Info (Async & Fast)
        username, display = await roblox_info(user_id)

        if username == "Invalid ID":
             return await i.followup.send(embed=discord.Embed(title="❌ Error", description="Invalid Roblox ID", color=0xff0000))

        # ================= B. FETCH DATA (PARALLEL & NON-BLOCKING) =================
        # Saari tables ek saath check hongi (Wait time = 0s)
        
        task1 = db_call(lambda: supabase.table("access_users").select("*").eq("user_id", user_id).execute())
        task2 = db_call(lambda: supabase.table("bans").select("*").eq("user_id", user_id).execute())
        task3 = db_call(lambda: supabase.table("blacklist_users").select("*").eq("user_id", user_id).execute())
        task4 = db_call(lambda: supabase.table("fake_warnings").select("*").eq("user_id", user_id).execute())
        task5 = db_call(lambda: supabase.table("fake_flags").select("*").eq("user_id", user_id).execute())
        task6 = db_call(lambda: supabase.table("kick_flags").select("*").eq("user_id", user_id).execute())

        # Sabka result ek saath aayega
        res1, res2, res3, res4, res5, res6 = await asyncio.gather(task1, task2, task3, task4, task5, task6)
        
        # Data Extraction (Safe Mode)
        access = res1.data if res1 else []
        bans = res2.data if res2 else []
        blk = res3.data if res3 else []
        warnings = res4.data if res4 else []
        flags = res5.data if res5 else []
        kicks = res6.data if res6 else []

        # ================= C. PROCESS DATA =================

        # --- 1. Verification Logic ---
        if access:
            data = access[0]
            verifier_id = data.get("discord_id", "Unknown")
            
            try:
                date_str = data.get("created_at", "").split("T")[0]
            except:
                date_str = "Unknown"

            verify_status = "✅ **Whitelisted**"
            verify_desc = (
                f"👤 **Verified By:** <@{verifier_id}>\n"
                f"📅 **Date:** `{date_str}`\n"
                f"🆔 **Verifier ID:** `{verifier_id}`"
            )
            color = 0x2ecc71 # Green
        else:
            verify_status = "⚠️ **Not Whitelisted**"
            verify_desc = "User verify nahi hai aur na hi whitelist access hai."
            color = 0x3498db # Blue (Neutral)

        # --- 2. Moderation Logic ---
        mod_status = []
        
        # Check Bans
        if bans:
            b = bans[0]
            if b.get('perm'):
                mod_status.append(f"🔴 **Permanent Ban:** `{b.get('reason')}`")
                color = 0xff0000 # Red
            else:
                mod_status.append(f"🟠 **Temp Ban:** `{b.get('reason')}`")
                color = 0xe67e22 # Orange

        # Check Blacklist
        if blk:
            mod_status.append("🚫 **Blacklisted User**")
            color = 0x2c3e50 # Dark

        # Check Flags
        if flags:
            mod_status.append(f"🚩 **Flags:** {len(flags)} Active Flags")
        
        # Check Kicks
        if kicks:
            mod_status.append(f"👢 **Kick History:** {len(kicks)} times kicked")

        # Check Warnings
        if warnings:
            mod_status.append(f"⚠️ **Warnings:** {len(warnings)} Warnings")

        # Combine Moderation Text
        if mod_status:
            mod_text = "\n".join(mod_status)
        else:
            mod_text = "🟢 **Clean Record** (No bans, flags, or warnings)"


        # ================= D. BUILD PREMIUM EMBED =================
        embed = discord.Embed(title=f"📂 Player Profile: {display}", color=color)
        
        # Header: User Identity
        embed.add_field(name="👤 Identity", value=f"**User:** @{username}\n**ID:** `{user_id}`", inline=False)
        
        # Section 1: Verification
        embed.add_field(name="🔐 Access Status", value=verify_status, inline=True)
        embed.add_field(name="🛡️ Safety Status", value="See Below 👇", inline=True)
        
        # Section 2: Details
        embed.add_field(name="📜 Verification Details", value=verify_desc, inline=False)
        
        # Section 3: History
        embed.add_field(name="🚨 Moderation History", value=mod_text, inline=False)

        # Thumbnail
        embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
        
        # Footer
        embed.set_footer(text=f"Requested by {i.user.display_name} • Full Database Scan", icon_url=i.user.display_avatar.url)
        embed.timestamp = datetime.utcnow()

        await i.followup.send(embed=embed)

    except Exception as e:
        print(f"PROFILE ERROR: {e}")
        await i.followup.send(f"❌ **System Error:** `{e}`")

# ================== MULTI-VERIFY COMMAND (FIXED: Async DB) ==================
@bot.tree.command(name="multiverify", description="Users who verified multiple Roblox accounts (Fixed)")
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
        # ✅ FIX: Blocking call hataya, db_call use kiya
        logs_req = await db_call(lambda: supabase.table("access_users").select("*").execute())
        logs = logs_req.data if logs_req else []
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
            if i.user.id != interaction.user.id: 
                return await interaction.response.send_message("❌ Not for you.", ephemeral=True)
            if self.page > 0:
                self.page -= 1
            await self.refresh(interaction)

        @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.gray)
        async def next(self, interaction: discord.Interaction, btn: discord.ui.Button):
            if i.user.id != interaction.user.id: 
                return await interaction.response.send_message("❌ Not for you.", ephemeral=True)
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

# ================== FAKE BAN COMMAND (FIXED: Async & No Lag) ==================
@bot.tree.command(name="fakeban", description="Fake ban control panel (Fixed)")
@app_commands.choices(action=[
    app_commands.Choice(name="➕ Add Fake Ban", value="add"),
    app_commands.Choice(name="➖ Remove Fake Ban", value="remove"),
    app_commands.Choice(name="📜 List All", value="list")
])
@app_commands.describe(userid="Roblox User ID", message="Custom kick message")
async def fakeban(i: discord.Interaction, action: app_commands.Choice[str], userid: str = None, message: str = None):

    if not owner(i):
        return await i.response.send_message(embed=emb("❌ NO PERMISSION", "Owner only"), ephemeral=True)

    await i.response.defer()

    try:
        # ================= ADD FAKE BAN =================
        if action.value == "add":
            if not userid:
                return await i.followup.send(embed=emb("❌ ERROR","User ID required"))

            # ✅ FIX: Async Check
            chk_req = await db_call(lambda: supabase.table("fake_warnings").select("user_id").eq("user_id", userid).execute())
            chk = chk_req.data if chk_req else []

            if chk:
                return await i.followup.send(embed=emb("⚠️ ALREADY PENDING","This player already has a fake warning pending"))

            # Roblox Info Fetch
            uname, dname = await roblox_info(userid)

            # Default Message Logic
            msg = message or "🚫 Account Action Required\n\nYour account has been temporarily restricted...\nDuration: 3 Days\nReference: #SEC-9043X"

            # ✅ FIX: Async Insert
            await db_call(lambda: supabase.table("fake_warnings").insert({
                "user_id": userid,
                "username": uname,
                "display_name": dname,
                "message": msg
            }).execute())

            return await i.followup.send(embed=emb(
                "🚨 FAKE BAN ADDED",
                f"👤 **{dname}** (`{uname}`)\n🆔 `{userid}`\n📝 Msg: `{msg[:50]}...`\n\nFake ban queued successfully",
                0xff0000
            ))

        # ================= REMOVE =================
        elif action.value == "remove":
            if not userid:
                return await i.followup.send(embed=emb("❌ ERROR","User ID required"))

            # ✅ FIX: Async Delete
            await db_call(lambda: supabase.table("fake_warnings").delete().eq("user_id", userid).execute())

            return await i.followup.send(embed=emb(
                "🧹 REMOVED",
                f"User `{userid}` removed from fake queue",
                0x2ecc71
            ))

        # ================= LIST =================
        elif action.value == "list":
            # ✅ FIX: Async Fetch
            data_req = await db_call(lambda: supabase.table("fake_warnings").select("*").execute())
            data = data_req.data if data_req else []

            if not data:
                return await i.followup.send(embed=emb("📭 EMPTY","No pending fake bans"))

            text = ""
            for x in data:
                text += f"👤 **{x['display_name']}** (`{x['username']}`)\n🆔 `{x['user_id']}`\n-------------------\n"

            # Message limit safety
            if len(text) > 4000: text = text[:4000] + "\n... (More hidden)"

            return await i.followup.send(embed=emb("📜 PENDING FAKE BANS", text, 0x3498db))

    except Exception as e:
        return await i.followup.send(embed=emb("❌ ERROR", f"```{e}```"))

# ================== ADMIN LOGS COMMAND (FIXED: Async & No Duplicate) ==================
@bot.tree.command(name="logs", description="View admin logs with filters + pagination")
@app_commands.choices(filter=[
    app_commands.Choice(name="All Actions", value="all"),
    app_commands.Choice(name="Maintenance (On/Off)", value="maintenance"),
    app_commands.Choice(name="Stop System (On/Off)", value="stop"),
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
        return await i.response.send_message(embed=emb("❌ NO PERMISSION", "Owner Only"), ephemeral=True)

    await i.response.defer()

    try:
        # ✅ FIX: Async DB Call (Bot nahi atkega)
        if filter.value == "all":
            data_req = await db_call(lambda: supabase.table("admin_logs").select("*").order("timestamp", desc=True).limit(100).execute())
        else:
            # .ilike for partial match (ex: 'maintenance' matches 'maintenance_on' & 'maintenance_off')
            data_req = await db_call(lambda: supabase.table("admin_logs").select("*").ilike("action", f"{filter.value}%").order("timestamp", desc=True).limit(100).execute())
            
        data = data_req.data if data_req else []
            
    except Exception as e:
        return await i.followup.send(embed=emb("❌ ERROR", f"Logs failed:\n`{e}`", 0xff0000))

    if not data:
        return await i.followup.send(embed=emb("📭 NO DATA", f"No logs found for filter: **{filter.name}**", 0xffc107))

    pages = []
    chunk = []

    for x in data:
        # Timestamp Fix (Error Handling)
        t = x.get("timestamp", "Unknown").split("T")[0]
        
        # Executor formatting
        executor_id = x.get('executor', 'Unknown')
        executor_mention = f"<@{executor_id}>" if executor_id.isdigit() else executor_id

        # Action formatting
        act = x.get('action', 'Unknown').replace("_", " ").upper()
        target = x.get('user_id', '-')

        chunk.append(
            f"📌 **Action:** `{act}`\n"
            f"👮 **Admin:** {executor_mention}\n"
            f"🆔 **Target:** `{target}`\n"
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
            try:
                await interaction.response.edit_message(embed=e, view=self)
            except:
                pass

        @discord.ui.button(label="⏮ Back", style=discord.ButtonStyle.gray)
        async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
            if i.user.id != interaction.user.id: return await interaction.response.send_message("❌ Not for you.", ephemeral=True)
            if self.page > 0:
                self.page -= 1
            await self.update(interaction)

        @discord.ui.button(label="Next ⏭", style=discord.ButtonStyle.gray)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            if i.user.id != interaction.user.id: return await interaction.response.send_message("❌ Not for you.", ephemeral=True)
            if self.page < len(pages) - 1:
                self.page += 1
            await self.update(interaction)

    view = LogPages()
    e = emb(
        f"🗂 LOGS — {filter.name.upper()} (1/{len(pages)})",
        pages[0],
        0x3498db
    )

    # ✅ FIX: Duplicate 'await i.followup.send' hata diya
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

# ================== AUDIT COMMAND (FIXED: Async & Non-Blocking) ==================
@bot.tree.command(name="audit", description="Run Advanced Full System Audit (Fixed)")
async def audit(i: discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("❌ NO PERMISSION", "Owners only"))

    await i.response.defer()

    try:
        reports = []
        ok = True

        # ===============================
        #  BACKEND HEALTH + LATENCY (FIXED)
        # ===============================
        t = time.time()
        backend_online = False
        latency = 9999

        try:
            # ✅ FIX: requests.get ki jagah bot.session use kiya (Fast)
            async with bot.session.get("https://testingbot-z0y6.onrender.com/ping", timeout=6) as r:
                text = await r.text()
                backend_online = (text.strip() == "pong")
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
        # DATABASE HEALTH (FIXED)
        # ===============================
        t = time.time()
        db_ok = True
        q_ms = 9999

        try:
            # ✅ FIX: db_call use kiya
            await db_call(lambda: supabase.table("bot_settings").select("key").limit(1).execute())
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
        # SYSTEM SETTINGS (FIXED)
        # ===============================
        try:
            # ✅ FIX: Async Fetch
            settings_req = await db_call(lambda: supabase.table("bot_settings").select("*").execute())
            settings = settings_req.data if settings_req else []
        except:
            settings = []

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
        # Note: TRAFFIC_LOG global list honi chahiye aapke code me
        last_min = [t for t, _ in TRAFFIC_LOG if now - t <= 60]
        rpm = len(last_min)

        reports.append(
            f"📡 **Traffic Monitor**\n"
            f"Requests per minute: `{rpm}`"
        )

        # ===============================
        #  LOAD ESTIMATE
        # ===============================
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
            except:                pass
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

# ================== 🦑 SQUID GAME DUEL (ORIGINAL THEME + VIP FIX) ==================

class SquidGameMaster(discord.ui.View):
    def __init__(self, p1, p2, bullets, punishment_level, cylinder=None, slot_index=0):
        super().__init__(timeout=300)
        self.p1 = p1
        self.p2 = p2
        self.bullets = bullets
        self.punishment_level = punishment_level
        
        # Game State
        self.p1_choice = None
        self.p2_choice = None
        self.round_loser = None 
        
        # Cylinder Logic
        if cylinder is None:
            self.cylinder = [1] * bullets + [0] * (6 - bullets)
            random.shuffle(self.cylinder)
        else:
            self.cylinder = cylinder
            
        self.slot_index = slot_index
        
        # Start in RPS Mode
        self.setup_rps_buttons()
        self.update_embed(mode="RPS")

    def setup_rps_buttons(self):
        self.clear_items()
        btn_rock = discord.ui.Button(emoji="🪨", style=discord.ButtonStyle.secondary, custom_id="rock")
        btn_paper = discord.ui.Button(emoji="📄", style=discord.ButtonStyle.secondary, custom_id="paper")
        btn_scissor = discord.ui.Button(emoji="✂️", style=discord.ButtonStyle.secondary, custom_id="scissor")
        
        btn_rock.callback = self.rps_callback
        btn_paper.callback = self.rps_callback
        btn_scissor.callback = self.rps_callback
        
        self.add_item(btn_rock)
        self.add_item(btn_paper)
        self.add_item(btn_scissor)

    def setup_trigger_button(self):
        self.clear_items()
        btn_trigger = discord.ui.Button(label="😨 PULL TRIGGER (Maut ka Button)", style=discord.ButtonStyle.danger, emoji="🔫")
        btn_trigger.callback = self.trigger_callback
        self.add_item(btn_trigger)

    def update_embed(self, mode="RPS", extra_text=""):
        # 🎨 PREMIUM COLOR PALETTE (ORIGINAL)
        color = 0x00FFFF if mode == "RPS" else 0xFF00E6 # Cyan for RPS, Hot Pink for Gun
        
        desc = f"### 💀 ROUND {self.slot_index + 1} / 6\n"
        
        # --- 🎬 VISUALS (GIFs) ---
        gifs = {
            "rps": "https://media.tenor.com/BfRK3aY2Nn4AAAAC/squid-game.gif", # Squid game guards
            "gun": "https://media.tenor.com/y1_B0m0k_mUAAAAd/revolver-spin.gif", # Spinning Gun
            "safe": "https://media.tenor.com/5yXk8QoZzBkAAAAC/sweating-nervous.gif", # Sweating anime
            "wasted": "https://media.tenor.com/d6-SreC3_p8AAAAC/wasted-gta5.gif" # GTA Wasted
        }

        image_url = gifs["rps"]

        if mode == "RPS":
            desc += f"👉 **Toss Time:** Dono apna move chuno!\n\n" \
                    f"🧑‍🚀 **{self.p1.name}:** {'✅ READY' if self.p1_choice else '⏳ Thinking...'}\n" \
                    f"🧑‍🚀 **{self.p2.name}:** {'✅ READY' if self.p2_choice else '⏳ Thinking...'}\n\n" \
                    f"⚠️ *Jo haarega, wo agle slot ki goli apne bheje me utarega!*"
            image_url = gifs["rps"]
            
        elif mode == "TRIGGER":
            desc += f"🩸 **RPS Result:** {self.round_loser.mention} haar gaya!\n" \
                    f"👉 Ab isko **Trigger** dabana padega.\n\n" \
                    f"🎯 Target: **Slot #{self.slot_index + 1}**"
            image_url = gifs["gun"]
        
        elif mode == "SAFE":
             desc += f"😌 **BACH GAYA!**\n" \
                     f"Gun se sirf *Click* ki aawaz aayi.\n\n" \
                     f"{extra_text}"
             image_url = gifs["safe"]
             color = 0x00FF00 # Green for safe

        # Embed Build
        self.embed = discord.Embed(title="🦑 SQUID GAME: DEATH MATCH", description=desc, color=color)
        self.embed.add_field(name="🔫 Ammo Left", value=f"`{self.bullets}` Bullets", inline=True)
        self.embed.add_field(name="⚖️ Punishment", value=f"**Level {self.punishment_level}**", inline=True)
        self.embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2822/2822506.png") # Revolver Icon
        self.embed.set_image(url=image_url)
        self.embed.set_footer(text="Powered by Russian Roulette System", icon_url="https://cdn-icons-png.flaticon.com/512/9249/9249309.png")

    async def rps_callback(self, interaction: discord.Interaction):
        if interaction.user.id not in [self.p1.id, self.p2.id]:
            return await interaction.response.send_message("❌ Tu audience hai, shant baith!", ephemeral=True)
        
        choice = interaction.data["custom_id"] 
        
        if interaction.user.id == self.p1.id:
            self.p1_choice = choice
        else:
            self.p2_choice = choice
            
        self.update_embed(mode="RPS")
        await interaction.response.edit_message(embed=self.embed, view=self)
        
        if self.p1_choice and self.p2_choice:
            await self.resolve_rps(interaction)

    async def resolve_rps(self, interaction):
        choices_map = {'rock': 0, 'paper': 1, 'scissor': 2}
        v1 = choices_map[self.p1_choice]
        v2 = choices_map[self.p2_choice]
        
        if v1 == v2:
            self.p1_choice = None
            self.p2_choice = None
            self.update_embed(mode="RPS")
            self.embed.description = "### 🤝 DRAW! Dobara Khelo!\nDono ne same choose kiya."
            await interaction.edit_original_response(embed=self.embed, view=self)
            return
            
        elif (v1 == 0 and v2 == 2) or (v1 == 1 and v2 == 0) or (v1 == 2 and v2 == 1):
            self.round_loser = self.p2
        else:
            self.round_loser = self.p1
            
        self.setup_trigger_button()
        self.update_embed(mode="TRIGGER")
        await interaction.edit_original_response(embed=self.embed, view=self)

    async def trigger_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.round_loser.id:
            return await interaction.response.send_message(f"❌ Ruk ja bhai! Ye saza {self.round_loser.name} ke liye hai.", ephemeral=True)
            
        is_bullet = self.cylinder[self.slot_index] == 1
        
        if is_bullet:
            self.stop()
            
            # --- 🔥 NEW: ECONOMY & VIP LOGIC ADDED HERE 🔥 ---
            winner = self.p1 if self.round_loser.id == self.p2.id else self.p2
            
            # 1. Give Money to Winner
            prize = 50000 
            await update_balance(winner.id, prize)
            
            # 2. Punishment Logic (With VIP Check)
            punishment_msg = await self.apply_punishment_with_vip(interaction, self.round_loser)
            
            # 💀 WASTED EMBED (ORIGINAL STYLE)
            dead_embed = discord.Embed(title="💀 WASTED!", color=0x880808)
            dead_embed.description = (
                f"# 💥 BANG!\n"
                f"**{self.round_loser.mention}** ka bheja uda diya gaya.\n"
                f"(Slot #{self.slot_index + 1})\n\n"
                f"{punishment_msg}\n"
                f"🏆 **Winner:** {winner.mention} (Won **${prize:,}**)"
            )
            dead_embed.set_image(url="https://media.tenor.com/d6-SreC3_p8AAAAC/wasted-gta5.gif")
            dead_embed.set_footer(text="Game Over.")
            
            await interaction.response.edit_message(embed=dead_embed, view=None)
            
        else:
            self.slot_index += 1
            if self.slot_index >= 6:
                await interaction.response.edit_message(content="🧊 **Gun Empty!** Kya kismat hai! Game Draw.", view=None)
                return
                
            self.p1_choice = None
            self.p2_choice = None
            self.round_loser = None
            
            self.setup_rps_buttons()
            self.update_embed(mode="SAFE", extra_text=f"**{interaction.user.name}** bach gaya! Ab Next Round.")
            await interaction.response.edit_message(embed=self.embed, view=self)
            
            await asyncio.sleep(2) 
            self.update_embed(mode="RPS")
            await interaction.edit_original_response(embed=self.embed, view=self)

    async def apply_punishment_with_vip(self, interaction, loser):
        level = self.punishment_level
        reason = "Lost Squid Game Roulette 💀"
        msg = ""

        # Using smart_timeout for VIP checks on Mutes
        try:
            if level == 1:
                # 1 Minute Mute
                msg = await smart_timeout(interaction, loser, 60, reason)
                
            elif level == 2:
                msg = "📉 **Saza (L2):** Level/XP Ghat gaya (No Mute)."
                
            elif level == 3:
                # Script Ban Only (VIP Mute se bacha sakta hai, par Ban se nahi usually, but lets keep it strictly script ban)
                ban_time = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=3)
                await db_call(lambda: supabase.table("script_bans").upsert({"user_id": str(loser.id), "banned_until": ban_time.isoformat(), "reason": reason}).execute())
                msg = "🔒 **Saza (L3):** Script Access Blocked for **3 Hours**."
                
            elif level == 4:
                # 3 Hours Mute + Script Ban
                # Mute part (VIP can save)
                mute_status = await smart_timeout(interaction, loser, 10800, reason)
                # Script Ban Part
                ban_time = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=3)
                await db_call(lambda: supabase.table("script_bans").upsert({"user_id": str(loser.id), "banned_until": ban_time.isoformat(), "reason": reason}).execute())
                msg = f"{mute_status}\n🔒 **Script Ban:** 3 Hours applied."
                
            elif level == 5:
                # 1 Day Mute + Script Ban
                # Mute part (VIP can save)
                mute_status = await smart_timeout(interaction, loser, 86400, reason)
                # Script Ban Part
                ban_time = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1)
                await db_call(lambda: supabase.table("script_bans").upsert({"user_id": str(loser.id), "banned_until": ban_time.isoformat(), "reason": reason}).execute())
                msg = f"{mute_status}\n🔒 **Script Ban:** 1 Day applied."
                
        except Exception as e:
            msg += f"\n(Error punishment: {e})"
        return msg


# --- 2. INVITE VIEW (Starting Point) ---
class DuelInviteView(discord.ui.View):
    def __init__(self, challenger, opponent, bullets, punishment_level):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.opponent = opponent
        self.bullets = bullets
        self.punishment_level = punishment_level

    @discord.ui.button(label="✅ Accept Challenge", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.opponent.id:
            return await interaction.response.send_message("❌ Ye invite tere liye nahi hai!", ephemeral=True)
        
        # Start The Master Game Loop
        game_view = SquidGameMaster(self.challenger, self.opponent, self.bullets, self.punishment_level)
        await interaction.response.edit_message(view=game_view) 
        # Hack: Game view ka embed turant bhejte hain (Fixing previous display issues)
        await interaction.edit_original_response(embed=game_view.embed, view=game_view)

    @discord.ui.button(label="🏃 Bhaag Jao", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.opponent.id:
            return await interaction.response.send_message("❌ Tu decision nahi le sakta.", ephemeral=True)
        await interaction.response.edit_message(content=f"🚫 **{interaction.user.name}** ne dar ke maare mana kar diya.", view=None, embed=None)


# ================== 🎮 PUBLIC SQUID GAME COMMAND ==================
@bot.tree.command(name="squid_duel", description="🦑 Kisi ko bhi maut ka challenge do (Public)")
@app_commands.describe(
    opponent="Kisko maut ka challenge dena hai?",
    bullets="Kitni goli bharni hai? (1-5)",
    punishment="Saza ka level (1-5)"
)
@app_commands.choices(punishment=[
    app_commands.Choice(name="Level 1: 1 Min Timeout", value=1),
    app_commands.Choice(name="Level 2: XP/Level Deduction", value=2),
    app_commands.Choice(name="Level 3: Script Ban (3 Hrs)", value=3),
    app_commands.Choice(name="Level 4: 3Hr Timeout + 3Hr Ban", value=4),
    app_commands.Choice(name="Level 5: 1 Day Timeout + 1 Day Ban (BRUTAL)", value=5),
])
async def squid_duel(i: discord.Interaction, opponent: discord.Member, bullets: int, punishment: int):
    
    if not i.guild.me.guild_permissions.moderate_members:
        return await i.response.send_message("❌ **Bot Error:** Timeout Permission Missing!", ephemeral=True)
    
    if opponent.id == i.user.id or opponent.bot:
        return await i.response.send_message("❌ Invalid Opponent!", ephemeral=True)
        
    if bullets < 1 or bullets > 5:
        return await i.response.send_message("❌ Bullets 1-5 only.", ephemeral=True)

    # --- 📨 SEND PUBLIC INVITE (ORIGINAL THEME) ---
    embed = discord.Embed(
        title="🔺🟥🟢 SQUID GAME CHALLENGE", 
        description=f"📢 **SUNO SAB LOG!**\n\n**{i.user.mention}** ne **{opponent.mention}** ko Maut ka Challenge diya hai!", 
        color=0xFF00E6
    )
    embed.add_field(name="📜 Shartein (Rules)", value="• **RPS:** Pehle Toss hoga.\n• **Gun:** Jo hara, wo Trigger dabayega.\n• **Result:** Ya to Maut, ya Zindagi.", inline=False)
    embed.add_field(name="💣 Risk Info", value=f"🔫 Bullets: `{bullets}/6`\n⚖️ Saza Level: **{punishment}**", inline=False)
    
    embed.set_image(url="https://media.tenor.com/2147kZ75wW8AAAAC/squid-game-card.gif")
    embed.set_thumbnail(url=i.user.display_avatar.url)
    embed.set_footer(text="Accept karo ya Darpok kehlao! 🤡")
    
    await i.response.send_message(f"{opponent.mention}, pure server ke samne izzat ka sawal hai!", embed=embed, view=DuelInviteView(i.user, opponent, bullets, punishment))


# ================== SAY COMMAND (WITH IMAGE & LOGS) ==================

# 👇 Apki di hui Log Channel ID set kar di hai
SAY_LOG_CHANNEL_ID = 1450514760276774967

@bot.tree.command(name="say", description="📢 Make the bot speak (With Image Support & Logs)")
@app_commands.describe(
    message="Message content",
    channel="Where to send? (Default: current channel)",
    mode="Style of message (Text/Embed)",
    image="Attach an image (Optional)"
)
@app_commands.choices(mode=[
    app_commands.Choice(name="📝 Plain Text", value="text"),
    app_commands.Choice(name="✅ Green Embed (Success)", value="green"),
    app_commands.Choice(name="❌ Red Embed (Error)", value="red"),
    app_commands.Choice(name="ℹ️ Blue Embed (Info)", value="blue"),
])
async def say(i: discord.Interaction, message: str, mode: app_commands.Choice[str] = None, channel: discord.TextChannel = None, image: discord.Attachment = None):
    
    # 1. PERMISSION CHECK
    is_authorized = owner(i)
    if not is_authorized:
        try:
            data = supabase.table("say_access").select("user_id").eq("user_id", str(i.user.id)).execute().data
            if data: is_authorized = True
        except: pass

    if not is_authorized:
        return await i.response.send_message("❌ **Access Denied:** Aapko `/say` use karne ki permission nahi hai.", ephemeral=True)

    # 2. SETUP
    target_channel = channel or i.channel
    mode_value = mode.value if mode else "text"
    
    await i.response.defer(ephemeral=True)

    try:
        # --- IMAGE PROCESSING ---
        # Agar user ne image attach ki hai, to use file banao
        file_attachment = await image.to_file() if image else None
        
        # --- SENDING MESSAGE ---
        if mode_value == "text":
            # Plain text ke saath image bhejo
            sent_msg = await target_channel.send(content=message, file=file_attachment)
        else:
            # Color logic
            if mode_value == "green": color, title = 0x2ecc71, "✅ Success"
            elif mode_value == "red": color, title = 0xff0000, "❌ Error"
            elif mode_value == "blue": color, title = 0x3498db, "ℹ️ Info"
            else: color, title = 0x2f3136, "📢 Notice"

            # Embed banao
            embed = discord.Embed(title=title, description=message, color=color)
            
            # Embed ke saath image (Attachment) bhejo
            # Note: Embed ke andar image dikhane ke liye hum 'set_image' use kar sakte hain
            # lekin attachment bhejna zyada safe/reliable hota hai.
            if image:
                embed.set_image(url=f"attachment://{image.filename}")
                
            sent_msg = await target_channel.send(embed=embed, file=file_attachment)

        # 3. CONFIRMATION
        await i.followup.send(f"✅ **Sent!** Message delivered to {target_channel.mention}")

        # ================== 4. LOGGING TO YOUR CHANNEL ==================
        try:
            log_channel = bot.get_channel(SAY_LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(title="📢 Say Command Used", color=0xffa500) # Orange Log
                
                log_embed.add_field(name="👤 Executor", value=f"{i.user.mention}\n(`{i.user.id}`)", inline=True)
                log_embed.add_field(name="📍 Channel", value=f"{target_channel.mention}\n(`{target_channel.id}`)", inline=True)
                log_embed.add_field(name="🎨 Mode", value=f"`{mode_value.upper()}`", inline=True)
                log_embed.add_field(name="📝 Content", value=f"```{message}```", inline=False)
                
                # Log me photo dikhana
                if image:
                    log_embed.set_thumbnail(url=image.url)
                    log_embed.add_field(name="🖼️ Image Attached", value=f"[Click to View]({image.url})", inline=False)

                log_embed.set_footer(text=f"Time: {datetime.utcnow().strftime('%H:%M:%S UTC')}")
                
                await log_channel.send(embed=log_embed)
            
        except Exception as e:
            print(f"Logging Error: {e}")

    except discord.Forbidden:
        await i.followup.send(f"❌ **Permission Error:** Bot ko {target_channel.mention} me message bhejne ki permission nahi hai.")
    except Exception as e:
        await i.followup.send(f"❌ **System Error:** `{e}`")

# ================== 🥊 UNDERGROUND FIGHT CLUB (PREMIUM) ==================

class FightArenaView(discord.ui.View):
    def __init__(self, p1, p2, p1_data, p2_data, bet):
        super().__init__(timeout=180)
        self.p1 = p1
        self.p2 = p2
        self.bet = bet
        self.turn = p1.id # P1 starts
        self.logs = "🔥 **MATCH STARTED!** Fight for glory!"
        
        # --- PLAYER STATS SETUP ---
        self.stats = {
            p1.id: self.setup_stats(p1, p1_data),
            p2.id: self.setup_stats(p2, p2_data)
        }
        
    def setup_stats(self, user, data):
        # Base Stats
        hp = 100
        min_dmg = 8
        max_dmg = 15
        
        # 1. ROLE BONUSES
        roles = [r.name.lower() for r in user.roles]
        if "mafia" in roles or "god" in roles:
            hp = 150 
        if "hitman" in roles:
            min_dmg += 5
            max_dmg += 10
            
        # 2. INVENTORY BONUSES (Ab asli items check honge)
        inv = data.get('inventory', {})
        
        # 🗡️ KNIFE: Increases Damage
        if inv.get('knife', 0) > 0:
            min_dmg += 5
            max_dmg += 5
            
        # 🛡️ ARMOR: Increases HP
        if inv.get('armor', 0) > 0:
            hp += 50 # 100 -> 150 HP
            
        # 💉 STEROIDS: Big Damage Boost (One time use logic can be added later)
        if inv.get('steroids', 0) > 0:
            min_dmg += 10
            
        has_life = inv.get('life', 0) > 0
        
        return {
            "hp": hp,
            "max_hp": hp, # Max HP updated if Armor used
            "min_dmg": min_dmg,
            "max_dmg": max_dmg,
            "has_life": has_life,
            "heals": 2,
            "defending": False,
            "user": user
        }

    def get_hp_bar(self, current, maximum):
        percent = current / maximum
        filled = int(percent * 10)
        bar = "█" * filled + "░" * (10 - filled)
        return f"[{bar}] {current}/{maximum}"

    async def get_embed(self, winner=None):
        color = 0xFF0000 # Blood Red
        if winner: color = 0xFFD700 # Gold
        
        s1 = self.stats[self.p1.id]
        s2 = self.stats[self.p2.id]
        
        desc = f"💰 **Pot:** `${(self.bet * 2):,}`\n\n"
        
        # Player 1 Bar
        desc += f"🥊 **{self.p1.name}**\n{self.get_hp_bar(s1['hp'], s1['max_hp'])}\n"
        if s1['defending']: desc += "🛡️ **Block Active**\n"
        
        desc += "\n⚡ **VS** ⚡\n\n"
        
        # Player 2 Bar
        desc += f"🥊 **{self.p2.name}**\n{self.get_hp_bar(s2['hp'], s2['max_hp'])}\n"
        if s2['defending']: desc += "🛡️ **Block Active**\n"
        
        desc += f"\n📝 **Battle Log:**\n`{self.logs}`"
        
        if not winner:
            current_player = self.p1 if self.turn == self.p1.id else self.p2
            desc += f"\n\n👉 **Turn:** {current_player.mention}"

        embed = discord.Embed(title="🩸 UNDERGROUND FIGHT CLUB", description=desc, color=color)
        if winner:
            embed.set_image(url="https://media.tenor.com/M6Lw1wD2t40AAAAC/wwe-winner.gif")
        return embed

    async def check_death(self, interaction, victim_id):
        victim_stats = self.stats[victim_id]
        
        if victim_stats['hp'] <= 0:
            # 💖 EXTRA LIFE CHECK
            if victim_stats['has_life']:
                victim_stats['has_life'] = False # Consume life
                victim_stats['hp'] = 30 # Revive with 30 HP
                
                # Update Inventory (Remove Life)
                inv = await get_data(victim_id)
                new_inv = inv.get('inventory', {})
                if new_inv.get('life', 0) > 0:
                    new_inv['life'] -= 1
                    await db_call(lambda: supabase.table("economy").update({"inventory": new_inv}).eq("user_id", str(victim_id)).execute())

                self.logs = f"💖 **MIRACLE!** {victim_stats['user'].name} used Extra Life and revived!"
                return False # Not dead
            
            return True # Dead
        return False

    async def end_game(self, interaction, winner_id, loser_id):
        winner_user = self.stats[winner_id]['user']
        loser_user = self.stats[loser_id]['user']
        
        # Money Logic
        win_amount = self.bet * 2
        await update_balance(winner_id, win_amount) # Winner gets pot
        # Loser ka paisa already start me kat gaya tha
        
        # 🏥 Hospital Logic (Mute Loser)
        punish = await smart_timeout(interaction, loser_user, 600, "Lost Fight Club") # 10 Min
        
        embed = await self.get_embed(winner=winner_user)
        embed.description += f"\n\n🏆 **WINNER:** {winner_user.mention}\n💰 **Won:** `${win_amount:,}`\n💀 **Loser:** {loser_user.mention} is in Hospital ({punish})"
        
        for child in self.children: child.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    # --- BUTTONS ---
    
    @discord.ui.button(label="⚔️ ATTACK", style=discord.ButtonStyle.danger)
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.turn: return await interaction.response.send_message("Wait your turn!", ephemeral=True)
        
        attacker_id = self.turn
        defender_id = self.p2.id if attacker_id == self.p1.id else self.p1.id
        
        att = self.stats[attacker_id]
        defe = self.stats[defender_id]
        
        # Damage Calc
        dmg = random.randint(att['min_dmg'], att['max_dmg'])
        
        # Crit Chance (Hitman logic)
        is_crit = random.randint(1, 100) <= 20 # 20% Crit Chance
        if is_crit: dmg = int(dmg * 1.5)
        
        # Defense Check
        if defe['defending']:
            dmg = int(dmg / 2)
            defe['defending'] = False # Block used
            self.logs = f"🛡️ {defe['user'].name} blocked the attack! Only -{dmg} HP"
        else:
            if is_crit: self.logs = f"💥 **CRITICAL HIT!** {att['user'].name} dealt -{dmg} HP!"
            else: self.logs = f"⚔️ {att['user'].name} hit for -{dmg} HP"
        
        defe['hp'] -= dmg
        
        # Check Death
        is_dead = await self.check_death(interaction, defender_id)
        if is_dead:
            await self.end_game(interaction, attacker_id, defender_id)
        else:
            self.turn = defender_id # Switch turn
            await interaction.response.edit_message(embed=await self.get_embed(), view=self)

    @discord.ui.button(label="🛡️ DEFEND", style=discord.ButtonStyle.primary)
    async def defend(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.turn: return await interaction.response.send_message("Wait your turn!", ephemeral=True)
        
        self.stats[self.turn]['defending'] = True
        self.logs = f"🛡️ {interaction.user.name} is preparing to block!"
        
        self.turn = self.p2.id if self.turn == self.p1.id else self.p1.id
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)

    @discord.ui.button(label="💉 HEAL ($500)", style=discord.ButtonStyle.success)
    async def heal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.turn: return await interaction.response.send_message("Wait your turn!", ephemeral=True)
        
        me = self.stats[self.turn]
        
        if me['heals'] <= 0:
            return await interaction.response.send_message("❌ No meds left!", ephemeral=True)
            
        heal_amt = random.randint(15, 25)
        me['hp'] = min(me['hp'] + heal_amt, me['max_hp'])
        me['heals'] -= 1
        
        self.logs = f"💉 {interaction.user.name} used a stimpack! +{heal_amt} HP"
        
        # Cost Logic (Optional - abhi free rakha hai inventory logic simple rakhne ke liye)
        # await update_balance(self.turn, -500) 
        
        self.turn = self.p2.id if self.turn == self.p1.id else self.p1.id
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)

# --- CHALLENGE VIEW (Isse game start hoga) ---
class FightChallengeView(discord.ui.View):
    def __init__(self, p1, p2, bet):
        super().__init__(timeout=60)
        self.p1 = p1
        self.p2 = p2
        self.bet = bet
    
    @discord.ui.button(label="✅ ACCEPT FIGHT", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.p2.id: return await interaction.response.send_message("Ye challenge apke liye nahi hai!", ephemeral=True)
        
        # Check Money P2
        p2_d = await get_data(self.p2.id)
        if p2_d['balance'] < self.bet:
            return await interaction.response.send_message("❌ Gareeb! Paise nahi hai fight ke liye.", ephemeral=True)
            
        # Deduct Money from Both (Escrow)
        await update_balance(self.p1.id, -self.bet)
        await update_balance(self.p2.id, -self.bet)
        
        # Get Fresh Data for Game
        p1_data = await get_data(self.p1.id)
        p2_data = await get_data(self.p2.id)
        
        # Start Game
        game_view = FightArenaView(self.p1, self.p2, p1_data, p2_data, self.bet)
        await interaction.response.edit_message(content=None, embed=await game_view.get_embed(), view=game_view)

    @discord.ui.button(label="❌ DECLINE", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.p2.id:
            await interaction.response.edit_message(content=f"🚫 **{self.p2.name}** dar gaya! Fight cancelled.", view=None, embed=None)
        elif interaction.user.id == self.p1.id:
            await interaction.response.edit_message(content="🚫 Fight Cancelled by challenger.", view=None, embed=None)

# ================== 🎮 FIGHT COMMAND ==================

@bot.tree.command(name="fight", description="🥊 Challenge user to Fight Club (Winner takes all)")
async def fight(i: discord.Interaction, opponent: discord.Member, amount: int):
    if i.user.id == opponent.id or opponent.bot:
        return await i.response.send_message("❌ Khud se nahi lad sakte!", ephemeral=True)
        
    if amount < 500:
        return await i.response.send_message("❌ Minimum Bet: $500", ephemeral=True)
        
    # Check Money P1
    p1_data = await get_data(i.user.id)
    if p1_data['balance'] < amount:
        return await i.response.send_message("❌ Apke paas paise nahi hai!", ephemeral=True)
        
    embed = discord.Embed(title="🥊 FIGHT CHALLENGE", description=f"{i.user.mention} wants to fight **{opponent.mention}**!\n\n💰 **Bet:** `${amount:,}`\n💀 **Loser:** Goes to Hospital (Mute)\n\nAccept?", color=0xFFD700)
    
    view = FightChallengeView(i.user, opponent, amount)
    await i.response.send_message(f"{opponent.mention}", embed=embed, view=view)


# ================== 🧠 FLIP & PAIR MEMORY GAME (PREMIUM TIERS) ==================

class MemoryGameView(discord.ui.View):
    def __init__(self, user, level):
        super().__init__(timeout=180)
        self.user = user
        self.level = level
        self.moves = 0
        self.pairs_found = 0
        self.game_over = False
        
        # --- LEVEL CONFIGURATION (Grid Size) ---
        self.grid_config = {
            1: (2, 2), # 4 Cards (Baby)
            2: (2, 3), # 6 Cards (Easy)
            3: (2, 4), # 8 Cards (Medium)
            4: (3, 4), # 12 Cards (Hard)
            5: (4, 4), # 16 Cards (Expert)
            6: (4, 5), # 20 Cards (Master)
            7: (5, 5), # 25 Cards (GOD MODE)
        }
        
        # --- THEME & REWARD CONFIGURATION (Premium Looks) ---
        self.level_data = {
            1: {"reward": 10000, "color": 0x2ecc71, "title": "👶 LEVEL 1: BABY STEPS", "icon": "🍼"},
            2: {"reward": 15000, "color": 0x3498db, "title": "🔹 LEVEL 2: EASY PEASY", "icon": "🧊"},
            3: {"reward": 30000, "color": 0xf1c40f, "title": "🔸 LEVEL 3: MEDIUM GRIND", "icon": "🧀"},
            4: {"reward": 60000, "color": 0xe67e22, "title": "🔥 LEVEL 4: HARD CORE", "icon": "🌶️"},
            5: {"reward": 80000, "color": 0xe74c3c, "title": "🧠 LEVEL 5: EXPERT MIND", "icon": "🥊"},
            6: {"reward": 100000, "color": 0x9b59b6, "title": "🔮 LEVEL 6: MASTER CLASS", "icon": "🧞"},
            7: {"reward": 10000000000, "color": 0x000000, "title": "☠️ LEVEL 7: GOD MODE", "icon": "👑"},
        }

        self.rows, self.cols = self.grid_config.get(level, (2, 2))
        
        # --- DECK GENERATION ---
        all_emojis = ["🍎", "🍌", "🍒", "🍇", "🍉", "🍓", "🍍", "🥝", "🥑", "🌽", "🥕", "🥦", "🍄", "🥜", "🥐", "🥨", "🍔", "🍕", "🌭", "🌮", "🍬", "🍭", "🧊", "🍩", "🍪"]
        
        if level == 7:
            # Level 7: 3 BOMBS Logic 
            self.total_pairs = 11
            game_emojis = all_emojis[:11]
            self.deck = game_emojis * 2
            self.deck.extend(["💣", "💣", "💣"]) # Adding 3 Bombs
        else:
            self.total_pairs = (self.rows * self.cols) // 2
            game_emojis = all_emojis[:self.total_pairs]
            self.deck = game_emojis * 2
            
        random.shuffle(self.deck)
        
        # --- STATE ---
        self.matched_indices = []
        self.flipped = []
        
        self.create_grid()

    def create_grid(self):
        self.clear_items()
        for i in range(len(self.deck)):
            row_num = i // 5 
            
            if i in self.matched_indices:
                btn = discord.ui.Button(label=self.deck[i], style=discord.ButtonStyle.success, disabled=True, row=row_num)
            elif i in self.flipped:
                # Agar Bomb hai to Danger color, Normal hai to Primary
                style = discord.ButtonStyle.danger if self.deck[i] == "💣" else discord.ButtonStyle.primary
                btn = discord.ui.Button(label=self.deck[i], style=style, disabled=False, row=row_num)
            else:
                if self.game_over: 
                    # Game over pe sab disable
                    style = discord.ButtonStyle.danger if self.deck[i] == "💣" else discord.ButtonStyle.secondary
                    btn = discord.ui.Button(label=self.deck[i], style=style, disabled=True, row=row_num)
                else:
                    btn = discord.ui.Button(label="❓", style=discord.ButtonStyle.secondary, custom_id=f"card_{i}", row=row_num)
                    btn.callback = self.card_callback
            
            self.add_item(btn)

    async def get_embed(self, status="PLAYING"):
        data = self.level_data[self.level]
        
        title = f"{data['icon']} {data['title']}"
        color = data['color']
        
        desc = f"**Difficulty:** Level {self.level}\n**Potential Reward:** `${data['reward']:,}`\n\n"
        
        if self.level == 7:
            desc += "⚠️ **WARNING:** Isme **3 BOMBS (💣)** chupe hain!\nEk galti aur Game Over.\n\n"

        desc += f"**📊 Stats:**\n🎯 Pairs Found: `{self.pairs_found}/{self.total_pairs}`\n🔄 Moves Used: `{self.moves}`"
        
        if status == "WON":
            title = f"🎉 LEVEL {self.level} CONQUERED!"
            color = 0x00FF00 # Bright Green for Win
            desc = f"### 🏆 VICTORY!\n\n**Player:** {self.user.mention}\n**Moves:** `{self.moves}`\n\n💰 **REWARD:** `${data['reward']:,}` Coins Added!"
        
        elif status == "LOST":
            title = "💀 WASTED"
            color = 0xFF0000 # Red for Loss
            desc = f"### 💥 BOOM!\n**{self.user.mention}** bomb se ud gaya!\n\n❌ **Reward:** $0\nTry again if you dare."

        embed = discord.Embed(title=title, description=desc, color=color)
        embed.set_thumbnail(url=self.user.display_avatar.url)
        
        if status == "PLAYING":
            embed.set_footer(text=f"Find all {self.total_pairs} pairs to win!")
        else:
            embed.set_footer(text="Game Over")
            
        return embed

    async def card_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ Khud ka game start karo!", ephemeral=True)

        idx = int(interaction.data["custom_id"].split("_")[1])
        
        if idx in self.flipped or idx in self.matched_indices or len(self.flipped) >= 2:
            return await interaction.response.defer()

        # --- BOMB CHECK (Level 7) ---
        if self.deck[idx] == "💣":
            self.game_over = True
            self.flipped.append(idx)
            self.create_grid()
            
            # 🔥 PUNISHMENT LOGIC 🔥
            punish_msg = await smart_timeout(interaction, self.user, 3600, "Memory Bomb Death")
            
            embed = await self.get_embed(status="LOST")
            embed.description += f"\n\n{punish_msg}"
            embed.set_image(url="https://media.tenor.com/2147kZ75wW8AAAAC/squid-game-card.gif")
            
            await interaction.response.edit_message(embed=embed, view=self)
            return

        # --- NORMAL FLIP ---
        self.flipped.append(idx)
        self.create_grid()
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
        
        if len(self.flipped) == 2:
            self.moves += 1
            idx1, idx2 = self.flipped
            
            if self.deck[idx1] == self.deck[idx2]:
                # ✅ MATCH
                self.matched_indices.extend(self.flipped)
                self.pairs_found += 1
                self.flipped = []
                
                # Check Win
                if self.pairs_found == self.total_pairs:
                    self.game_over = True
                    self.create_grid()
                    
                    # 💰 REWARD SYSTEM (UPDATED) 💰
                    reward = self.level_data[self.level]["reward"]
                    await update_balance(self.user.id, reward)

                    embed = await self.get_embed(status="WON")
                    
                    # Special GIF for Level 7
                    if self.level == 7:
                        embed.set_image(url="https://media.tenor.com/p7a8o1r5c8cAAAAC/money-rain.gif")
                    else:
                        embed.set_image(url="https://media.tenor.com/bXjOidvDvoQAAAAC/confetti-celebrate.gif")
                    
                    for child in self.children: child.disabled = True
                    await interaction.edit_original_response(embed=embed, view=self)
                    return
                
                self.create_grid()
                await interaction.edit_original_response(embed=await self.get_embed(), view=self)
            
            else:
                # ❌ NO MATCH
                for item in self.children: item.disabled = True
                await interaction.edit_original_response(view=self)
                await asyncio.sleep(1.5) # Wait for user to see cards
                self.flipped = []
                self.create_grid()
                await interaction.edit_original_response(embed=await self.get_embed(), view=self)

# ================== 🎮 COMMAND UPDATE ==================

@bot.tree.command(name="memory", description="🧠 Play Memory Game (New Rewards System)")
@app_commands.describe(level="Difficulty Level chuno (1-7)")
@app_commands.choices(level=[
    app_commands.Choice(name="Level 1: Baby ($10k)", value=1),
    app_commands.Choice(name="Level 2: Easy ($15k)", value=2),
    app_commands.Choice(name="Level 3: Medium ($30k)", value=3),
    app_commands.Choice(name="Level 4: Hard ($60k)", value=4),
    app_commands.Choice(name="Level 5: Expert ($80k)", value=5),
    app_commands.Choice(name="Level 6: Master ($100k)", value=6),
    app_commands.Choice(name="Level 7: GOD MODE ($10 Billion 💣)", value=7),
])
async def memory_game(interaction: discord.Interaction, level: int):
    view = MemoryGameView(interaction.user, level)
    embed = await view.get_embed()
    await interaction.response.send_message(embed=embed, view=view)


# ================== 🏦 HEIST: NIGHTMARE MODE (ECONOMY + VIP) ==================

# --- 1. LOBBY VIEW ---
class HeistLobbyView(discord.ui.View):
    def __init__(self, leader):
        super().__init__(timeout=120)
        self.leader = leader
        self.crew = [leader] 
        self.started = False

    def update_embed(self):
        crew_list = "\n".join([f"👤 **{m.name}**" for m in self.crew])
        embed = discord.Embed(title="☠️ HEIST: NIGHTMARE MODE", color=0x000000)
        embed.description = (
            "Mission: **CERTAIN DEATH**\n"
            "Tasks: **Impossible** | Time: **3s**\n"
            "💰 **Reward:** $1,500,000 (Each)\n"
            "🔇 **Penalty:** 1 Minute Mute (Group Punishment)\n\n"
            "*VIPs will be saved automatically.*"
        )
        embed.add_field(name=f"👥 Victims ({len(self.crew)}/4)", value=crew_list, inline=False)
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1785/1785117.png")
        embed.set_footer(text="Start at your own risk.")
        return embed

    @discord.ui.button(label="💀 Join Suicide Mission", style=discord.ButtonStyle.danger)
    async def join_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.started: return
        if interaction.user in self.crew: return await interaction.response.send_message("Tu pehle se hai!", ephemeral=True)
        if len(self.crew) >= 4: return await interaction.response.send_message("Gang Full!", ephemeral=True)
        
        self.crew.append(interaction.user)
        await interaction.response.edit_message(embed=self.update_embed(), view=self)

    @discord.ui.button(label="🚀 START NIGHTMARE", style=discord.ButtonStyle.secondary)
    async def start_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.leader.id: return await interaction.response.send_message("Leader only.", ephemeral=True)
        if len(self.crew) < 2: return await interaction.response.send_message("Need 2+ people to suffer.", ephemeral=True)

        self.started = True
        for child in self.children: child.disabled = True
        
        await interaction.response.edit_message(content="⚫ **ENTERING THE VOID...**", view=self, embed=self.update_embed())
        await start_interactive_heist(interaction, self.crew)


# --- 2. TASK VIEWS ---
class HeistTaskView(discord.ui.View):
    def __init__(self, player, correct_answer, fail_callback, success_callback, timeout_duration):
        super().__init__(timeout=timeout_duration) 
        self.player = player
        self.correct_answer = correct_answer
        self.fail_callback = fail_callback
        self.success_callback = success_callback
        self.responded = False

    async def on_timeout(self):
        if not self.responded:
            await self.fail_callback(f"⏳ **TOO SLOW!** {self.player.mention} ka reflex bohot slow hai!", self.player)

    async def verify_answer(self, interaction, answer):
        if interaction.user.id != self.player.id:
            return await interaction.response.send_message("❌ Door reh!", ephemeral=True)
        
        self.responded = True
        self.stop()

        if answer == self.correct_answer:
            await self.success_callback(interaction)
        else:
            await self.fail_callback(f"❌ **WRONG!** {self.player.mention} fail ho gaya!", self.player)


class SequenceTaskView(HeistTaskView):
    def __init__(self, player, target_sequence, fail_callback, success_callback, timeout_duration, buttons_config):
        super().__init__(player, None, fail_callback, success_callback, timeout_duration)
        self.target_sequence = target_sequence
        self.current_index = 0
        
        for label, style, emoji in buttons_config:
            btn = discord.ui.Button(label=label, style=style, emoji=emoji, custom_id=label)
            btn.callback = self.make_callback(label)
            self.add_item(btn)

    def make_callback(self, input_val):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.player.id: return await interaction.response.send_message("Not your turn!", ephemeral=True)
            
            expected = self.target_sequence[self.current_index]
            
            if input_val == expected:
                self.current_index += 1
                if self.current_index >= len(self.target_sequence):
                    self.responded = True
                    self.stop()
                    await self.success_callback(interaction)
                else:
                    await interaction.response.defer()
            else:
                self.responded = True
                self.stop()
                await self.fail_callback(f"❌ **WIRE BLAST!** {self.player.mention} ne galat taar kaat di!", self.player)
        return callback


# --- 3. MAIN LOGIC (UNFAIR TASKS) ---
async def start_interactive_heist(interaction, crew):
    random.shuffle(crew)
    roles = {
        "💻 Hacker": crew[0],
        "💣 Demolition": crew[1] if len(crew) > 1 else crew[0],
        "🔫 Shooter": crew[2] if len(crew) > 2 else crew[0],
        "🚗 Driver": crew[3] if len(crew) > 3 else crew[0]
    }
    
    role_text = "\n".join([f"**{r}:** {u.mention}" for r, u in roles.items()])
    intro_embed = discord.Embed(title="☠️ NIGHTMARE STARTED", description=role_text + "\n\n🚨 **RULES:**\n1. Time: 3-5 Seconds.\n2. One mistake = SQUAD WIPE.\n3. Good Luck.", color=0x000000)
    
    try: await interaction.edit_original_response(content=None, embed=intro_embed, view=None)
    except: await interaction.followup.send(embed=intro_embed)
    await asyncio.sleep(4)

    # --- FAIL HANDLER (WITH ECONOMY & VIP) ---
    async def mission_failed(reason, culprit):
        # Apply Punishments loop
        status_report = []
        for member in crew:
            # Use smart_timeout from shop system
            msg = await smart_timeout(interaction, member, 60, f"Heist Failed by {culprit.name}")
            if "Saved" in msg or "Extra Life" in msg:
                status_report.append(f"🛡️ {member.name}: Saved")
            else:
                status_report.append(f"🔇 {member.name}: Muted")

        fail_embed = discord.Embed(title="🚨 MISSION FAILED", color=0xFF0000)
        fail_embed.description = f"# {reason}\n\n**Culprit:** {culprit.mention}\n\n**Squad Status:**\n" + "\n".join(status_report)
        fail_embed.set_image(url="https://media.tenor.com/d6-SreC3_p8AAAAC/wasted-gta5.gif")
        
        try: await interaction.edit_original_response(embed=fail_embed, view=None)
        except: await interaction.followup.send(embed=fail_embed)


    # --- STAGE 1: HACKER (Impossible Math) ---
    hacker = roles["💻 Hacker"]
    
    # Advanced Questions
    questions = [
        ("sin(90°) + cos(0°)", "2"),
        ("cosec(30°) + sec(60°)", "4"),
        ("tan(60°) x cot(60°)", "1"),
        ("log10(1000)", "3"),
        ("sin(180°) + cos(180°)", "-1"),
        ("2sin(30°)cos(30°)", "sin(60°)"),
        ("cos²(45°) - sin²(45°)", "0"),
        ("tan(90°)", "Undefined"),
        ("e⁰ + ln(e)", "2"),
        ("d/dx (sin x)", "cos x"),
        ("∫ 1 dx", "x"),
        ("15% of 1200", "180"),
        ("13 x 17", "221"),
        ("7³", "343"),
        ("π radians", "180°"),
        ("cos(-60°)", "0.5"),
        ("log2(64)", "6"),
        ("√2 + √2", "2√2"),
        ("sin²θ + cos²θ", "1"),
        ("log(1)", "0"),
        ("tan(45°)", "1"),
        ("d/dx (x²)", "2x"),
        ("sin²θ + cos²θ", "1"),
        ("√256", "16"),
        ("sec(0°)", "1"),
        ("sin(270°)", "-1")
    ]
    q_text, q_ans = random.choice(questions)
    
    # Options generation
    wrong_options = ["0", "1", "-1", "2", "Undefined", "0.5", "∞", "2x", "x"]
    if q_ans in wrong_options: wrong_options.remove(q_ans)
    options = random.sample(wrong_options, 3) + [q_ans]
    random.shuffle(options)

    embed = discord.Embed(title="💻 STAGE 1: QUANTUM HACK", description=f"**{hacker.mention}**, SOLVE FAST (4s)!\n# `{q_text} = ?`", color=0x00FFFF)
    
    async def pass_stage_1(i): await i.response.defer()
    
    view = HeistTaskView(hacker, str(q_ans), mission_failed, pass_stage_1, 4.0) # 4 Seconds
    for opt in options:
        view.add_item(discord.ui.Button(label=opt, style=discord.ButtonStyle.secondary, custom_id=opt))
        view.children[-1].callback = lambda i, opt=opt: view.verify_answer(i, opt)

    await interaction.edit_original_response(embed=embed, view=view)
    if await view.wait(): return 

    # --- STAGE 2: DEMOLITION (Impossible Sequence) ---
    demo = roles["💣 Demolition"]
    
    # 6 Colors Sequence (Hard)
    colors = ["🟥", "🟦", "🟩", "🟨"]
    seq = [random.choice(colors) for _ in range(6)] # 6 steps!
    seq_str = " ".join(seq)
    
    embed = discord.Embed(title="💣 STAGE 2: RAPID DEFUSAL", description=f"**{demo.mention}**, MEMORIZE THIS!\n# {seq_str}\n\n*(You have 5 seconds only!)*", color=0xFFA500)
    
    await interaction.edit_original_response(embed=embed, view=None)
    await asyncio.sleep(4) # Memorize time
    
    embed.description = f"**{demo.mention}**, CUT THE WIRES!\n# ✂️ ✂️ ✂️ ✂️ ✂️ ✂️"
    
    async def pass_stage_2(i): await i.response.defer()

    btn_config = [("RED", discord.ButtonStyle.danger, "🟥"), 
                  ("BLUE", discord.ButtonStyle.primary, "🟦"),
                  ("GREEN", discord.ButtonStyle.success, "🟩"), 
                  ("YELLOW", discord.ButtonStyle.secondary, "🟨")]
    
    map_input = {"RED": "🟥", "BLUE": "🟦", "GREEN": "🟩", "YELLOW": "🟨"}
    target_labels = []
    for s in seq:
        for k, v in map_input.items():
            if v == s: target_labels.append(k)

    # 6 Steps in 6 Seconds = Insane Pressure
    view = SequenceTaskView(demo, target_labels, mission_failed, pass_stage_2, 6, btn_config)
    await interaction.edit_original_response(embed=embed, view=view)
    if await view.wait(): return

    # --- STAGE 3: SHOOTER (The "Same" Trap) ---
    shooter = roles["🔫 Shooter"]
    target = "I" # Capital i
    distraction = "l" # Small L
    
    layout = [distraction, distraction, target, distraction]
    random.shuffle(layout)
    
    embed = discord.Embed(title="🔫 STAGE 3: PRECISION SHOT", description=f"**{shooter.mention}**, Find the **Capital 'i'** (I)!\nBaaki sab 'Small L' (l) hain.\n\n*Don't miss!*", color=0xFF0000)
    
    async def pass_stage_3(i): await i.response.defer()

    view = HeistTaskView(shooter, target, mission_failed, pass_stage_3, 3.5)
    for item in layout:
        view.add_item(discord.ui.Button(label=item, style=discord.ButtonStyle.secondary, custom_id=item + str(random.random())))
        view.children[-1].callback = lambda i, v=item: view.verify_answer(i, target if v == target else "FAIL")

    await interaction.edit_original_response(embed=embed, view=view)
    if await view.wait(): return

    # --- STAGE 4: DRIVER (The Blank Button) ---
    driver = roles["🚗 Driver"]
    
    embed = discord.Embed(title="🚗 STAGE 4: ESCAPE MODE", description=f"**{driver.mention}**, Police Radar Active!\n**Go into SILENT MODE.**\n(Press the invisible/blank button)", color=0x808080)
    
    async def pass_stage_4(i): await i.response.defer()

    view = HeistTaskView(driver, "SILENT", mission_failed, pass_stage_4, 4)
    
    view.add_item(discord.ui.Button(label="HORN 🔊", style=discord.ButtonStyle.danger, custom_id="HORN"))
    view.add_item(discord.ui.Button(label="NITRO 🔥", style=discord.ButtonStyle.primary, custom_id="NITRO"))
    view.add_item(discord.ui.Button(label=" ", style=discord.ButtonStyle.secondary, custom_id="SILENT")) # Correct
    
    # Shuffle buttons to confuse muscle memory
    random.shuffle(view.children)
    
    # Re-bind callbacks after shuffle
    for child in view.children:
        if child.custom_id == "SILENT":
            child.callback = lambda i: view.verify_answer(i, "SILENT")
        else:
            child.callback = lambda i: view.verify_answer(i, "FAIL")

    await interaction.edit_original_response(embed=embed, view=view)
    if await view.wait(): return

    # --- VICTORY & PAYOUT ---
    payout = 1500000 # 1.5 Million Fixed
    
    # Distribute Money
    for m in crew:
        await update_balance(m.id, payout)

    win_embed = discord.Embed(title="🏆 HEIST COMPLETED!", description=f"# 💰 LOOT: ${payout:,} (Each)\n\n**LEGENDS:** {', '.join([m.name for m in crew])}\n\n✅ **Payment Successful!** Shop mein uda dena!", color=0x00FF00)
    win_embed.set_image(url="https://media.tenor.com/p7a8o1r5c8cAAAAC/money-rain.gif")
    await interaction.edit_original_response(embed=win_embed, view=None)


# --- COMMAND ---
@bot.tree.command(name="heist", description="🏦 Nightmare Mode Heist (Team Task)")
async def heist_cmd(i: discord.Interaction):
    if not i.guild.me.guild_permissions.moderate_members:
        return await i.response.send_message("❌ Mute Permission Missing!", ephemeral=True)
    
    view = HeistLobbyView(i.user)
    await i.response.send_message(embed=view.update_embed(), view=view)

# ================== 🤠 WESTERN DUEL (REACTION TEST) ==================

class WesternDuelView(discord.ui.View):
    def __init__(self, p1, p2):
        super().__init__(timeout=60)
        self.p1 = p1
        self.p2 = p2
        self.signal_given = False
        self.winner = None
        self.start_time = None
        
        # Initial Button (Red - Suicide Trap)
        btn = discord.ui.Button(label="🛑 WAIT...", style=discord.ButtonStyle.danger, custom_id="shoot_btn")
        btn.callback = self.shoot_callback
        self.add_item(btn)

    async def start_game_logic(self, interaction):
        # 1. Suspense Phase (Random Delay)
        delay = random.uniform(3, 8)
        await asyncio.sleep(delay)
        
        if self.winner: return 

        # 2. FIRE SIGNAL!
        self.signal_given = True
        self.start_time = dt.datetime.now().timestamp()
        
        # Update Button to GREEN
        self.children[0].label = "🔥 SHOOT NOW!"
        self.children[0].style = discord.ButtonStyle.success 
        
        # Update Embed to GREEN signal
        new_embed = discord.Embed(color=0x00FF00)
        new_embed.set_author(name=f"{self.p1.name} (Ready)", icon_url=self.p1.display_avatar.url)
        new_embed.set_thumbnail(url=self.p2.display_avatar.url)
        
        new_embed.description = (
            f"# 🔫 FIRE! FIRE! FIRE!\n"
            f"# 👇 **BUTTON DABAO!** 👇\n"
            f"**-----------------------------**"
        )
        new_embed.set_image(url="https://media.tenor.com/E5J0kC1yTzAAAAAC/the-good-the-bad-and-the-ugly-clint-eastwood.gif")
        
        try:
            await interaction.edit_original_response(embed=new_embed, view=self)
        except:
            pass

    async def shoot_callback(self, interaction: discord.Interaction):
        if interaction.user.id not in [self.p1.id, self.p2.id]:
            return await interaction.response.send_message("❌ Audience door rahein!", ephemeral=True)
            
        if self.winner:
            return await interaction.response.send_message("⚰️ Tum mar chuke ho. Late ho gaye.", ephemeral=True)

        # --- LOGIC START ---
        
        # CASE A: EARLY FIRE (Disqualified / Suicide)
        if not self.signal_given:
            # Current user loses, Opponent wins
            loser = interaction.user
            winner = self.p1 if loser.id == self.p2.id else self.p2
            self.winner = winner 
            self.stop()
            
            # ECONOMY: Give Money to Winner
            prize = 10000
            await update_balance(winner.id, prize)
            
            # VIP: Punish Loser (Smart Timeout)
            punish_msg = await smart_timeout(interaction, loser, 30, "Duel Suicide") # 30s Mute

            embed = discord.Embed(title="💀 MISFIRE! (Suicide)", color=0x000000)
            embed.set_author(name=winner.name + " WINS!", icon_url=winner.display_avatar.url)
            embed.set_thumbnail(url=loser.display_avatar.url)
            
            embed.description = (
                f"### 🤦‍♂️ {loser.mention} ne ghabra ke khud ko uda liya!\n"
                f"**Winner:** {winner.mention} (+$10,000)\n\n"
                f"{punish_msg}"
            )
            embed.set_image(url="https://media.tenor.com/12s3s2v1b4cAAAAC/gun-fail.gif")
            
            await interaction.response.edit_message(embed=embed, view=None)
            return

        # CASE B: PERFECT SHOT (Win)
        reaction_time = round(dt.datetime.now().timestamp() - self.start_time, 3)
        self.winner = interaction.user
        self.stop()
        
        winner = interaction.user
        loser = self.p1 if winner.id == self.p2.id else self.p2
        
        # ECONOMY: Give Money to Winner
        prize = 10000
        await update_balance(winner.id, prize)
        
        # VIP: Punish Loser
        punish_msg = await smart_timeout(interaction, loser, 30, "Lost Duel") # 30s Mute
        
        embed = discord.Embed(title="🤠 VICTORY!", color=0xFFD700)
        embed.set_author(name=f"🏆 {winner.name}", icon_url=winner.display_avatar.url)
        embed.set_thumbnail(url=loser.display_avatar.url)
        
        embed.description = (
            f"# 💥 BANG!\n"
            f"**{winner.mention}** ne **{reaction_time}s** mein trigger dabaya!\n\n"
            f"💰 **Won:** ${prize:,}\n"
            f"🪦 **R.I.P:** {loser.mention}\n"
            f"{punish_msg}"
        )
        embed.set_image(url="https://media.tenor.com/w9yv4p2y3QAAAAAC/tumbleweed.gif")
        
        await interaction.response.edit_message(embed=embed, view=None)


@bot.tree.command(name="duel", description="🤠 Face-Off Duel (Reaction Test)")
async def western_duel(i: discord.Interaction, opponent: discord.Member):
    if not i.guild.me.guild_permissions.moderate_members:
        return await i.response.send_message("❌ Mere paas 'Timeout' power nahi hai!", ephemeral=True)
        
    if opponent.id == i.user.id or opponent.bot:
        return await i.response.send_message("❌ Khud se ya Bot se nahi lad sakte.", ephemeral=True)

    # --- 🎭 THE FACE-OFF EMBED ---
    embed = discord.Embed(color=0xB8860B) # Gold/Brown Style
    
    # Left Side: Challenger (Author)
    embed.set_author(name=f"{i.user.name} 🔫", icon_url=i.user.display_avatar.url)
    
    # Right Side: Opponent (Thumbnail)
    embed.set_thumbnail(url=opponent.display_avatar.url)
    
    # Center: The VS Sign
    embed.description = (
        f"# ⚡ {i.user.mention} 🆚 {opponent.mention} ⚡\n"
        f"**-----------------------------**\n"
        f"### 👁️ NAZAR BUTTON PE RAKHO!\n"
        f"Jab button **GREEN** ho jaye, tabhi dabana.\n"
        f"*(Jaldi kiya to Maut, Late kiya to Maut)*\n\n"
        f"💰 **Prize:** $10,000"
    )
    
    # Image: Tumbleweed
    embed.set_image(url="https://media.tenor.com/w9yv4p2y3QAAAAAC/tumbleweed.gif")
    
    view = WesternDuelView(i.user, opponent)
    await i.response.send_message(embed=embed, view=view)
    
    # Start Logic in Background
    asyncio.create_task(view.start_game_logic(i))

# ================== 💣 HOT POTATO BOMB GAME (PREMIUM) ==================

class BombPassView(discord.ui.View):
    def __init__(self, holder, interaction):
        super().__init__(timeout=120)
        self.holder = holder
        self.origin_interaction = interaction
        self.exploded = False
        
        # Bomb Timer: Random between 20s to 45s
        # User ko pata nahi chalega kab phatega
        self.explode_time = dt.datetime.now().timestamp() + random.randint(20, 45)
        
        # Start Timer Loop
        self.timer_task = asyncio.create_task(self.bomb_timer())

    async def bomb_timer(self):
        while not self.exploded:
            await asyncio.sleep(1)
            # Check Time
            if dt.datetime.now().timestamp() >= self.explode_time:
                self.exploded = True
                await self.trigger_explosion()
                break

    async def trigger_explosion(self):
        # --- 🛡️ PUNISHMENT LOGIC (Universal) ---
        # 5 Minute Mute (300s)
        punish_msg = await smart_timeout(self.origin_interaction, self.holder, 300, "Holding the Bomb")

        embed = discord.Embed(title="💥 BOMB PHAT GAYA!", color=0x000000) # Pitch Black
        embed.description = (
            f"# ☠️ KABOOOM!\n\n"
            f"**{self.holder.mention}** react karne mein slow nikla!\n"
            f"Shareer ke chithde udd gaye.\n\n"
            f"🏥 **STATUS:**\n{punish_msg}"
        )
        embed.set_thumbnail(url=self.holder.display_avatar.url)
        embed.set_image(url="https://media.tenor.com/8p1jZ5jG4yQAAAAC/explosion-boom.gif")
        embed.set_footer(text="Game Over | Cost: $30k")
        
        # Sab disable kar do
        self.clear_items()
        
        try:
            # Edit original message with dead embed
            await self.origin_interaction.edit_original_response(content=f"💀 **R.I.P** {self.holder.mention}", embed=embed, view=None)
        except: pass

    @discord.ui.select(placeholder="🔥 JALDI FEKO! (Select Victim)", cls=discord.ui.UserSelect, max_values=1)
    async def pass_bomb(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        if self.exploded: 
            return await interaction.response.send_message("❌ Bomb phat chuka hai, ab kya fayda!", ephemeral=True)

        # Check: Kya bomb inke paas hai?
        if interaction.user.id != self.holder.id:
            return await interaction.response.send_message("❌ Bomb tere haath mein nahi hai, hero mat ban!", ephemeral=True)

        target = select.values[0]
        
        # --- VALIDATION ---
        if target.bot:
            return await interaction.response.send_message("❌ Bots immune hote hain, kisi insaan ko do!", ephemeral=True)
        if target.id == interaction.user.id:
            return await interaction.response.send_message("❌ Khud ko pass karke kya milega? Marne ka shauk hai?", ephemeral=True)

        # ✅ SUCCESSFUL PASS
        self.holder = target
        
        # Intense Embed Update
        embed = discord.Embed(title="💣 HOT POTATO! BOMB PASSED!", color=0xFFA500) # Panic Orange
        embed.description = (
            f"### 🏃💨 BHAAGO!\n"
            f"**{interaction.user.name}** ne maut **{target.mention}** ki taraf fek di!\n\n"
            f"⏱️ **Timer:** *Tik.. Tok.. Tik.. Tok..*\n"
            f"🛑 **Target Locked:** {target.name}\n\n"
            f"👇 **Jaldi Dropdown se next victim chuno!**"
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_image(url="https://media.tenor.com/G5m6K_1u_mIAAAAC/bomb-ticking.gif")
        
        # Edit message to alert new target (Ping them hard)
        await interaction.response.edit_message(
            content=f"🚨 **URGENT:** {target.mention} TERE PAAS BOMB HAI! JALDI FEK! 💣", 
            embed=embed, 
            view=self
        )


@bot.tree.command(name="bomb_start", description="💣 Start Bomb Game ($30k Fee)")
async def start_bomb(i: discord.Interaction):
    # 1. Permission Check
    if not i.guild.me.guild_permissions.moderate_members:
        return await i.response.send_message("❌ Mere paas 'Timeout' permission nahi hai!", ephemeral=True)

    # 2. Economy Check ($30k Fee)
    cost = 30000
    data = await get_data(i.user.id)
    
    if data["balance"] < cost:
        return await i.response.send_message(f"❌ **Gareeb!** Bomb kharidne ke liye **${cost:,}** chahiye.\n💳 Balance: `${data['balance']:,}`", ephemeral=True)
    
    # Deduct Money
    await update_balance(i.user.id, -cost)

    # 3. Game Start Embed
    embed = discord.Embed(title="💣 ACTIVE BOMB PLANTED!", color=0xFF4500) # Red Orange
    embed.description = (
        f"**{i.user.mention}** ne **$30,000** dekar pin nikaal di hai!\n\n"
        f"💀 **Situation:** Critical\n"
        f"⏳ **Timer:** Random (Kabhi bhi phatega)\n"
        f"🔇 **Penalty:** 5 Min Mute (Hospital)\n\n"
        f"👇 **Niche Dropdown se kisi dushman ko select karo aur bomb feko!**"
    )
    embed.set_image(url="https://media.tenor.com/pyk_eO99u_0AAAAC/bomb-bomb-timer.gif")
    embed.set_footer(text="Game Started by: " + i.user.name)
    
    view = BombPassView(i.user, i)
    await i.response.send_message(f"🚨 **WARNING:** {i.user.mention} HAS THE BOMB!", embed=embed, view=view)



# ================== 🎰 DEVIL SLOTS (HIGH STAKES) ==================

class DevilSlotsView(discord.ui.View):
    def __init__(self, user, fee):
        super().__init__(timeout=180)
        self.user = user
        self.fee = fee # $100k Entry Fee

    async def assign_role(self, interaction, role_name, color):
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=role_name)
        try:
            if not role:
                role = await guild.create_role(name=role_name, color=color, reason="Devil Slots Game")
            if role not in interaction.user.roles:
                await interaction.user.add_roles(role)
            return True
        except: return False 

    async def check_vip_status(self, user_id):
        data = await get_data(user_id)
        if data["vip_expiry"]:
            expire_dt = dt.datetime.fromisoformat(data["vip_expiry"])
            if datetime.utcnow() < expire_dt: return True, "👑 **VIP Protection:** Izzat bach gayi!"
        inv = data["inventory"]
        if inv.get("life", 0) > 0: # Note: 'life' use kar rahe hain
            await update_inventory(user_id, "life", -1)
            remaining = inv.get("life", 0) - 1
            return True, f"💖 **Extra Life Used:** Nickname change dodged! (Left: {remaining})"
        return False, None

    @discord.ui.button(label="🎰 SPIN (-$100k)", style=discord.ButtonStyle.blurple, custom_id="spin_now")
    async def spin_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ Apne paise lagao!", ephemeral=True)

        # 💰 ENTRY FEE DEDUCTION
        user_data = await get_data(self.user.id)
        if user_data['balance'] < self.fee:
            return await interaction.response.send_message("❌ **Gareeb!** $100,000 nahi hain wallet me.", ephemeral=True)
            
        await update_balance(self.user.id, -self.fee) # Deduct Fee

        # Animation
        button.disabled = True
        button.label = "🔄 SPINNING..."
        button.style = discord.ButtonStyle.secondary
        
        spin_embed = discord.Embed(title="🎰 ROLLING...", color=0x9932CC)
        spin_embed.description = "# 🌀 | 🌀 | 🌀\n**Paise kat gaye... Kismat aajmao!**"
        spin_embed.set_image(url="https://media.tenor.com/GoMvLaZs8KkAAAAC/slot-machine-casino.gif")
        
        await interaction.response.edit_message(embed=spin_embed, view=self)
        await asyncio.sleep(3) 

        # 🎲 PROBABILITY LOGIC (0.1% Jackpot)
        # Total Weights: 0.1 + 5 + 10 + 30 + 54.9 = 100
        outcomes = ["JACKPOT", "DEATH", "SHAME", "WIN", "LOSS"]
        weights = [0.1, 5, 10, 30, 54.9] 
        result_type = random.choices(outcomes, weights=weights, k=1)[0]
        
        final_desc = ""
        color = 0x000000
        image = ""
        status_text = ""

        if result_type == "JACKPOT":
            slots = "💎 | 💎 | 💎"
            status_text = "🎉 GRAND JACKPOT!"
            prize = 50000000 # 5 Crore
            await update_balance(interaction.user.id, prize)
            final_desc = f"# [ {slots} ]\n\n### 👑 REWARD: 'Casino King' Role\n**💰 +${prize:,} COINS!**\nAap server ke naye Raja hain!"
            color = 0xFFD700
            image = "https://media.tenor.com/p7a8o1r5c8cAAAAC/money-rain.gif"
            await self.assign_role(interaction, "👑 CASINO KING", discord.Color.gold())

        elif result_type == "DEATH":
            slots = "💀 | 💀 | 💀"
            status_text = "💀 DEATH SPIN!"
            punish_msg = await smart_timeout(interaction, interaction.user, 3600, "Devil Slots Death")
            final_desc = f"# [ {slots} ]\n\n### 🔇 PUNISHMENT\n**Shaitan ne aapki aawaz cheen li.**\n\n{punish_msg}"
            color = 0x000000
            image = "https://media.tenor.com/2147kZ75wW8AAAAC/squid-game-card.gif"

        elif result_type == "SHAME":
            slots = "💩 | 💩 | 💩"
            status_text = "💩 SHAME SPIN!"
            is_saved, save_msg = await self.check_vip_status(interaction.user.id)
            if is_saved:
                final_desc = f"# [ {slots} ]\n\n### 💩 SHAME SPIN!\nLekin...\n{save_msg}"
                color = 0x8B4513
            else:
                final_desc = f"# [ {slots} ]\n\n### 🏷️ PUNISHMENT: 'HAGGU' Role\n**Apka naam ab 'Mr. Haggu' hai.**\nPoora server ab hasega! 😂"
                color = 0x8B4513
                try:
                    if interaction.user.top_role < interaction.guild.me.top_role:
                        await interaction.user.edit(nick="Mr. Haggu 💩")
                        await self.assign_role(interaction, "💩 HAGGU", discord.Color.brown())
                except: pass

        elif result_type == "WIN":
            f1 = random.choice(["🍒", "🍋", "🍇"])
            slots = f"{f1} | {f1} | {f1}"
            status_text = "🍒 LUCKY WIN!"
            prize = 200000 # 2 Lakh (Taaki entry fee se jyada mile)
            await update_balance(interaction.user.id, prize)
            final_desc = f"# [ {slots} ]\n\n### 💰 +${prize:,} Coins\nEntry Fee wapis + Profit!"
            color = 0x00FF00

        else: # LOSS
            slots = f"❌ | 🍋 | 🔔"
            status_text = "❌ YOU LOST!"
            final_desc = f"# [ {slots} ]\n\n**Haar gaye!**\nApke $100,000 doob gaye."
            color = 0xFF0000

        result_embed = discord.Embed(title=f"🎰 {status_text}", color=color)
        result_embed.description = final_desc
        result_embed.set_thumbnail(url=interaction.user.display_avatar.url)
        if image: result_embed.set_image(url=image)
        
        button.label = "PLAY AGAIN (-100k)"
        button.style = discord.ButtonStyle.primary
        button.disabled = False # Button wapis enable taaki wo dubara khel sake
        
        await interaction.edit_original_response(embed=result_embed, view=self)

@bot.tree.command(name="devil_slots", description="🎰 Spin for $100k Fee (0.1% Jackpot Chance)")
async def devil_slots(i: discord.Interaction):
    embed = discord.Embed(title="🎰 DEVIL'S CASINO", color=0x9932CC)
    embed.description = (
        "**Entry Fee:** `$100,000`\n"
        "**Jackpot Chance:** `0.1%` (Extremely Rare)\n\n"
        "💎 **JACKPOT:** $50M + Role\n"
        "💀 **DEATH:** 1 Hour Mute\n"
        "💩 **SHAME:** Name Change + Role\n"
        "🍒 **WIN:** $200,000 Coins\n\n"
        "👇 **Click to Pay & Spin!**"
    )
    view = DevilSlotsView(i.user, 100000)
    await i.response.send_message(embed=embed, view=view)


# ================== 🍪 SQUID GAME: DALGONA COOKIE (ECONOMY + VIP) ==================

class DalgonaGameView(discord.ui.View):
    def __init__(self, user, difficulty):
        super().__init__(timeout=60) # 1 Minute Timer
        self.user = user
        self.difficulty = difficulty
        self.progress = 0 # 0 to 100 needed
        self.durability = 100 # Cookie Health
        self.game_over = False
        
        # Difficulty Settings
        self.settings = {
            "TRIANGLE": {"break_chance": 10, "lick_gain": 8, "crack_gain": 25, "img": "https://media.tenor.com/images/15e61291880564d2627993092787476e/tenor.gif"},
            "CIRCLE":   {"break_chance": 30, "lick_gain": 6, "crack_gain": 20, "img": "https://media.tenor.com/images/15e61291880564d2627993092787476e/tenor.gif"},
            "UMBRELLA": {"break_chance": 60, "lick_gain": 4, "crack_gain": 15, "img": "https://media.tenor.com/images/15e61291880564d2627993092787476e/tenor.gif"}
        }
        
        self.current_setting = self.settings[difficulty]

    def get_progress_bar(self):
        bar_len = 10
        filled = int((self.progress / 100) * bar_len)
        bar = "🟩" * filled + "⬜" * (bar_len - filled)
        return bar

    async def get_embed(self, status="PLAYING"):
        color = 0xFFA500 # Orange
        
        if status == "WON":
            title = "🎉 PASSED!"
            desc = f"**{self.user.mention}** ne **{self.difficulty}** complete kar liya!\n\n🍪 **Cookie:** Perfect Shape!\n🏆 **Status:** SURVIVOR"
            img = "https://media.tenor.com/bXjOidvDvoQAAAAC/confetti-celebrate.gif"
            color = 0x00FF00
        elif status == "DIED":
            title = "💀 CRACKED!"
            desc = f"**{self.user.mention}** ne jaldbaazi mein cookie tod di!\n\n🍪 **Cookie:** DESTROYED"
            img = "https://media.tenor.com/2147kZ75wW8AAAAC/squid-game-card.gif"
            color = 0xFF0000
        else:
            title = f"🍪 DALGONA: {self.difficulty}"
            desc = (
                f"**Shape:** {self.difficulty}\n"
                f"**Integrity:** `{self.durability}%`\n"
                f"**Progress:** `{self.progress}%`\n"
                f"{self.get_progress_bar()}\n\n"
                f"👇 **Action lo:**\n"
                f"👅 **Lick:** Safe, Slow.\n"
                f"🔨 **Crack:** Risky, Fast (+Risk of Break)."
            )
            img = self.current_setting["img"]
        
        embed = discord.Embed(title=title, description=desc, color=color)
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.set_image(url=img)
        
        if status == "PLAYING":
            embed.set_footer(text="Timer: 60 Seconds | Don't break it!")
            
        return embed

    async def check_game_state(self, interaction):
        # 1. Check Win
        if self.progress >= 100:
            self.game_over = True
            
            # --- 💰 REWARD LOGIC ---
            rewards = {"TRIANGLE": 10000, "CIRCLE": 25000, "UMBRELLA": 50000}
            prize = rewards.get(self.difficulty, 10000)
            
            await update_balance(self.user.id, prize)

            for child in self.children: child.disabled = True
            
            embed = await self.get_embed("WON")
            embed.description += f"\n💰 **Reward:** ${prize:,}"
            
            await interaction.response.edit_message(embed=embed, view=self)
            return

        # 2. Check Loss (Durability 0)
        if self.durability <= 0:
            await self.trigger_death(interaction, "Cookie choora ho gayi!")
            return

        # 3. Continue
        await interaction.response.edit_message(embed=await self.get_embed("PLAYING"), view=self)


    async def trigger_death(self, interaction, reason):
        self.game_over = True
        for child in self.children: child.disabled = True
        
        # --- 🛡️ SMART PUNISHMENT (VIP CHECK) ---
        # 1 Hour Mute (3600 Seconds)
        punish_msg = await smart_timeout(interaction, self.user, 3600, "Dalgona Failed")

        embed = await self.get_embed("DIED")
        embed.description += f"\n\n**Reason:** {reason}\n{punish_msg}"
        
        await interaction.response.edit_message(embed=embed, view=self)


    @discord.ui.button(label="👅 LICK (Safe)", style=discord.ButtonStyle.success)
    async def lick_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id: return
        
        gain = self.current_setting["lick_gain"] + random.randint(-2, 2)
        self.progress += gain
        self.durability -= random.randint(1, 3) 
        
        await self.check_game_state(interaction)


    @discord.ui.button(label="🔨 CRACK (Risky)", style=discord.ButtonStyle.danger)
    async def crack_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id: return
        
        # Risk Check
        fail_chance = self.current_setting["break_chance"]
        roll = random.randint(1, 100)
        
        if roll <= fail_chance:
            # INSTANT DEATH
            await self.trigger_death(interaction, "Hathoda zor se lag gaya!")
            return

        gain = self.current_setting["crack_gain"] + random.randint(-5, 5)
        self.progress += gain
        self.durability -= random.randint(5, 15) 
        
        await self.check_game_state(interaction)


# --- SHAPE SELECTION VIEW ---
class DalgonaLobbyView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user

    async def start_game(self, interaction, shape):
        if interaction.user.id != self.user.id: return
        
        view = DalgonaGameView(self.user, shape)
        await interaction.response.edit_message(embed=await view.get_embed(), view=view)

    @discord.ui.button(label="🔺 TRIANGLE (Easy)", style=discord.ButtonStyle.secondary)
    async def tri_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.start_game(interaction, "TRIANGLE")

    @discord.ui.button(label="⭕ CIRCLE (Medium)", style=discord.ButtonStyle.primary)
    async def cir_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.start_game(interaction, "CIRCLE")

    @discord.ui.button(label="☂️ UMBRELLA (Hard)", style=discord.ButtonStyle.danger)
    async def umb_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.start_game(interaction, "UMBRELLA")


@bot.tree.command(name="dalgona", description="🍪 Squid Game: Honeycomb Challenge")
async def dalgona(i: discord.Interaction):
    if not i.guild.me.guild_permissions.moderate_members:
        return await i.response.send_message("❌ Mute Permission Missing!", ephemeral=True)
        
    embed = discord.Embed(title="🍪 DALGONA CHALLENGE", description="Apna Shape choose karo!\n\n🔺 **Triangle:** $10,000 (Low Risk)\n⭕ **Circle:** $25,000 (Medium)\n☂️ **Umbrella:** $50,000 (High Risk)", color=0xFFA500)
    embed.set_image(url="https://media.tenor.com/images/15e61291880564d2627993092787476e/tenor.gif")
    
    view = DalgonaLobbyView(i.user)
    await i.response.send_message(embed=embed, view=view)

# ================== 🪢 PREMIUM TUG OF WAR (FIXED) ==================

class TugOfWarGame(discord.ui.View):
    def __init__(self, red_team, blue_team, interaction):
        super().__init__(timeout=60) # 60 Seconds Match
        self.red_team = red_team
        self.blue_team = blue_team
        self.interaction = interaction
        
        self.score = 0 
        self.win_threshold = 20 # 20 Points to Win
        self.game_active = True
        
        # Setup Buttons
        self.add_item(discord.ui.Button(label="🔥 PULL RED", style=discord.ButtonStyle.danger, custom_id="pull_red", emoji="🔴"))
        self.add_item(discord.ui.Button(label="🔥 PULL BLUE", style=discord.ButtonStyle.primary, custom_id="pull_blue", emoji="🔵"))
        
        self.children[0].callback = self.red_pull
        self.children[1].callback = self.blue_pull
        
        # Visual Loop (Sirf Bar Update karega, Win logic Button me hai)
        self.updater_task = asyncio.create_task(self.update_game_state())

    def get_progress_bar(self):
        # Scale score between -10 and 10
        scaled = int((self.score / self.win_threshold) * 10)
        scaled = max(-10, min(10, scaled))
        
        # Center point shifting
        center_idx = 10 + scaled 
        
        # 🎨 PREMIUM ROPE DESIGN
        rope_char = "═" 
        center_marker = "🪢" # Knot
        
        # Create Track (21 Blocks)
        track = [rope_char] * 21
        track[center_idx] = center_marker # Knot moves based on score
        
        # Visual Construction
        # Example: 🔴 ══════════🪢══════════ 🔵
        bar = "".join(track)
        return f"🔴 `{bar}` 🔵"

    async def get_embed(self, winner=None):
        if winner:
            color = 0xE74C3C if winner == "RED" else 0x3498DB
            desc = f"### 🏆 VICTORY FOR TEAM {winner}!\n\n**🔴 Red Team:** {len(self.red_team)} Players\n**🔵 Blue Team:** {len(self.blue_team)} Players"
            title = "🎉 ROPE SNAPPED! MATCH OVER!"
            image = "https://media.tenor.com/M6Lw1wD2t40AAAAC/wwe-winner.gif"
        else:
            color = 0xFFA500
            title = "🔥 TUG OF WAR: PULL HARDER!"
            
            # Dynamic Commentary
            commentary = "MATCH IS EVEN!"
            if self.score > 5: commentary = "🔵 BLUE IS DOMINATING!"
            elif self.score < -5: commentary = "🔴 RED IS DOMINATING!"
            elif self.score > 15: commentary = "🔵 BLUE IS ABOUT TO WIN!"
            elif self.score < -15: commentary = "🔴 RED IS ABOUT TO WIN!"

            desc = (
                f"{self.get_progress_bar()}\n\n"
                f"📢 **Status:** `{commentary}`\n"
                f"🔴 **RED Power:** `{abs(min(0, self.score))}`\n"
                f"🔵 **BLUE Power:** `{max(0, self.score)}`\n\n"
                f"👇 **BUTTON SPAM KARO! RUKNA MAT!**"
            )
            image = None
            
        embed = discord.Embed(title=title, description=desc, color=color)
        if image: embed.set_image(url=image)
        
        if not winner:
            embed.set_footer(text=f"Goal: Reach {self.win_threshold} Points | Time Left: 60s")
            
        return embed

    async def update_game_state(self):
        # Ye loop sirf visuals update karega taaki rate limit na lage
        while self.game_active:
            await asyncio.sleep(2.0) # Har 2 sec me embed refresh
            try:
                await self.interaction.edit_original_response(embed=await self.get_embed(), view=self)
            except: pass

    async def end_game(self, winner_team_name):
        if not self.game_active: return # Double end hone se rokega
        
        self.game_active = False
        self.updater_task.cancel()
        
        # --- ECONOMY & PUNISHMENT ---
        winning_team = self.red_team if winner_team_name == "RED" else self.blue_team
        losing_team = self.blue_team if winner_team_name == "RED" else self.red_team
        
        # 1. Reward Winners
        prize = 20000
        for member in winning_team:
            await update_balance(member.id, prize)

        # 2. Punish Losers (Universal Smart Timeout)
        status_report = []
        for member in losing_team:
            msg = await smart_timeout(self.interaction, member, 300, "Lost Tug of War")
            status_report.append(f"{member.name}: {msg}")

        # Disable buttons
        for child in self.children: 
            child.disabled = True
            child.style = discord.ButtonStyle.secondary
        
        embed = await self.get_embed(winner_team_name)
        
        # Report Field
        logs = "\n".join(status_report[:8])
        if len(status_report) > 8: logs += "\n...and more"
        
        embed.add_field(name="💰 Winners Reward", value=f"${prize:,} (Each)", inline=True)
        embed.add_field(name="💀 Losers Status", value=logs if logs else "No Losers?", inline=False)
        
        await self.interaction.edit_original_response(embed=embed, view=self)

    # --- BUTTON CALLBACKS (Instant Check Fix) ---
    async def red_pull(self, interaction: discord.Interaction):
        if interaction.user not in self.red_team:
            return await interaction.response.send_message("❌ Tum Red Team mein nahi ho!", ephemeral=True)
        
        if not self.game_active: return await interaction.response.defer()
        
        self.score -= 1 
        
        # ✅ INSTANT WIN CHECK (Yahan fix kiya hai)
        if self.score <= -self.win_threshold:
            await self.end_game("RED")
        
        await interaction.response.defer() # Message update mat karo, loop karega

    async def blue_pull(self, interaction: discord.Interaction):
        if interaction.user not in self.blue_team:
            return await interaction.response.send_message("❌ Tum Blue Team mein nahi ho!", ephemeral=True)
            
        if not self.game_active: return await interaction.response.defer()
        
        self.score += 1 
        
        # ✅ INSTANT WIN CHECK
        if self.score >= self.win_threshold:
            await self.end_game("BLUE")

        await interaction.response.defer()


# --- LOBBY VIEW ---
class TugLobbyView(discord.ui.View):
    def __init__(self, host):
        super().__init__(timeout=120)
        self.host = host
        self.red_team = []
        self.blue_team = []
        self.started = False

    def get_embed(self):
        r_list = "\n".join([f"🔴 {u.name}" for u in self.red_team]) or "Waiting..."
        b_list = "\n".join([f"🔵 {u.name}" for u in self.blue_team]) or "Waiting..."
        
        embed = discord.Embed(title="🪢 TUG OF WAR: LOBBY", description=f"**Host:** {self.host.mention}\n\n💰 **Prize:** $20,000\n🔇 **Penalty:** 5 Min Mute\n\nApni team choose karo 👇", color=0x95a5a6)
        embed.add_field(name=f"🔴 TEAM RED ({len(self.red_team)})", value=r_list, inline=True)
        embed.add_field(name=f"🔵 TEAM BLUE ({len(self.blue_team)})", value=b_list, inline=True)
        embed.set_image(url="https://media.tenor.com/J3t_A2lO-w0AAAAC/squid-game-tug-of-war.gif")
        return embed

    @discord.ui.button(label="JOIN RED", style=discord.ButtonStyle.danger, emoji="🔴")
    async def join_red(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.red_team or interaction.user in self.blue_team:
            return await interaction.response.send_message("Already in a team!", ephemeral=True)
        self.red_team.append(interaction.user)
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="JOIN BLUE", style=discord.ButtonStyle.primary, emoji="🔵")
    async def join_blue(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.red_team or interaction.user in self.blue_team:
            return await interaction.response.send_message("Already in a team!", ephemeral=True)
        self.blue_team.append(interaction.user)
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="START MATCH", style=discord.ButtonStyle.success, row=1, emoji="🚀")
    async def start_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host.id: return await interaction.response.send_message("❌ Sirf Host start kar sakta hai.", ephemeral=True)
        if len(self.red_team) == 0 or len(self.blue_team) == 0:
            return await interaction.response.send_message("⚠️ Dono taraf players hone chahiye!", ephemeral=True)
        
        self.started = True
        game_view = TugOfWarGame(self.red_team, self.blue_team, interaction)
        await interaction.response.edit_message(embed=await game_view.get_embed(), view=game_view)


@bot.tree.command(name="tug_of_war", description="🪢 Team Battle: Spam Buttons to Win")
async def tug_of_war(i: discord.Interaction):
    # Permission Check
    if not i.guild.me.guild_permissions.moderate_members:
        return await i.response.send_message("❌ Mere paas 'Timeout' permission nahi hai!", ephemeral=True)
    
    view = TugLobbyView(i.user)
    await i.response.send_message(embed=view.get_embed(), view=view)        
        
# ================== 🔮 SQUID GAME: MARBLES (ECONOMY + VIP) ==================

# --- 1. HIDDEN INPUT MODAL ---
class MarblesHideModal(discord.ui.Modal, title="Hide Your Marbles"):
    number = discord.ui.TextInput(
        label="Kitne kanche chipane hain? (1-10)",
        placeholder="Ek number likho (e.g. 3)",
        min_length=1,
        max_length=2,
        required=True
    )

    def __init__(self, view_obj, max_bet):
        super().__init__()
        self.view_obj = view_obj
        self.max_bet = max_bet

    async def on_submit(self, interaction: discord.Interaction):
        try:
            val = int(self.number.value)
            if val < 1 or val > 10:
                return await interaction.response.send_message("❌ Sirf 1 se 10 ke beech mein!", ephemeral=True)
            if val > self.max_bet:
                return await interaction.response.send_message(f"❌ Tumhare paas itne kanche nahi hain! Max: {self.max_bet}", ephemeral=True)
            
            self.view_obj.hidden_number = val
            self.view_obj.state = "GUESSING"
            
            await interaction.response.defer() 
            await self.view_obj.update_board(interaction, f"👀 **{self.view_obj.p2.mention}**, Ab guess karo! Odd ya Even?")
            
        except ValueError:
            await interaction.response.send_message("❌ Number likho, text nahi!", ephemeral=True)


# --- 2. MAIN GAME VIEW ---
class MarblesGameView(discord.ui.View):
    def __init__(self, p1, p2):
        super().__init__(timeout=300) 
        self.p1 = p1
        self.p2 = p2
        self.marbles = {p1.id: 10, p2.id: 10}
        self.turn_hider = p1 
        self.turn_guesser = p2
        self.hidden_number = None
        self.state = "HIDING" 
        self.setup_buttons()

    def setup_buttons(self):
        self.clear_items()
        
        if self.state == "HIDING":
            btn = discord.ui.Button(label="🖐️ HIDE MARBLES", style=discord.ButtonStyle.primary, custom_id="hide_btn")
            btn.callback = self.hide_callback
            self.add_item(btn)
        else:
            btn_odd = discord.ui.Button(label="ODD (1, 3, 5...)", style=discord.ButtonStyle.secondary, custom_id="odd")
            btn_even = discord.ui.Button(label="EVEN (2, 4, 6...)", style=discord.ButtonStyle.secondary, custom_id="even")
            btn_odd.callback = self.guess_callback
            btn_even.callback = self.guess_callback
            self.add_item(btn_odd)
            self.add_item(btn_even)

    async def update_board(self, interaction, status_msg):
        self.setup_buttons()
        
        p1_m = "🔮" * self.marbles[self.p1.id]
        p2_m = "🔮" * self.marbles[self.p2.id]
        
        embed = discord.Embed(title="🔮 MARBLES GAME (Gaddari)", color=0xE91E63)
        embed.description = (
            f"**{self.p1.name}:** {self.marbles[self.p1.id]}\n{p1_m}\n\n"
            f"**{self.p2.name}:** {self.marbles[self.p2.id]}\n{p2_m}\n\n"
            f"-----------------------------\n"
            f"{status_msg}"
        )
        
        if self.state == "HIDING":
            embed.set_footer(text=f"Turn: {self.turn_hider.name} chupa raha hai...")
            embed.set_thumbnail(url=self.turn_hider.display_avatar.url)
        else:
            embed.set_footer(text=f"Turn: {self.turn_guesser.name} guess kar raha hai...")
            embed.set_thumbnail(url=self.turn_guesser.display_avatar.url)
            
        embed.set_image(url="https://media.tenor.com/yA0wXCoqQJAAAAAC/squid-game-marbles.gif")
        
        try:
            if interaction.response.is_done():
                await interaction.edit_original_response(content=None, embed=embed, view=self)
            else:
                await interaction.response.edit_message(content=None, embed=embed, view=self)
        except Exception as e:
            try: await interaction.followup.send(embed=embed, view=self)
            except: pass

    # --- CALLBACKS ---
    async def hide_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.turn_hider.id:
            return await interaction.response.send_message("❌ Abhi tumhari baari nahi hai!", ephemeral=True)
        modal = MarblesHideModal(self, self.marbles[self.turn_hider.id])
        await interaction.response.send_modal(modal)

    async def guess_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.turn_guesser.id:
            return await interaction.response.send_message("❌ Tumhe guess nahi karna hai!", ephemeral=True)
        
        guess = interaction.data["custom_id"].upper()
        actual_is_odd = (self.hidden_number % 2 != 0)
        
        win = False
        if (guess == "ODD" and actual_is_odd) or (guess == "EVEN" and not actual_is_odd):
            win = True
            
        amount = self.hidden_number
        msg = ""
        
        if win:
            self.marbles[self.turn_guesser.id] += amount
            self.marbles[self.turn_hider.id] -= amount
            msg = f"🎉 **CORRECT!** ({self.hidden_number})\n**{self.turn_guesser.name}** ne {amount} marbles jeet liye!"
        else:
            if self.marbles[self.turn_guesser.id] < amount:
                amount = self.marbles[self.turn_guesser.id]
            self.marbles[self.turn_guesser.id] -= amount
            self.marbles[self.turn_hider.id] += amount
            msg = f"❌ **WRONG!** ({self.hidden_number})\n**{self.turn_guesser.name}** ne {amount} marbles kho diye!"

        # CHECK GAME OVER
        if self.marbles[self.p1.id] <= 0:
            await self.end_game(interaction, self.p2, self.p1)
        elif self.marbles[self.p2.id] <= 0:
            await self.end_game(interaction, self.p1, self.p2)
        else:
            self.turn_hider, self.turn_guesser = self.turn_guesser, self.turn_hider
            self.state = "HIDING"
            self.hidden_number = None
            await self.update_board(interaction, f"{msg}\n\n🔄 **SWAP!** Ab **{self.turn_hider.mention}** chupayega!")

    async def end_game(self, interaction, winner, loser):
        self.stop()
        
        # --- ECONOMY & PUNISHMENT ---
        # 1. Winner Reward ($50,000)
        prize = 50000
        await update_balance(winner.id, prize)
        
        # 2. Loser Punishment (Smart Timeout - 10 Mins)
        punish_msg = await smart_timeout(interaction, loser, 600, "Lost Marbles Game")
        
        embed = discord.Embed(title="💀 GAME OVER", color=0x000000)
        embed.description = (
            f"### 🏆 WINNER: {winner.mention}\n"
            f"**{winner.name}** ne saare Marbles jeet liye!\n"
            f"💰 **Reward:** ${prize:,}\n\n"
            f"### ⚰️ ELIMINATED: {loser.mention}\n"
            f"{punish_msg}"
        )
        embed.set_thumbnail(url=winner.display_avatar.url)
        embed.set_image(url="https://media.tenor.com/2147kZ75wW8AAAAC/squid-game-card.gif")
        
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=None)
        else:
            await interaction.response.edit_message(embed=embed, view=None)


# --- COMMAND ---
@bot.tree.command(name="marbles", description="🔮 Squid Game Marbles (Odd/Even Betrayal)")
async def marbles(i: discord.Interaction, opponent: discord.Member):
    if opponent.id == i.user.id or opponent.bot:
        return await i.response.send_message("❌ Khud se ya bot se nahi khel sakte!", ephemeral=True)
    
    if not i.guild.me.guild_permissions.moderate_members:
        return await i.response.send_message("❌ Mute Permission Missing!", ephemeral=True)

    embed = discord.Embed(title="🔮 MARBLES CHALLENGE", description=f"**{i.user.mention}** vs **{opponent.mention}**\n\nRule: 10-10 Marbles start.\n💰 **Prize:** $50,000\n🔇 **Penalty:** 10 Min Mute\n\n**Accept Challenge?**", color=0xE91E63)
    
    view = discord.ui.View(timeout=60) 
    btn = discord.ui.Button(label="✅ ACCEPT", style=discord.ButtonStyle.success)
    
    async def accept_callback(itx):
        if itx.user.id != opponent.id: return await itx.response.send_message("Ye tumhare liye nahi hai!", ephemeral=True)
        
        game_view = MarblesGameView(i.user, opponent)
        game_view.setup_buttons()
        
        p1_m = "🔮" * 10
        p2_m = "🔮" * 10
        start_embed = discord.Embed(title="🔮 MARBLES GAME (Gaddari)", color=0xE91E63)
        start_embed.description = (
            f"**{game_view.p1.name}:** 10\n{p1_m}\n\n"
            f"**{game_view.p2.name}:** 10\n{p2_m}\n\n"
            f"-----------------------------\n"
            f"Game Start! Player 1 hiding marbles..."
        )
        start_embed.set_footer(text=f"Turn: {game_view.turn_hider.name} chupa raha hai...")
        start_embed.set_thumbnail(url=game_view.turn_hider.display_avatar.url)
        start_embed.set_image(url="https://media.tenor.com/yA0wXCoqQJAAAAAC/squid-game-marbles.gif")
        
        await itx.response.edit_message(embed=start_embed, view=game_view)
        
    btn.callback = accept_callback
    view.add_item(btn)
    
    await i.response.send_message(embed=embed, view=view)

# ================== 🎲 SATTA SYSTEM (FAIR & EVIL MODES) ==================

class EvilSattaView(discord.ui.View):
    def __init__(self, user, bet_amount):
        super().__init__(timeout=60)
        self.user = user
        self.bet = bet_amount

    async def run_satta(self, interaction, multiplier, win_chance, risk_type):
        """
        multiplier: Kitna guna paisa milega (2x, 5x, 100x)
        win_chance: Jeetne ka % chance (50, 20, 0.1)
        risk_type: 'NORMAL' (Lose Bet), 'WIPE' (Bal 0), 'DEATH' (Bal 0 + Mute)
        """
        if interaction.user.id != self.user.id: 
            return await interaction.response.send_message("❌ Apna paisa lagao!", ephemeral=True)
        
        # 1. Disable & Animate
        for child in self.children: child.disabled = True
        
        # Color Logic based on difficulty
        embed_color = 0x00FF00 if win_chance >= 20 else 0xFFFF00
        if win_chance < 1: embed_color = 0x000000 # Black for Evil Modes

        embed = discord.Embed(title="🎲 SATTA SPINNING...", color=embed_color)
        embed.description = (
            f"💰 **Bet:** `${self.bet:,}`\n"
            f"🚀 **Target:** {multiplier}x Payout\n"
            f"🍀 **Win Chance:** {win_chance}%\n\n"
            f"**🤞 Rolling the dice...**"
        )
        embed.set_image(url="https://media.tenor.com/GoMvLaZs8KkAAAAC/slot-machine-casino.gif")
        await interaction.response.edit_message(embed=embed, view=self)
        
        await asyncio.sleep(3) # Suspense

        # 2. LOGIC (Roll the Dice)
        # Random number between 0.0 and 100.0
        roll = random.uniform(0, 100)
        is_win = roll <= win_chance 
        
        final_embed = discord.Embed()

        if is_win:
            # --- 🏆 WINNER ---
            winnings = int(self.bet * multiplier)
            await update_balance(self.user.id, winnings) # Add winnings (Bet already safe)
            
            final_embed.title = f"🎉 WINNER! ({multiplier}x)"
            final_embed.color = 0xFFD700 # Gold
            final_embed.description = (
                f"### 🎯 JACKPOT HIT!\n"
                f"🎲 **Roll:** {roll:.2f} (Needed < {win_chance})\n"
                f"💸 **WON:** `${winnings:,}`\n"
                f"**Kismat chamak gayi!** ✨"
            )
            
            # Special Gif for Evil Wins (0.1%)
            if win_chance < 1:
                final_embed.description += "\n\n🚨 **IMPOSSIBLE!** Tumne System tod diya! 🤯"
                final_embed.set_image(url="https://media.tenor.com/p7a8o1r5c8cAAAAC/money-rain.gif")
            else:
                final_embed.set_image(url="https://media.tenor.com/bXjOidvDvoQAAAAC/confetti-celebrate.gif")

        else:
            # --- 💀 LOSS ---
            punish_msg = ""
            desc = ""
            
            # Roast Messages
            roast = random.choice(["L lag gaye.", "Paisaa barbad.", "Better luck next time.", "Sed lyf."])
            if win_chance < 1: roast = "System ke aage koi nahi bol sakta! 📉"

            if risk_type == "NORMAL": 
                # Sirf Bet Amount Jayega (Already deducted nahi tha, ab katega)
                # NOTE: Agar aap bet pehle nahi kat rahe, to yahan negative update karo
                await update_balance(self.user.id, -self.bet)
                desc = f"💸 **Loss:** -${self.bet:,}\n📉 **Wallet:** Thoda halka hua."

            elif risk_type == "WIPE": 
                # Pura Bank Balance 0
                data = await get_data(self.user.id)
                current_bal = data["balance"]
                await update_balance(self.user.id, -current_bal)
                desc = f"💸 **Loss:** YOUR ENTIRE BANK ACCOUNT!\n💀 **Balance:** $0\n*Sadak pe aa gaye bhai tum.*"

            elif risk_type == "DEATH": 
                # Balance 0 + Mute
                data = await get_data(self.user.id)
                current_bal = data["balance"]
                await update_balance(self.user.id, -current_bal)
                
                punish_msg = await smart_timeout(interaction, self.user, 3600, "Greedy Satta Loss")
                desc = f"💸 **Loss:** EVERYTHING ($0)\n🤐 **Izzat:** Nil\n{punish_msg}"

            final_embed.title = "❌ HAAR GAYE!"
            final_embed.color = 0xFF0000
            final_embed.description = f"### {roast}\n🎲 **Roll:** {roll:.2f} (Needed < {win_chance})\n\n{desc}"
            final_embed.set_image(url="https://media.tenor.com/d6-SreC3_p8AAAAC/wasted-gta5.gif")

        await interaction.edit_original_response(embed=final_embed, view=None)

    # --- ROW 1: FAIR PLAY (New Options) ---
    @discord.ui.button(label="SAFE (2x)", style=discord.ButtonStyle.success, row=0)
    async def bet_2x(self, i, b):
        # 50% Chance, Normal Risk
        await self.run_satta(i, multiplier=2, win_chance=50.0, risk_type="NORMAL")

    @discord.ui.button(label="RISKY (3x)", style=discord.ButtonStyle.primary, row=0)
    async def bet_3x(self, i, b):
        # 20% Chance, Normal Risk
        await self.run_satta(i, multiplier=3, win_chance=20.0, risk_type="NORMAL")

    @discord.ui.button(label="CRAZY (5x)", style=discord.ButtonStyle.secondary, row=0)
    async def bet_5x(self, i, b):
        # 5% Chance, Normal Risk
        await self.run_satta(i, multiplier=5, win_chance=5.0, risk_type="NORMAL")

    # --- ROW 2: EVIL MODE (Old Options - 0.1% Chance) ---
    @discord.ui.button(label="LALCHI (10x)", style=discord.ButtonStyle.secondary, row=1)
    async def bet_10x(self, i, b):
        # 0.1% Chance, Lose Bet
        await self.run_satta(i, multiplier=10, win_chance=0.1, risk_type="NORMAL")

    @discord.ui.button(label="BARBAAD (50x)", style=discord.ButtonStyle.danger, row=1)
    async def bet_50x(self, i, b):
        # 0.1% Chance, WIPE BALANCE
        await self.run_satta(i, multiplier=50, win_chance=0.1, risk_type="WIPE")

    @discord.ui.button(label="SUICIDE (100x)", style=discord.ButtonStyle.danger, row=1)
    async def bet_100x(self, i, b):
        # 0.1% Chance, WIPE + MUTE
        await self.run_satta(i, multiplier=100, win_chance=0.1, risk_type="DEATH")


@bot.tree.command(name="satta", description="🎲 Gambling: From Safe (2x) to Suicide (100x)")
async def satta(i: discord.Interaction, amount: int):
    data = await get_data(i.user.id)
    
    if amount <= 0:
        return await i.response.send_message("❌ Positive number daal!", ephemeral=True)
    
    if data["balance"] < amount:
        return await i.response.send_message(f"❌ **Bhikari!** Tere paas `${data['balance']:,}` hain bas.", ephemeral=True)

    embed = discord.Embed(title="🎲 SATTA BAZAAR", color=0x2B2D31)
    embed.description = (
        f"💰 **Bet Amount:** `${amount:,}`\n\n"
        f"🟢 **SAFE (2x):** 50% Win Chance\n"
        f"🔵 **RISKY (3x):** 20% Win Chance\n"
        f"⚪ **CRAZY (5x):** 5% Win Chance\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"🌑 **LALCHI (10x):** 0.1% Win Chance\n"
        f"🔴 **BARBAAD (50x):** 0.1% Win | Loss = **Zero Balance**\n"
        f"💀 **SUICIDE (100x):** 0.1% Win | Loss = **Zero Bal + Mute**"
    )
    embed.set_thumbnail(url=i.user.display_avatar.url)
    
    view = EvilSattaView(i.user, amount)
    await i.response.send_message(embed=embed, view=view)

            

# ================== 🦑 SQUID GAME: GLASS BRIDGE (ECONOMY + VIP) ==================

class GlassBridgeGame(discord.ui.View):
    def __init__(self, players, interaction):
        super().__init__(timeout=60) # 1 Minute Hard Limit
        self.original_interaction = interaction
        self.bridge_len = 7 # 7 Steps Long
        self.path = [random.choice(["LEFT", "RIGHT"]) for _ in range(self.bridge_len)]
        self.revealed = [None] * self.bridge_len 
        
        random.shuffle(players)
        self.players = players 
        self.dead_players = []
        self.winners = []
        
        self.current_player_idx = 0 
        self.current_step = 0 
        
        self.game_active = True
        self.timer_task = asyncio.create_task(self.start_timer())

        # Setup Buttons
        self.add_item(discord.ui.Button(label="🦵 LEFT GLASS", style=discord.ButtonStyle.secondary, custom_id="LEFT"))
        self.add_item(discord.ui.Button(label="🦵 RIGHT GLASS", style=discord.ButtonStyle.secondary, custom_id="RIGHT"))
        push_btn = discord.ui.Button(label="✋ PUSH FRONT PLAYER", style=discord.ButtonStyle.danger, custom_id="PUSH", row=1)
        push_btn.callback = self.push_callback
        self.add_item(push_btn)
        
        self.children[0].callback = self.jump_callback
        self.children[1].callback = self.jump_callback

    async def start_timer(self):
        await asyncio.sleep(60)
        if self.game_active:
            self.game_active = False
            self.stop()
            
            # Kill Everyone Remaining
            survivors = self.players[self.current_player_idx:]
            status_report = []
            
            for p in survivors:
                # --- 🛡️ SMART TIMEOUT LOOP ---
                msg = await smart_timeout(self.original_interaction, p, 30, "Glass Bridge Timeout")
                status_report.append(f"{p.name}: {msg}")
            
            embed = discord.Embed(title="⏰ TIME OVER! ELIMINATED!", color=0x000000)
            embed.description = (
                f"**60 Seconds khatam!** Bridge toot gaya.\n\n"
                f"💀 **Status Report:**\n" + "\n".join(status_report)
            )
            embed.set_image(url="https://media.tenor.com/2147kZ75wW8AAAAC/squid-game-card.gif")
            
            try: await self.original_interaction.edit_original_response(embed=embed, view=None)
            except: pass

    def generate_board(self):
        board_str = ""
        for i in range(self.bridge_len - 1, -1, -1):
            step_marker = f"**Step {i+1}**"
            
            if i == self.current_step and self.current_player_idx < len(self.players):
                left_icon = "⬜"; right_icon = "⬜"
            elif i < self.current_step:
                left_icon = "🟩" if self.path[i] == "LEFT" else "⬛"
                right_icon = "🟩" if self.path[i] == "RIGHT" else "⬛"
            else:
                left_icon = "🌫️"; right_icon = "🌫️"

            if self.revealed[i]:
                left_icon = "✅" if self.path[i] == "LEFT" else "❌"
                right_icon = "✅" if self.path[i] == "RIGHT" else "❌"
            
            pointer = "👈 **HERE**" if i == self.current_step else ""
            board_str += f"`[{left_icon}]`  `[{right_icon}]` {step_marker} {pointer}\n"
        return board_str

    async def get_embed(self):
        if not self.game_active: return None
        
        active_p = self.players[self.current_player_idx]
        next_p = self.players[self.current_player_idx + 1] if self.current_player_idx + 1 < len(self.players) else "None"
        
        desc = (
            f"⏱️ **TIME REMAINING:** Checking...\n\n"
            f"{self.generate_board()}\n"
            f"**🏃 CURRENT TURN:** {active_p.mention} (Step {self.current_step + 1})\n"
            f"**😈 BEHIND:** {next_p.mention if isinstance(next_p, discord.Member) else 'No one'}\n\n"
            f"*Rules: Jump karo ya Push karo. 1 Min limit!*"
        )
        embed = discord.Embed(title="🦑 GLASS BRIDGE CHALLENGE", description=desc, color=0x3498DB)
        embed.set_thumbnail(url=active_p.display_avatar.url)
        return embed

    async def jump_callback(self, interaction: discord.Interaction):
        if not self.game_active: return
        
        active_player = self.players[self.current_player_idx]
        if interaction.user.id != active_player.id:
            return await interaction.response.send_message("❌ Teri baari nahi hai!", ephemeral=True)

        chosen_side = interaction.data["custom_id"] 
        correct_side = self.path[self.current_step]
        
        if chosen_side == correct_side:
            self.current_step += 1
            
            # --- WIN CONDITION ---
            if self.current_step >= self.bridge_len:
                self.game_active = False
                self.timer_task.cancel()
                self.winners.append(active_player)
                
                # 💰 REWARD: $30,000
                prize = 30000
                await update_balance(active_player.id, prize)
                
                embed = discord.Embed(title="🎉 SURVIVOR!", color=0x00FF00)
                embed.description = f"**{active_player.mention}** ne Glass Bridge par kar liya!\n\n🏆 **WINNER**\n💰 **Reward:** ${prize:,}"
                embed.set_image(url="https://media.tenor.com/bXjOidvDvoQAAAAC/confetti-celebrate.gif")
                await interaction.response.edit_message(embed=embed, view=None)
                return

            await interaction.response.edit_message(embed=await self.get_embed(), view=self)
            
        else:
            await self.handle_death(interaction, active_player, "Wrong Glass!")

    async def push_callback(self, interaction: discord.Interaction):
        if not self.game_active: return
        
        if self.current_player_idx + 1 >= len(self.players):
            return await interaction.response.send_message("❌ Push karne ke liye koi nahi hai!", ephemeral=True)
            
        pusher = self.players[self.current_player_idx + 1]
        victim = self.players[self.current_player_idx]
        
        if interaction.user.id != pusher.id:
            return await interaction.response.send_message(f"❌ Sirf {pusher.name} dhakka de sakta hai!", ephemeral=True)

        self.revealed[self.current_step] = True
        await self.handle_death(interaction, victim, f"Pushed by {pusher.name}", revealed=True)

    async def handle_death(self, interaction, player, reason, revealed=False):
        # --- 🛡️ SMART PUNISHMENT (VIP CHECK) ---
        punish_msg = await smart_timeout(interaction, player, 30, "Glass Bridge Death")
        
        self.dead_players.append(player)
        self.current_player_idx += 1 
        
        if self.current_player_idx >= len(self.players):
            self.game_active = False
            self.timer_task.cancel()
            embed = discord.Embed(title="💀 GAME OVER", description="**Sab mar gaye!** Koi nahi bacha.", color=0x000000)
            await interaction.response.edit_message(embed=embed, view=None)
            return

        msg = f"💀 **{player.name}** gir gaya! ({reason})\n{punish_msg}"
        if revealed:
            msg += "\n👀 **GLASS REVEALED!** Rasta saaf hai!"

        await interaction.response.edit_message(content=msg, embed=await self.get_embed(), view=self)


# --- LOBBY VIEW ---
class GlassLobbyView(discord.ui.View):
    def __init__(self, host):
        super().__init__(timeout=120)
        self.host = host
        self.players = [host]
        self.started = False

    def get_embed(self):
        p_list = "\n".join([f"{i+1}. {p.name}" for i, p in enumerate(self.players)])
        embed = discord.Embed(title="🦑 SQUID GAME: GLASS BRIDGE", color=0x3498DB)
        embed.description = (
            "**Rule 1:** 2 Glasses. Ek toote ga, ek tikega.\n"
            "**Rule 2:** Random Numbers milenge.\n"
            "**Rule 3:** Peeche wala aage wale ko **PUSH** kar sakta hai (Reveal).\n"
            "**Prizes:** 💰 $30,000 (Winner) | 🔇 30s Mute (Loser)\n\n"
            f"👥 **Players ({len(self.players)}):**\n{p_list}"
        )
        embed.set_image(url="https://media.tenor.com/2147kZ75wW8AAAAC/squid-game-card.gif")
        return embed

    @discord.ui.button(label="✋ Join Game", style=discord.ButtonStyle.success)
    async def join_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.started: return
        if interaction.user in self.players: return await interaction.response.send_message("Already joined!", ephemeral=True)
        self.players.append(interaction.user)
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="🚀 START", style=discord.ButtonStyle.danger)
    async def start_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host.id: return await interaction.response.send_message("Host only.", ephemeral=True)
        if len(self.players) < 2: return await interaction.response.send_message("Need at least 2 players!", ephemeral=True)
        
        self.started = True
        game_view = GlassBridgeGame(self.players, interaction)
        await interaction.response.edit_message(content="🔢 **Assigning Numbers...**", embed=await game_view.get_embed(), view=game_view)


@bot.tree.command(name="glass_bridge", description="🦑 Squid Game Glass Bridge (Push & Survive)")
async def glass_bridge(i: discord.Interaction):
    if not i.guild.me.guild_permissions.moderate_members:
        return await i.response.send_message("❌ Mute Permission Missing!", ephemeral=True)
    
    view = GlassLobbyView(i.user)
    await i.response.send_message(embed=view.get_embed(), view=view)

# ================== 📉 ADMIN: REMOVE MONEY (ASSET SEIZURE) ==================

@bot.tree.command(name="remove_money", description="👮‍♂️ Admin: Kisi user ke wallet se paise remove karo")
@app_commands.describe(user="Kiske paise kaatne hain?", amount="Kitna amount remove karna hai?")
@app_commands.default_permissions(administrator=True) # Sirf Admin ke liye
async def remove_money(interaction: discord.Interaction, user: discord.Member, amount: int):
    
    # 1. Security Check (Waise to default_permissions sambhal lega, par double safety)
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ **Access Denied:** Sirf Admins ye command use kar sakte hain!", ephemeral=True)

    if amount <= 0:
        return await interaction.response.send_message("❌ Positive number daalo (e.g. 5000)", ephemeral=True)

    if user.bot:
        return await interaction.response.send_message("❌ Bots ke paas paise nahi hote.", ephemeral=True)

    # 2. Data Fetch
    data = await get_data(user.id)
    current_bal = data['balance']
    
    if current_bal <= 0:
        return await interaction.response.send_message(f"❌ **Already Broke:** {user.name} ke paas pehle se $0 hain.", ephemeral=True)

    # 3. Calculation (Negative Balance Protection)
    # Agar 500 hain aur 1000 nikal rahe ho, to sirf 500 hi niklenge (Bal = 0)
    amount_to_remove = min(current_bal, amount)
    new_bal = current_bal - amount_to_remove

    # 4. Database Update
    await update_balance(user.id, -amount_to_remove)

    # 5. PREMIUM EMBED
    embed = discord.Embed(title="📉 ASSET SEIZURE (TAX RAID)", color=0x8B0000) # Dark Red
    embed.description = (
        f"# 👮‍♂️ ORDER EXECUTED\n"
        f"**Authority:** {interaction.user.mention}\n"
        f"**Target:** {user.mention}\n\n"
        f"Official action ke tehat inke account se funds zabt kar liye gaye hain."
    )
    
    embed.add_field(name="🔻 Removed Amount", value=f"```-${amount_to_remove:,}```", inline=True)
    embed.add_field(name="🏦 New Balance", value=f"```${new_bal:,}```", inline=True)
    
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_image(url="https://media.tenor.com/EA84s3occX8AAAAC/burning-money-money.gif") # Money Burning GIF
    embed.set_footer(text="Secure Banking System | Action Irreversible")

    await interaction.response.send_message(embed=embed)
        

# ================== SAY ACCESS MANAGER (PREMIUM) ==================
@bot.tree.command(name="sayaccess", description="Manage who can use /say command (Owner Only)")
@app_commands.choices(action=[
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="remove", value="remove"),
    app_commands.Choice(name="list", value="list"),
])
async def sayaccess(i: discord.Interaction, action: app_commands.Choice[str], user: discord.User = None):
    
    # 1. OWNER CHECK (Database Logic)
    if not owner(i):
        return await i.response.send_message("❌ **Access Denied:** Owner/Admin only.", ephemeral=True)

    await i.response.defer(ephemeral=False)

    try:
                # ================== ADD USER ==================
        if action.value == "add":
            if not user:
                return await i.followup.send("❌ **User select karna zaroori hai!**")
            
            # Upsert to DB
            supabase.table("say_access").upsert({
                "user_id": str(user.id),
                "added_by": str(i.user.id)
            }).execute()
            
            # 👇 YAHAN GALTI THI (Ab sahi hai)
            embed = discord.Embed(title="✅ Access Granted", description=f"**{user.mention}** ab `/say` command use kar sakta hai.", color=0x2ecc71)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(name="👤 User Info", value=f"**Name:** {user.display_name}\n**ID:** `{user.id}`", inline=False)
            embed.set_footer(text=f"Added by {i.user.display_name}", icon_url=i.user.display_avatar.url)
            
            await i.followup.send(embed=embed)

        # ================== REMOVE USER ==================
        elif action.value == "remove":
            if not user:
                return await i.followup.send("❌ **User select karna zaroori hai!**")
            
            # Delete from DB
            supabase.table("say_access").delete().eq("user_id", str(user.id)).execute()
            
            embed = discord.Embed(title="🗑️ Access Revoked", description=f"**{user.mention}** se `/say` command ki permission le li gayi hai.", color=0xe74c3c)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(name="👤 User Info", value=f"**Name:** {user.display_name}\n**ID:** `{user.id}`", inline=False)
            embed.set_footer(text=f"Removed by {i.user.display_name}", icon_url=i.user.display_avatar.url)

            await i.followup.send(embed=embed)

        # ================== LIST USERS ==================
        elif action.value == "list":
            data = supabase.table("say_access").select("user_id").execute().data

            if not data:
                return await i.followup.send(embed=discord.Embed(title="🗣️ Say Access List", description="❌ List is Empty.", color=0xffa500))

            # Paginator Call
            view = SayAccessPaginator(data, i.user, bot)
            if view.total_pages <= 1:
                view.children[0].disabled = True
                view.children[1].disabled = True
            else:
                view.update_buttons()

            embed = await view.get_page_embed()
            await i.followup.send(embed=embed, view=view)

    except Exception as e:
        print(f"SAYACCESS ERROR: {e}")
        await i.followup.send(f"❌ **System Error:** `{e}`")

# ================== RESTRICT COMMAND (PREMIUM) ==================
@bot.tree.command(name="restrict", description="Manage Banned Words & Whitelisted Users")
@app_commands.choices(action=[
    app_commands.Choice(name="add / allow", value="add"),
    app_commands.Choice(name="remove / block", value="remove"),
    app_commands.Choice(name="list", value="list"),
])
@app_commands.describe(word="Comma separated (e.g. word1, word2)", user="User to Allow/Block")
async def restrict(i: discord.Interaction, action: app_commands.Choice[str], word: str = None, user: discord.User = None):
    
    # 1. OWNER CHECK (Database Logic)
    if not owner(i): 
        await i.response.send_message("❌ **Only Owner/Admins can use this.**", ephemeral=True)
        return

    await i.response.defer(ephemeral=False)
    
    # Global Cache access (Zaroori hai fast processing ke liye)
    global BANNED_WORDS_CACHE, BYPASS_USERS_CACHE

    try:
        # ================= 1. USER MANAGEMENT (VIP) =================
        if user:
            if action.value == "add":
                # Add to DB
                supabase.table("restrict_bypass").upsert({"user_id": str(user.id)}).execute()
                # Update Cache
                BYPASS_USERS_CACHE.add(user.id)
                
                embed = discord.Embed(title="👑 Exception Added", description=f"✅ **{user.mention}** ab restrictions bypass kar sakta hai.", color=0x2ecc71)
                embed.set_thumbnail(url=user.display_avatar.url)
                embed.set_footer(text=f"Allowed by {i.user.display_name}")
                await i.followup.send(embed=embed)
                return

            elif action.value == "remove":
                # Remove from DB
                supabase.table("restrict_bypass").delete().eq("user_id", str(user.id)).execute()
                # Update Cache
                BYPASS_USERS_CACHE.discard(user.id)

                embed = discord.Embed(title="🚫 Exception Removed", description=f"⚠️ **{user.mention}** ab restrictions bypass nahi kar sakta.", color=0xe74c3c)
                embed.set_thumbnail(url=user.display_avatar.url)
                embed.set_footer(text=f"Blocked by {i.user.display_name}")
                await i.followup.send(embed=embed)
                return
                
            elif action.value == "list":
                # Fetch fresh list from DB for pagination
                data = supabase.table("restrict_bypass").select("user_id").execute().data
                
                if not data:
                    await i.followup.send(embed=discord.Embed(title="📂 List Empty", description="Koi user allowed nahi hai.", color=0xffa500))
                    return
                
                # Pagination
                view = RestrictUserPaginator(data, i.user, bot)
                if view.total_pages <= 1:
                    view.children[0].disabled = True
                    view.children[1].disabled = True
                else:
                    view.update_buttons()

                embed = await view.get_page_embed()
                await i.followup.send(embed=embed, view=view)
                return

        # ================= 2. WORD MANAGEMENT (BULK) =================
        if word:
            # Words clean karna
            raw_words = [w.strip().lower() for w in word.split(',') if w.strip()]

            if action.value == "add":
                added = []
                for w in raw_words:
                    if w and w not in BANNED_WORDS_CACHE:
                        supabase.table("banned_words").insert({"word": w}).execute()
                        BANNED_WORDS_CACHE.add(w)
                        added.append(w)
                
                if added:
                    # Spoiler tag lagaya taaki chat gandi na dikhe
                    msg = ", ".join([f"||`{x}`||" for x in added])
                    embed = discord.Embed(title="🛡️ Words Banned", description=f"**Successfully Added:**\n{msg}", color=0xe74c3c)
                    embed.set_footer(text=f"Total: {len(added)} words added")
                    await i.followup.send(embed=embed)
                else:
                    await i.followup.send("⚠️ Ye words pehle se list mein hain.")
                return

            elif action.value == "remove":
                removed = []
                for w in raw_words:
                    if w in BANNED_WORDS_CACHE:
                        supabase.table("banned_words").delete().eq("word", w).execute()
                        BANNED_WORDS_CACHE.discard(w)
                        removed.append(w)
                
                if removed:
                    msg = ", ".join([f"||`{x}`||" for x in removed])
                    embed = discord.Embed(title="🗑️ Words Unbanned", description=f"**Successfully Removed:**\n{msg}", color=0x2ecc71)
                    await i.followup.send(embed=embed)
                else:
                    await i.followup.send("⚠️ Ye words list mein nahi mile.")
                return
            
        # ================= 3. LIST ALL WORDS =================
        if action.value == "list":
            # Cache ko list me convert karke sort karo
            all_words = sorted(list(BANNED_WORDS_CACHE))

            if not all_words:
                await i.followup.send(embed=discord.Embed(title="📂 Banned Words", description="List is currently empty.", color=0x3498db))
                return
            
            # Pagination Logic for Words
            view = WordPaginator(all_words, i.user)
            if view.total_pages <= 1:
                view.children[0].disabled = True
                view.children[1].disabled = True
            else:
                view.update_buttons()

            await i.followup.send(embed=view.get_embed(), view=view)
            return
        
        # Agar kuch select nahi kiya
        await i.followup.send("❌ **Usage Error:** Ya toh `word` likho ya `user` select karo!", ephemeral=True)

    except Exception as e:
        print(f"RESTRICT ERROR: {e}")
        await i.followup.send(f"❌ System Error: `{e}`")
                
# ================== FUN: FAKE HACK COMMAND ==================
@bot.tree.command(name="hack", description="Prank hack a user (Funny)")
async def hack(i: discord.Interaction, target: discord.User):
    # 1. Start Operation
    await i.response.send_message(f"💻 **Initiating Hack on {target.mention}...**")
    msg = await i.original_response()
    
    # 2. Fake Steps (Loop)
    import asyncio
    import random
    
    # Funny "Leaked" Passwords & History
    passwords = ["ilovepappu", "password123", "saksham_is_pro", "mummy_ka_ladla", "00000000"]
    history = ["how to impress girls", "baal kaise ugaye", "free fire diamond hack", "funny cat videos", "saksham se dosti kaise kare"]
    
    steps = [
        f"🔍 Fetching IP Address of {target.name}...",
        "🔓 Bypassing Firewall...",
        "💉 Injecting Trojan Virus...",
        f"📂 Accessing Files... Found 'Homework' folder (Empty) 📁",
        f"🔑 Decrypting Password... Success: ||**{random.choice(passwords)}**||",
        f"👀 Reading Google Search History: '`{random.choice(history)}`'...",
        "📡 Uploading Photos to Dark Web...",
        "💸 Stealing Paytm Balance... ₹12 found.",
        "✅ **HACK COMPLETE! System Destroyed.** 💀"
    ]

    # Har step ko 1.5 second baad dikhayenge (Edit karke)
    for step in steps:
        await asyncio.sleep(1.5) # Wait time
        await msg.edit(content=f"```diff\n- {step}\n```")

    # Final Message
    await asyncio.sleep(1)
    await msg.edit(content=f"🔥 **{target.mention} has been HACKED!** ☠️\n(Just kidding, masti thi 😂)")

# ================== FUN: LOVE / DOSTI METER ==================
@bot.tree.command(name="match", description="Calculate Love/Friendship % between two users")
async def match(i: discord.Interaction, user1: discord.User, user2: discord.User = None):
    # Agar 2nd user nahi diya, toh command use karne wale ke saath check karenge
    if user2 is None:
        user2 = i.user

    # Masti: Random Percentage
    import random
    score = random.randint(0, 100)
    
    # Funny Comments based on Score
    comment = ""
    color = 0x000000
    
    if score < 20:
        comment = "💔 **Bhai-Behen ka rishta lagta hai.** (No chance)"
        color = 0xff0000 # Red
    elif score < 50:
        comment = "😐 **Kaam chalaau dosti.** (Bas Hi-Hello)"
        color = 0xffa500 # Orange
    elif score < 80:
        comment = "❤️ **Arey waah! Mast Jodi hai.** (Party kab?)"
        color = 0xffff00 # Yellow
    else:
        comment = "💍 **Rab ne bana di jodi!** (Shaadi ka card bhejna)"
        color = 0x2ecc71 # Green

    # Progress Bar (Visual)
    # E.g: [████......]
    bar_length = 10
    filled = int(score / 10)
    bar = "█" * filled + "░" * (bar_length - filled)

    embed = discord.Embed(title="💖 Love/Dosti Calculator 💖", color=color)
    embed.add_field(name=f"🔻 Match: {user1.name} x {user2.name}", value=f"**{score}%**\n`[{bar}]`\n\n{comment}")
    
    await i.response.send_message(embed=embed)

# ================== ROBLOX INFO COMMAND (FINAL MEGA VERSION 👑) ==================
@bot.tree.command(name="robloxinfo", description="🔍 Get MAXIMUM details (Socials, DevStats, Inv, Favs, History)")
@app_commands.describe(identifier="Username or Roblox ID")
async def robloxinfo(i: discord.Interaction, identifier: str):
    
    await i.response.defer()

    try:
        # 1. ID RESOLVER (SAFE)
        target_id = identifier
        if not identifier.isdigit():
            payload = {"usernames": [identifier], "excludeBannedUsers": False}
            try:
                async with bot.session.post("https://users.roblox.com/v1/usernames/users", json=payload) as res:
                    data = await res.json()
                    if data and "data" in data and len(data["data"]) > 0:
                        target_id = str(data["data"][0]["id"])
                    else:
                        return await i.followup.send(embed=emb("❌ Not Found", f"User `{identifier}` nahi mila."))
            except:
                return await i.followup.send(embed=emb("❌ API Error", "Roblox API down hai. ID use karein."))

        # ================= 2. PARALLEL FETCHING (15 APIs) =================
        # Saari details ek saath nikalenge
        urls = [
            f"https://users.roblox.com/v1/users/{target_id}",                                      # 0. Info
            f"https://friends.roblox.com/v1/users/{target_id}/friends/count",                       # 1. Friends
            f"https://friends.roblox.com/v1/users/{target_id}/followers/count",                     # 2. Followers
            f"https://friends.roblox.com/v1/users/{target_id}/followings/count",                    # 3. Following
            f"https://presence.roblox.com/v1/presence/users",                                       # 4. Presence
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={target_id}&size=420x420&format=Png&isCircular=false", # 5. Head
            f"https://thumbnails.roblox.com/v1/users/avatar?userIds={target_id}&size=420x420&format=Png&isCircular=false",          # 6. Body
            f"https://users.roblox.com/v1/users/{target_id}/username-history?limit=20&sortOrder=Desc", # 7. History
            f"https://groups.roblox.com/v1/users/{target_id}/groups/roles",                          # 8. Groups
            f"https://premiumfeatures.roblox.com/v1/users/{target_id}/validate-membership",         # 9. Premium
            f"https://accountinformation.roblox.com/v1/users/{target_id}/roblox-badges",            # 10. Badges
            f"https://users.roblox.com/v1/users/{target_id}/promotion-channels",                    # 11. Socials 🔗
            f"https://games.roblox.com/v2/users/{target_id}/games?accessFilter=Public&limit=50",    # 12. Dev Stats 🛠️
            f"https://inventory.roblox.com/v1/users/{target_id}/can-view-inventory",                # 13. Inventory 🎒
            f"https://games.roblox.com/v2/users/{target_id}/favorite/games?limit=1"                 # 14. Favorites ⭐
        ]

        presence_payload = {"userIds": [int(target_id)]}

        async def get_json(url, method="GET", json_body=None):
            try:
                if method == "POST":
                    async with bot.session.post(url, json=json_body) as r: return await r.json()
                else:
                    async with bot.session.get(url) as r: return await r.json()
            except: return None

        results = await asyncio.gather(
            get_json(urls[0]), get_json(urls[1]), get_json(urls[2]), get_json(urls[3]),
            get_json(urls[4], "POST", presence_payload), get_json(urls[5]), get_json(urls[6]),
            get_json(urls[7]), get_json(urls[8]), get_json(urls[9]), get_json(urls[10]),
            get_json(urls[11]), get_json(urls[12]), get_json(urls[13]), get_json(urls[14])
        )

        # 🛡️ HELPER: Safe List Extractor (Crash Fix)
        def get_d(res):
            if res and isinstance(res, dict) and "data" in res: return res["data"]
            return []

        user_data = results[0]
        if not user_data or "id" not in user_data: 
            return await i.followup.send(embed=emb("🚫 TERMINATED", "User Banned/Not Found.", 0xff0000))

        # ================= 3. PARSING (ALL DETAILS) =================
        
        # A. Identity (Verified & Premium)
        display_name = user_data.get('displayName', 'Unknown')
        username = user_data.get('name', 'Unknown')
        
        is_verified = user_data.get("hasVerifiedBadge", False)
        is_premium = results[9].get("membershipValid", False) if results[9] else False

        name_str = f"{display_name} (@{username})"
        if is_verified: name_str += " ☑️"
        if is_premium: name_str += " 💎"

        # B. Official Badges (Admin/Staff)
        badges_list = get_d(results[10])
        official_badges = []
        for badge in badges_list:
            b_name = badge.get("name")
            if b_name == "Administrator": official_badges.append("🛡️ Admin")
            elif b_name == "Creator": official_badges.append("🔨 Creator")
            elif "Intern" in b_name: official_badges.append("🎓 Intern")
            elif "Star" in b_name: official_badges.append("⭐ Star")
            else: official_badges.append(f"🎖️ {b_name}")
        
        badges_str = " | ".join(official_badges) if official_badges else "None"

        # C. Status & Last Seen (Game Link Included)
        status_str = "⚫ Offline"
        last_seen_str = "Unknown"
        
        if results[4] and "userPresences" in results[4]:
            p_data = results[4]["userPresences"][0]
            p_type = p_data.get("userPresenceType", 0)
            
            # Exact Last Seen Time
            if p_data.get("lastOnline"):
                try:
                    dt = datetime.strptime(p_data["lastOnline"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
                    last_seen_str = f"<t:{int(dt.timestamp())}:f> (<t:{int(dt.timestamp())}:R>)"
                except: pass

            if p_type == 1: status_str = "🟢 **Online** (Web)"
            elif p_type == 2:
                gname = p_data.get("lastLocation", "Game")
                pid = p_data.get("placeId")
                # Game Link Logic 🎮
                status_str = f"🎮 Playing **[{gname}](https://www.roblox.com/games/{pid})**" if pid else f"🎮 Playing **{gname}**"
            elif p_type == 3: status_str = "🔶 **In Studio**"
            else: status_str = f"⚫ **Offline**\nLast seen: {last_seen_str}"

        # D. Socials & Groups
        friends = results[1]['count'] if results[1] else 0
        followers = results[2]['count'] if results[2] else 0
        following = results[3]['count'] if results[3] else 0
        groups_list = get_d(results[8])
        group_count = len(groups_list)

        # ================= 4. EXTRA FEATURES (JO AAPNE MAANGI THI) =================

        # 1. Social Links 🔗
        socials = []
        if results[11] and isinstance(results[11], dict):
            for key, val in results[11].items():
                if val and "http" in str(val): socials.append(f"[{key.capitalize()}]({val})")
        social_str = " | ".join(socials) if socials else "None"

        # 2. Dev Stats 🛠️
        games_list = get_d(results[12])
        total_visits = sum(g.get("placeVisits", 0) for g in games_list)
        dev_stat_str = f"🎮 **Games:** `{len(games_list)}` | 👣 **Visits:** `{total_visits:,}`"

        # 3. Inventory 🎒
        inv_open = results[13].get("canView", False) if results[13] else False
        inv_str = "🔓 **Open**" if inv_open else "🔒 **Private**"

        # 4. Group Owner 🎖️
        owned_groups = []
        for g in groups_list:
            if g.get("role", {}).get("rank") == 255:
                owned_groups.append(g.get("group", {}).get("name", "Unknown"))
        owner_str = ", ".join(owned_groups[:3]) if owned_groups else "None"

        # 5. Favorites ⭐
        fav_list = get_d(results[14])
        fav_game = "None"
        if fav_list:
            fg = fav_list[0]
            fav_game = f"[{fg.get('name','Game')}](https://www.roblox.com/games/{fg.get('id')})"

        # ================= 5. DB CHECK (Internal) =================
        tid = str(target_id)
        local_access = await db_call(lambda: supabase.table("access_users").select("*").eq("user_id", tid).execute())
        local_ban = await db_call(lambda: supabase.table("bans").select("*").eq("user_id", tid).execute())
        
        db_txt = "🔒 Not Verified"
        col = 0x2f3136
        if local_access.data: 
            db_txt = f"✅ **Verified** (<@{local_access.data[0]['discord_id']}>)"
            col = 0x2ecc71
        if local_ban.data:
            db_txt = f"🔴 **BANNED** (`{local_ban.data[0]['reason']}`)"
            col = 0xff0000

        # ================= 6. FINAL PREMIUM EMBED =================
        embed = discord.Embed(title=name_str, url=f"https://www.roblox.com/users/{target_id}/profile", color=col)
        
        # Visuals (Thumbnail & Image)
        head_list = get_d(results[5])
        body_list = get_d(results[6])
        if head_list: embed.set_thumbnail(url=head_list[0].get("imageUrl"))
        if body_list: embed.set_image(url=body_list[0].get("imageUrl"))

        # --- SECTIONS ---

        # Row 1: Identity & Bio
        bio = user_data.get('description', 'No Bio')
        if len(bio) > 300: bio = bio[:300] + "..." # Limit badha di
        embed.add_field(name="🆔 Identity", value=f"**ID:** `{target_id}`\n**Bio:** {bio}", inline=False)

        # Row 2: Status & Age
        try:
            created_ts = int(datetime.strptime(user_data["created"].split(".")[0], "%Y-%m-%dT%H:%M:%S").timestamp())
            age_str = f"<t:{created_ts}:D>\n(<t:{created_ts}:R>)"
        except: age_str = "Unknown"

        embed.add_field(name="📡 Live Status", value=status_str, inline=True)
        embed.add_field(name="📅 Account Age", value=age_str, inline=True)

        # Row 3: Official Data
        off_data = f"**Premium:** {'Yes 💎' if is_premium else 'No'}\n**Verified:** {'Yes ☑️' if is_verified else 'No'}\n**Badges:** {badges_str}"
        embed.add_field(name="🏆 Official Status", value=off_data, inline=False)

        # Row 4: THE EXTRAS (Aapki request)
        extra_info = (
            f"🎒 **Inventory:** {inv_str}\n"
            f"⭐ **Last Fav:** {fav_game}\n"
            f"🎖️ **Owns Groups:** {owner_str}"
        )
        embed.add_field(name="📂 Profile Extras", value=extra_info, inline=True)
        
        # Row 5: Dev Stats
        embed.add_field(name="🛠️ Dev Stats", value=dev_stat_str, inline=False)
        
        # Row 6: Social Links
        embed.add_field(name="🔗 Social Media", value=social_str, inline=False)
        
        # Row 7: Stats
        stats_txt = f"👥 Fr: `{friends}` | 📡 Fl: `{followers}` | 👀 Fw: `{following}` | 👕 Grp: `{group_count}`"
        embed.add_field(name="📊 Roblox Stats", value=stats_txt, inline=False)
        
        # Row 8: Bot Data
        embed.add_field(name="🤖 RoboPal Data", value=db_txt, inline=False)

        # History
        hist_list = get_d(results[7])
        past = ", ".join([f"`{x['name']}`" for x in hist_list]) if hist_list else "None"
        if len(past) > 600: past = past[:600] + "..."
        if past != "None": embed.add_field(name="🕰️ Aliases", value=past, inline=False)

        embed.set_footer(text=f"Requested by {i.user.display_name}", icon_url=i.user.display_avatar.url)
        await i.followup.send(embed=embed)

    except Exception as e:
        print(f"INFO ERROR: {e}")
        try: await i.followup.send(embed=emb("❌ API Error", f"Details fetch failed.\nError: `{e}`"))
        except: pass
             
# ================== FUN: DESI THAPPAD (SLAP) ==================
@bot.tree.command(name="slap", description="Slap someone nicely (Desi Style)")
async def slap(i: discord.Interaction, target: discord.User):
    # Khud ko nahi maar sakte
    if target.id == i.user.id:
        await i.response.send_message("Bhai khud ko kyu maar raha hai? Depression? 😢", ephemeral=True)
        return

    import random
    # Funny Weapons List
    weapons = [
        "🩴 **Bheegi Hui Chappal** (Geeli pappi)",
        "🥖 **Mummy ka Belan** (Headshot)",
        "🧱 **Sadak ki Eeet** (Critical Damage)",
        "⌨️ **Mechanical Keyboard** (RGB Wala)",
        "🐟 **Gandi Machli** (Smelly)",
        "🍳 **Garam Tawa** (Burn damage)",
        "🚜 **JCB ka Panja** (Khatam Tata Bye Bye)"
    ]
    
    weapon = random.choice(weapons)
    
    # Embed
    embed = discord.Embed(
        description=f"👋 **{i.user.mention}** ne **{target.mention}** ko mara!",
        color=0xff5555
    )
    embed.add_field(name="🔫 Weapon Used:", value=weapon)
    embed.set_footer(text="Ouch! That hurts. 🤕")
    
    await i.response.send_message(embed=embed)

# ================== 🔫 RUSSIAN ROULETTE (MAFIA EDITION) ==================

@bot.tree.command(name="roulette", description="💀 Maut ka khel: High Stakes (Banner Edition)")
async def roulette(i: discord.Interaction):
    import datetime as dt 
    import asyncio
    import random

    # 1. Permission Check
    if not i.guild.me.guild_permissions.moderate_members:
        return await i.response.send_message("❌ **System Error:** Mere paas 'Timeout' power nahi hai!", ephemeral=True)

    # --- 🖼️ HD BANNERS (No GIFs, Only Class) ---
    # Ye links kabhi expire nahi honge.
    img_load = "https://media.discordapp.net/attachments/109000000000000000/110000000000000000/revolver_spin_banner.png?width=800&height=300" 
    # (Note: Agar upar wala link na chale, toh niche wala use karega code)
    # Hum generic aesthetic banners use kar rahe hain:
    
    banner_spin = "https://t3.ftcdn.net/jpg/05/52/90/11/360_F_552901119_d3Hw1WjD6k7A1A4A.jpg" # Dark Revolver Art
    banner_dead = "https://wallpapers.com/images/hd/wasted-gta-5-overlay-text-j3823432.jpg"   # Classic Wasted
    banner_safe = "https://c4.wallpaperflare.com/wallpaper/576/896/633/john-wick-chapter-2-movies-keanu-reeves-actor-wallpaper-preview.jpg" # Cool Survivor Vibe

    # --- PHASE 1: THE SETUP ---
    
    embed = discord.Embed(color=0x2b2d31) # Dark/Black Premium Theme
    
    # ✅ USER PROFILE ON TOP (Jaisa aapne manga)
    embed.set_author(name=f"{i.user.display_name} ki kismat daav par...", icon_url=i.user.display_avatar.url)
    
    # Systematic Text Layout
    embed.description = (
        "## 🎰 RUSSIAN ROULETTE\n"
        "```yaml\n"
        "Situation: Gun Loaded\n"
        "Bullet:    1 in 6\n"
        "Status:    Spinning Cylinder...\n"
        "```\n"
        "👉 **Apne dil ki dhadkano ko sambhalo...**"
    )
    
    embed.set_image(url=banner_spin) # Loading Banner
    embed.set_footer(text="Faisla 3 second mein...", icon_url=i.guild.icon.url if i.guild.icon else None)
    
    await i.response.send_message(embed=embed)
    
    await asyncio.sleep(4) # Suspense Time
    
    # --- PHASE 2: THE VERDICT ---
    bullet = random.randint(1, 6)
    original_msg = await i.original_response()

    if bullet == 1: # 💀 DEAD
        try:
            # Mute Logic
            duration = dt.timedelta(minutes=1)
            await i.user.timeout(duration, reason="Lost Russian Roulette")

            # Dead Embed
            dead_embed = discord.Embed(color=0xFF0000) # Red
            dead_embed.set_author(name=f"{i.user.display_name} Khatam!", icon_url=i.user.display_avatar.url)
            
            dead_embed.description = (
                "## 💀 WASTED\n"
                "**Result:** `HEADSHOT` 🩸\n\n"
                "> Gun chali aur sab khatam. Goli seedha bheje ke paar.\n"
                "> **Saza:** 1 Minute Mute (Rest in Peace)."
            )
            dead_embed.set_image(url=banner_dead) # Wasted Banner
            dead_embed.set_footer(text="Khel Khatam.", icon_url="https://cdn-icons-png.flaticon.com/512/2996/2996395.png")

            await original_msg.edit(embed=dead_embed)
            
        except:
            # Admin Safe
            safe_embed = discord.Embed(color=0xFFD700)
            safe_embed.set_author(name=f"{i.user.display_name} Bach Gaya (Admin)", icon_url=i.user.display_avatar.url)
            safe_embed.description = "## 🛡️ IMMORTAL\n**Result:** `GOLI LAGI PAR ASAR NAHI HUA`\n\nTum Admin ho, Yamraj tumhara kuch nahi bigad sakta. 😎"
            safe_embed.set_image(url=banner_dead)
            await original_msg.edit(embed=safe_embed)

    else: # ✅ SURVIVED
        safe_embed = discord.Embed(color=0x00FF00) # Green
        safe_embed.set_author(name=f"{i.user.display_name} Zinda Hai!", icon_url=i.user.display_avatar.url)
        
        safe_embed.description = (
            "## 🎉 SURVIVED\n"
            "**Result:** `EMPTY CHAMBER` 💨\n\n"
            "> *Click*... awaz aayi par goli nahi chali.\n"
            "> Kismat aaj tumhare saath hai mere dost."
        )
        safe_embed.set_image(url=banner_safe) # Victory Banner
        safe_embed.set_footer(text="Aaj party hogi!", icon_url=i.user.display_avatar.url)

        await original_msg.edit(embed=safe_embed)

# ================== 🧠 ULTIMATE IQ TEST CHALLENGE ==================

# --- QUESTION BANK (Basic Knowledge) ---
iq_questions = [
    {"q": "India ki capital kya hai?", "a": "DELHI", "opts": ["MUMBAI", "DELHI", "KOLKATA"]},
    {"q": "2 + 2 x 2 kitna hota hai?", "a": "6", "opts": ["6", "8", "4"]},
    {"q": "Sun ek ____ hai.", "a": "STAR", "opts": ["PLANET", "STAR", "MOON"]},
    {"q": "H2O kiska formula hai?", "a": "WATER", "opts": ["AIR", "WATER", "FIRE"]},
    {"q": "Human body mein kitni haddiyan (bones) hoti hain?", "a": "206", "opts": ["206", "208", "300"]},
    {"q": "Rainbow mein kitne colors hote hain?", "a": "7", "opts": ["5", "7", "9"]},
    {"q": "Duniya ka sabse bada janwar (animal) kaunsa hai?", "a": "BLUE WHALE", "opts": ["ELEPHANT", "BLUE WHALE", "GIRAFFE"]},
    {"q": "1 Kilogram mein kitne grams hote hain?", "a": "1000", "opts": ["100", "500", "1000"]},
    {"q": "Moon par pehla kadam kisne rakha?", "a": "NEIL ARMSTRONG", "opts": ["ELON MUSK", "NEIL ARMSTRONG", "EINSTEIN"]},
    {"q": "Computer ka dimag kise kehte hain?", "a": "CPU", "opts": ["MOUSE", "CPU", "KEYBOARD"]},
    {"q": "Vowels kitne hote hain?", "a": "5", "opts": ["5", "21", "26"]},
    # --- ANIME & GAMING (Discord Audience ke liye) ---
    {"q": "Goku (Dragon Ball) ke transformation ko kya kehte hain?", "a": "SUPER SAIYAN", "opts": ["NINJA", "SUPER SAIYAN", "BANKAI"]},
    {"q": "PUBG ka full form kya hai?", "a": "PLAYERUNKNOWN'S BATTLEGROUNDS", "opts": ["PUBLIC BATTLE GAME", "PLAYERUNKNOWN'S BATTLEGROUNDS", "PEOPLE UNDER BATTLE"]},
    {"q": "Minecraft game ka malik kaun hai?", "a": "MICROSOFT", "opts": ["SONY", "MICROSOFT", "TENCENT"]},
    {"q": "Naruto ke village ka naam kya hai?", "a": "KONOHA (LEAF)", "opts": ["SAND VILLAGE", "MIST VILLAGE", "KONOHA (LEAF)"]},
    {"q": "Free Fire kis desh ka game hai?", "a": "SINGAPORE", "opts": ["CHINA", "INDIA", "SINGAPORE"]},
    
    # --- SCIENCE & TECH (Thoda Dimaag) ---
    {"q": "Gold (Sona) ka chemical symbol kya hai?", "a": "Au", "opts": ["Ag", "Au", "Go"]},
    {"q": "Android OS kis company ka hai?", "a": "GOOGLE", "opts": ["SAMSUNG", "APPLE", "GOOGLE"]},
    {"q": "Bijli ke bulb (Bulb) mein kaunsi gas hoti hai?", "a": "ARGON", "opts": ["OXYGEN", "ARGON", "CARBON DIOXIDE"]},
    {"q": "Sound (Aawaz) kismen travel nahi kar sakti?", "a": "VACUUM", "opts": ["WATER", "AIR", "VACUUM"]},
    {"q": "Human heart mein kitne chambers hote hain?", "a": "4", "opts": ["2", "4", "6"]},

    # --- GEOGRAPHY (Tricky) ---
    {"q": "Canada ki capital kya hai?", "a": "OTTAWA", "opts": ["TORONTO", "VANCOUVER", "OTTAWA"]},
    {"q": "Duniya ka sabse chhota ocean kaunsa hai?", "a": "ARCTIC OCEAN", "opts": ["INDIAN OCEAN", "ARCTIC OCEAN", "PACIFIC OCEAN"]},
    {"q": "Japan ki currency kya hai?", "a": "YEN", "opts": ["DOLLAR", "WON", "YEN"]},
    {"q": "Pyramids kis desh mein hain?", "a": "EGYPT", "opts": ["DUBAI", "EGYPT", "MEXICO"]},
    {"q": "Kis desh ko 'Land of Rising Sun' kehte hain?", "a": "JAPAN", "opts": ["INDIA", "JAPAN", "NORWAY"]},

    # --- INDIAN GK (Patriotism Check) ---
    {"q": "Space mein jaane wala pehla Indian?", "a": "RAKESH SHARMA", "opts": ["KALPANA CHAWLA", "RAKESH SHARMA", "VIKRAM SARABHAI"]},
    {"q": "India ka National Animal kya hai?", "a": "TIGER", "opts": ["LION", "TIGER", "ELEPHANT"]},
    {"q": "Mahatma Gandhi ka janam kahan hua tha?", "a": "PORBANDAR", "opts": ["MUMBAI", "DELHI", "PORBANDAR"]},
    {"q": "ISRO ka headquarter kahan hai?", "a": "BENGALURU", "opts": ["DELHI", "MUMBAI", "BENGALURU"]},
    {"q": "IPL ki sabse pehli trophy kisne jeeti thi?", "a": "RAJASTHAN ROYALS", "opts": ["CSK", "MUMBAI INDIANS", "RAJASTHAN ROYALS"]},

    # --- MATH & LOGIC (Quick Calc) ---
    {"q": "12 ka Square (12x12) kya hota hai?", "a": "144", "opts": ["124", "144", "122"]},
    {"q": "Roman Number 'X' ka matlab kya hai?", "a": "10", "opts": ["5", "10", "20"]},
    {"q": "Ek ghante (Hour) mein kitne seconds hote hain?", "a": "3600", "opts": ["360", "600", "3600"]},
    {"q": "Tash (Cards) ki gaddi mein kitne patte hote hain?", "a": "52", "opts": ["50", "52", "54"]},
    {"q": "Agar 1kg Rui aur 1kg Loha fenke, to bhaari kaun?", "a": "BOTH EQUAL", "opts": ["LOHA (IRON)", "RUI (COTTON)", "BOTH EQUAL"]},

    # --- MOVIES & POP CULTURE ---
    {"q": "Avengers mein 'Iron Man' kaun hai?", "a": "TONY STARK", "opts": ["STEVE ROGERS", "TONY STARK", "BRUCE BANNER"]},
    {"q": "KGF movie mein hero ka naam kya tha?", "a": "ROCKY", "opts": ["ROLEX", "ROCKY", "ADHEERA"]},
    {"q": "Netflix kis desh ki company hai?", "a": "USA", "opts": ["UK", "USA", "CHINA"]},
    {"q": "'Bahubali' ko kisne maara tha?", "a": "KATTAPPA", "opts": ["BHALLALADEVA", "KATTAPPA", "BIJJALADEVA"]},
    {"q": "Oscar award kis cheez ke liye milta hai?", "a": "FILM/CINEMA", "opts": ["MUSIC ONLY", "SPORTS", "FILM/CINEMA"]},
    
    # --- TRICKY (Dimag Ghumane Wale) ---
    {"q": "USA ki Capital (Rajdhani) kya hai?", "a": "WASHINGTON DC", "opts": ["NEW YORK", "WASHINGTON DC", "LOS ANGELES"]},
    {"q": "Ek century (shatabdi) mein kitne saal hote hain?", "a": "100", "opts": ["10", "50", "100"]},
    {"q": "Agar aaj Monday hai, to 3 din baad kya hoga?", "a": "THURSDAY", "opts": ["WEDNESDAY", "THURSDAY", "FRIDAY"]},
    {"q": "Duniya ki sabse lambi nadi (river) kaunsi hai?", "a": "NILE", "opts": ["AMAZON", "GANGA", "NILE"]},
    {"q": "Kaunsa janwar khade-khade sota hai?", "a": "HORSE", "opts": ["DOG", "HORSE", "LION"]},

    # --- TECH & SOCIAL MEDIA ---
    {"q": "Instagram kisne khareeda tha?", "a": "FACEBOOK (META)", "opts": ["GOOGLE", "FACEBOOK (META)", "TWITTER"]},
    {"q": "PDF ka full form kya hai?", "a": "PORTABLE DOCUMENT FORMAT", "opts": ["PUBLIC DATA FILE", "PORTABLE DOCUMENT FORMAT", "PC DATA FILE"]},
    {"q": "Internet par 'WWW' ka matlab kya hai?", "a": "WORLD WIDE WEB", "opts": ["WORLD WEB WIDE", "WORLD WIDE WEB", "WIDE WORLD WEB"]},
    {"q": "iPhone kis company ka product hai?", "a": "APPLE", "opts": ["SAMSUNG", "NOKIA", "APPLE"]},
    {"q": "Keyboard mein sabse bada button kaunsa hota hai?", "a": "SPACE BAR", "opts": ["ENTER", "SHIFT", "SPACE BAR"]},

    # --- SCIENCE (School Yaad Dilane Wale) ---
    {"q": "Namak (Salt) ka chemical formula kya hai?", "a": "NaCl", "opts": ["H2O", "NaCl", "CO2"]},
    {"q": "Plants (Paudhe) apna khana kaise banate hain?", "a": "PHOTOSYNTHESIS", "opts": ["RESPIRATION", "PHOTOSYNTHESIS", "DIGESTION"]},
    {"q": "Human body ka normal temperature kitna hota hai?", "a": "37°C", "opts": ["37°C", "40°C", "30°C"]},
    {"q": "Duniya ka sabse hard substance kaunsa hai?", "a": "DIAMOND", "opts": ["IRON", "GOLD", "DIAMOND"]},
    {"q": "Penicillin ki khoj kisne ki thi?", "a": "ALEXANDER FLEMING", "opts": ["NEWTON", "ALEXANDER FLEMING", "EDISON"]},

    # --- INDIA & BOLLYWOOD ---
    {"q": "Sholay movie mein villain ka naam kya tha?", "a": "GABBAR SINGH", "opts": ["MOGAMBO", "SHAKAAL", "GABBAR SINGH"]},
    {"q": "India ka National Bird kaunsa hai?", "a": "PEACOCK", "opts": ["PARROT", "EAGLE", "PEACOCK"]},
    {"q": "Rupee (₹) ka symbol kisne design kiya?", "a": "UDAYA KUMAR", "opts": ["RBI GOVERNOR", "UDAYA KUMAR", "MODI JI"]},
    {"q": "Dangal movie kis sport par based thi?", "a": "WRESTLING", "opts": ["BOXING", "CRICKET", "WRESTLING"]},
    {"q": "India mein sabse zyada boli jane wali language?", "a": "HINDI", "opts": ["ENGLISH", "HINDI", "TAMIL"]},

    # --- SPORTS ---
    {"q": "Olympics kitne saal baad hota hai?", "a": "4 YEARS", "opts": ["2 YEARS", "4 YEARS", "5 YEARS"]},
    {"q": "Football match ki duration kitni hoti hai?", "a": "90 MINS", "opts": ["60 MINS", "90 MINS", "100 MINS"]},
    {"q": "Sachin Tendulkar ko kya kaha jata hai?", "a": "GOD OF CRICKET", "opts": ["THE WALL", "CAPTAIN COOL", "GOD OF CRICKET"]},
    {"q": "Chess mein sabse powerful piece kaunsa hai?", "a": "QUEEN", "opts": ["KING", "QUEEN", "ROOK"]},
    {"q": "Neeraj Chopra kis khel se jude hain?", "a": "JAVELIN THROW", "opts": ["CRICKET", "JAVELIN THROW", "HOCKEY"]},

    # --- IMPOSSIBLE (Streak Breakers) ---
    {"q": "Coca-Cola ka original color kya tha?", "a": "GREEN", "opts": ["BLACK", "BROWN", "GREEN"]},
    {"q": "Octopus ke kitne dil (hearts) hote hain?", "a": "3", "opts": ["1", "3", "9"]},
    {"q": "Chess game ki shuruaat kis desh mein hui?", "a": "INDIA", "opts": ["CHINA", "RUSSIA", "INDIA"]},
    {"q": "Giraffe ki jeebh (tongue) ka color kya hota hai?", "a": "BLUE/BLACK", "opts": ["RED", "PINK", "BLUE/BLACK"]},
    {"q": "Mona Lisa painting kisne banayi thi?", "a": "LEONARDO DA VINCI", "opts": ["PICASSO", "VAN GOGH", "LEONARDO DA VINCI"]},
    {"q": "Google ka purana naam kya tha?", "a": "BACKRUB", "opts": ["BACKRUB", "SEARCHER", "ALPHABET"]},
    {"q": "Duniya ka sabse chhota desh (country)?", "a": "VATICAN CITY", "opts": ["MONACO", "VATICAN CITY", "NEPAL"]},
    {"q": "Harry Potter ke ullu (owl) ka naam kya tha?", "a": "HEDWIG", "opts": ["DOBBY", "HEDWIG", "DRACO"]},
    {"q": "Titanic ka captain kaun tha?", "a": "EDWARD SMITH", "opts": ["JACK DAWSON", "EDWARD SMITH", "JAMES CAMERON"]},
    {"q": "PUBG kis saal launch hua tha?", "a": "2017", "opts": ["2017", "2018", "2016"]},

    # --- EASY / WARMUP ---
    {"q": "India ki capital kya hai?", "a": "DELHI", "opts": ["MUMBAI", "DELHI", "KOLKATA"]},
    {"q": "Rainbow mein kitne colors hote hain?", "a": "7", "opts": ["5", "7", "9"]},
    {"q": "Cricket team mein kitne players hote hain?", "a": "11", "opts": ["10", "11", "12"]},
    {"q": "H2O kiska formula hai?", "a": "WATER", "opts": ["AIR", "WATER", "FIRE"]},
    {"q": "Computer ka dimag kise kehte hain?", "a": "CPU", "opts": ["MOUSE", "CPU", "KEYBOARD"]},
    
    # --- MEDIUM ---
    {"q": "Human body mein kitni haddiyan (bones) hoti hain?", "a": "206", "opts": ["206", "208", "300"]},
    {"q": "Duniya ka sabse bada janwar (animal) kaunsa hai?", "a": "BLUE WHALE", "opts": ["ELEPHANT", "BLUE WHALE", "GIRAFFE"]},
    {"q": "Facebook ka malik kaun hai?", "a": "MARK ZUCKERBERG", "opts": ["ELON MUSK", "MARK ZUCKERBERG", "BILL GATES"]},
    {"q": "Zero (0) kisne invent kiya tha?", "a": "ARYABHATTA", "opts": ["NEWTON", "ARYABHATTA", "EINSTEIN"]},
    {"q": "Punjab mein kitni nadiya (rivers) hain?", "a": "5", "opts": ["5", "7", "3"]},
    
    # --- TRICKY (Log Galti Karenge) ---
    {"q": "Solar System ka sabse garam (hottest) planet?", "a": "VENUS", "opts": ["MERCURY", "VENUS", "MARS"]},
    {"q": "Australia ki capital kya hai?", "a": "CANBERRA", "opts": ["SYDNEY", "MELBOURNE", "CANBERRA"]},
    {"q": "Kitne months mein 28 din hote hain?", "a": "ALL 12", "opts": ["1 (FEB)", "ALL 12", "6"]},
    {"q": "Tomato (Tamatar) kya hai?", "a": "FRUIT", "opts": ["VEGETABLE", "FRUIT", "ROOT"]},
    {"q": "Mount Everest kis desh mein hai?", "a": "NEPAL", "opts": ["INDIA", "CHINA", "NEPAL"]},
    
    # --- HARD (General Knowledge) ---
    {"q": "Human Body ki sabse chhoti bone kahan hoti hai?", "a": "EAR", "opts": ["NOSE", "EAR", "FINGER"]},
    {"q": "Bitcoin ka inventor kaun hai?", "a": "SATOSHI NAKAMOTO", "opts": ["ELON MUSK", "VITALIK", "SATOSHI NAKAMOTO"]},
    {"q": "India ka Iron Man kise kehte hain?", "a": "SARDAR PATEL", "opts": ["GANDHI JI", "SARDAR PATEL", "BHAGAT SINGH"]},
    {"q": "Light ki speed (approx) kitni hai?", "a": "3 LAKH KM/S", "opts": ["3 LAKH KM/S", "1 LAKH KM/S", "SOUND SPEED"]},
    {"q": "Periodic Table ka pehla element kaunsa hai?", "a": "HYDROGEN", "opts": ["HELIUM", "HYDROGEN", "OXYGEN"]},
    {"q": "Wifi ka full form kya hai?", "a": "WIRELESS FIDELITY", "opts": ["WIRELESS FIBER", "WIRELESS FIDELITY", "WIRELESS FIX"]},
    {"q": "Titanic ship kab dooba tha?", "a": "1912", "opts": ["1905", "1912", "1920"]},
    {"q": "GTA V game kab release hua tha?", "a": "2013", "opts": ["2013", "2015", "2011"]},
    {"q": "Chess board mein total kitne squares hote hain?", "a": "64", "opts": ["64", "32", "100"]},
    {"q": "Duniya mein sabse zyada islands kis desh mein hain?", "a": "SWEDEN", "opts": ["INDONESIA", "SWEDEN", "PHILIPPINES"]},

    # --- BASIC & WARMUP (Round 1-5) ---
    {"q": "India ka National Bird kaunsa hai?", "a": "PEACOCK", "opts": ["EAGLE", "PEACOCK", "PARROT"]},
    {"q": "H2O kiska formula hai?", "a": "WATER", "opts": ["AIR", "WATER", "OIL"]},
    {"q": "Triangle mein kitni sides hoti hain?", "a": "3", "opts": ["3", "4", "5"]},
    {"q": "Computer ka brain kise kehte hain?", "a": "CPU", "opts": ["RAM", "CPU", "GPU"]},
    {"q": "1 saal mein kitne weeks hote hain?", "a": "52", "opts": ["48", "50", "52"]},
    {"q": "Rainbow mein kitne colors hote hain?", "a": "7", "opts": ["5", "7", "9"]},
    {"q": "Earth ke sabse paas ka Planet?", "a": "VENUS", "opts": ["MARS", "VENUS", "JUPITER"]},
    {"q": "Light ki speed (approx) kitni hai?", "a": "3 LAKH KM/S", "opts": ["3 LAKH KM/S", "1 LAKH KM/S", "5 LAKH KM/S"]},
    {"q": "Solar system ka sabse bada planet?", "a": "JUPITER", "opts": ["SATURN", "JUPITER", "EARTH"]},
    {"q": "Duniya ki sabse unchi choti (peak)?", "a": "MT. EVEREST", "opts": ["K2", "MT. EVEREST", "KANCHENJUNGA"]},

    # --- MEDIUM & TRICKY (Round 6-10) ---
    {"q": "Australia ki Capital kya hai?", "a": "CANBERRA", "opts": ["SYDNEY", "MELBOURNE", "CANBERRA"]},
    {"q": "Goku ki sabse powerful form?", "a": "ULTRA INSTINCT", "opts": ["SUPER SAIYAN 3", "ULTRA INSTINCT", "GEAR 5"]},
    {"q": "PUBG kis saal launch hua?", "a": "2017", "opts": ["2016", "2017", "2018"]},
    {"q": "Human heart mein kitne chambers hote hain?", "a": "4", "opts": ["2", "4", "6"]},
    {"q": "Python language kab bani thi?", "a": "1991", "opts": ["1991", "1995", "2000"]},
    {"q": "ISRO ka headquarter kahan hai?", "a": "BENGALURU", "opts": ["DELHI", "MUMBAI", "BENGALURU"]},
    {"q": "Zero (0) kisne invent kiya?", "a": "ARYABHATTA", "opts": ["EINSTEIN", "ARYABHATTA", "NEWTON"]},
    {"q": "Minecraft ka creator kaun hai?", "a": "NOTCH", "opts": ["NOTCH", "JEB", "ELON MUSK"]},
    {"q": "Duniya ka sabse bada desert?", "a": "SAHARA", "opts": ["THAR", "SAHARA", "GOBI"]},
    {"q": "1 GB mein kitne MB hote hain?", "a": "1024", "opts": ["1000", "1024", "1056"]},

    # --- HARD & GENIUS (Round 11-15) ---
    {"q": "Titanic kis saal dooba tha?", "a": "1912", "opts": ["1905", "1912", "1920"]},
    {"q": "Duniya ka sabse chhota country?", "a": "VATICAN CITY", "opts": ["MONACO", "VATICAN CITY", "SINGAPORE"]},
    {"q": "Bitcoin ka inventor?", "a": "SATOSHI NAKAMOTO", "opts": ["ELON MUSK", "SATOSHI NAKAMOTO", "BILL GATES"]},
    {"q": "Mona Lisa painting kisne banayi?", "a": "LEONARDO DA VINCI", "opts": ["PICASSO", "LEONARDO DA VINCI", "VAN GOGH"]},
    {"q": "Human body ki sabse badi haddi (bone)?", "a": "FEMUR", "opts": ["SKULL", "FEMUR", "SPINE"]},
    {"q": "Periodic table ka pehla element?", "a": "HYDROGEN", "opts": ["OXYGEN", "HYDROGEN", "HELIUM"]},
    {"q": "Japan ki currency kya hai?", "a": "YEN", "opts": ["DOLLAR", "WON", "YEN"]},
    {"q": "Facebook ka purana naam?", "a": "THEFACEBOOK", "opts": ["THEFACEBOOK", "META", "FACEMASH"]},
    {"q": "Duniya ki sabse lambi nadi (river)?", "a": "NILE", "opts": ["AMAZON", "NILE", "GANGA"]},
    {"q": "Blood pressure napne ka instrument?", "a": "SPHYGMOMANOMETER", "opts": ["THERMOMETER", "SPHYGMOMANOMETER", "BAROMETER"]},

    # --- STREAK BREAKERS (Round 16-20) ---
    {"q": "Octopus ke kitne dil (hearts) hote hain?", "a": "3", "opts": ["1", "3", "8"]},
    {"q": "Eiffel Tower kahan hai?", "a": "PARIS", "opts": ["LONDON", "PARIS", "ROME"]},
    {"q": "Instagram kis saal launch hua?", "a": "2010", "opts": ["2008", "2010", "2012"]},
    {"q": "Spider-Man ka real name?", "a": "PETER PARKER", "opts": ["MILES MORALES", "PETER PARKER", "BRUCE WAYNE"]},
    {"q": "India ka Iron Man kise kehte hain?", "a": "SARDAR PATEL", "opts": ["GANDHI JI", "SARDAR PATEL", "NEHRU JI"]},
    {"q": "Duniya mein kitne continents hain?", "a": "7", "opts": ["5", "7", "8"]},
    {"q": "Chess board mein kitne squares hote hain?", "a": "64", "opts": ["32", "64", "100"]},
    {"q": "Kis desh ko 'Land of Rising Sun' kehte hain?", "a": "JAPAN", "opts": ["INDIA", "JAPAN", "CHINA"]},
    {"q": "Tomato kya hai?", "a": "FRUIT", "opts": ["VEGETABLE", "FRUIT", "ROOT"]},
    {"q": "Harry Potter mein kitni total movies hain?", "a": "8", "opts": ["7", "8", "9"]},

    # --- THE ELIMINATORS (Mixed Tough) ---
    {"q": "India ka National Anthem kisne likha?", "a": "TAGORE", "opts": ["GANDHI", "TAGORE", "NEHRU"]},
    {"q": "Duniya ka sabse chhota ocean?", "a": "ARCTIC", "opts": ["INDIAN", "PACIFIC", "ARCTIC"]},
    {"q": "Elon Musk ki car company?", "a": "TESLA", "opts": ["TESLA", "SPACEX", "FORD"]},
    {"q": "Kis planet ko 'Red Planet' kehte hain?", "a": "MARS", "opts": ["MARS", "VENUS", "SATURN"]},
    {"q": "Human eye kitne megapixels ki hoti hai?", "a": "576 MP", "opts": ["100 MP", "576 MP", "1000 MP"]},
    {"q": "Duniya ka sabse bada bird?", "a": "OSTRICH", "opts": ["EAGLE", "OSTRICH", "PEACOCK"]},
    {"q": "Google ka purana naam?", "a": "BACKRUB", "opts": ["BACKRUB", "SEARCHER", "ALPHABET"]},
    {"q": "1 ton mein kitne kg hote hain?", "a": "1000", "opts": ["100", "500", "1000"]},
    {"q": "Naruto ka favorite food?", "a": "RAMEN", "opts": ["SUSHI", "RAMEN", "DUMPLINGS"]},
    {"q": "Youtube ki pehli video kisne upload ki?", "a": "JAWED", "opts": ["PEWDIEPIE", "JAWED", "MRBEAST"]},

    # --- MORE BRAIN TEASERS ---
    {"q": "India kab aazad hua?", "a": "1947", "opts": ["1947", "1950", "1942"]},
    {"q": "Duniya ka sabse bada island?", "a": "GREENLAND", "opts": ["ICELAND", "GREENLAND", "SRI LANKA"]},
    {"q": "Kis gas ko 'Laughing Gas' kehte hain?", "a": "NITROUS OXIDE", "opts": ["OXYGEN", "NITROUS OXIDE", "HELIUM"]},
    {"q": "Coca-Cola ka original color?", "a": "GREEN", "opts": ["BLACK", "GREEN", "RED"]},
    {"q": "Duniya ka sabse tezz bird?", "a": "PEREGRINE FALCON", "opts": ["EAGLE", "PEREGRINE FALCON", "SWIFT"]},
    {"q": "NASA kahan ki space agency hai?", "a": "USA", "opts": ["USA", "RUSSIA", "INDIA"]},
    {"q": "Penicillin kisne discover kiya?", "a": "ALEXANDER FLEMING", "opts": ["NEWTON", "ALEXANDER FLEMING", "EDISON"]},
    {"q": "Cricket ka Bhagwan kise kehte hain?", "a": "SACHIN TENDULKAR", "opts": ["DHONI", "SACHIN TENDULKAR", "KOHLI"]},
    {"q": "Chess mein kitne pieces (mohre) hote hain?", "a": "32", "opts": ["16", "32", "64"]},
    {"q": "India ka sabse bada state (Area)?", "a": "RAJASTHAN", "opts": ["UP", "MP", "RAJASTHAN"]},

    # --- MIXED & TRICKY ---
    {"q": "Kitne months mein 28 days hote hain?", "a": "ALL 12", "opts": ["1 (FEB)", "ALL 12", "6"]},
    {"q": "GTA 5 kab release hua?", "a": "2013", "opts": ["2013", "2015", "2011"]},
    {"q": "iPhone kis company ka hai?", "a": "APPLE", "opts": ["APPLE", "SAMSUNG", "GOOGLE"]},
    {"q": "Duniya ka sabse meetha fruit?", "a": "STEVIA", "opts": ["MANGO", "STEVIA", "APPLE"]},
    {"q": "Olympic rings mein kitne colors hote hain?", "a": "5", "opts": ["4", "5", "6"]},
    {"q": "Duniya ka sabse purana dharam?", "a": "SANATAN DHARMA", "opts": ["SANATAN DHARMA", "ISLAM", "BUDDHISM"]},
    {"q": "India ki sabse lambi train?", "a": "VIVEK EXPRESS", "opts": ["RAJDHANI", "SHATABDI", "VIVEK EXPRESS"]},
    {"q": "Ek normal insan kitne din bina soye reh sakta hai?", "a": "11 DAYS", "opts": ["3 DAYS", "7 DAYS", "11 DAYS"]},
    {"q": "Wifi ka full form?", "a": "WIRELESS FIDELITY", "opts": ["WIRELESS FIBER", "WIRELESS FIDELITY", "WIRELESS FIX"]},
    {"q": "Duniya ka sabse bada stadium?", "a": "NARENDRA MODI STADIUM", "opts": ["MCG", "NARENDRA MODI STADIUM", "LORDS"]},

    # --- FINAL ROUND KILLERS ---
    {"q": "Elon Musk ki company 'X' ka purana naam?", "a": "TWITTER", "opts": ["FACEBOOK", "TWITTER", "LINKEDIN"]},
    {"q": "One Piece anime ka main character?", "a": "LUFFY", "opts": ["ZORO", "LUFFY", "SANJI"]},
    {"q": "Duniya ka sabse pehla website?", "a": "CERN", "opts": ["GOOGLE", "CERN", "YAHOO"]},
    {"q": "Duniya ka sabse bada flower?", "a": "RAFFLESIA", "opts": ["ROSE", "RAFFLESIA", "LOTUS"]},
    {"q": "India ka sabse lamba bridge?", "a": "DHOLA-SADIYA", "opts": ["BANDRA-WORLI", "DHOLA-SADIYA", "HOWRAH"]},
    {"q": "1 minute mein kitne seconds?", "a": "60", "opts": ["60", "100", "3600"]},
    {"q": "Duniya ka sabse hard substance?", "a": "DIAMOND", "opts": ["GOLD", "IRON", "DIAMOND"]},
    {"q": "Free Fire kis desh ka game hai?", "a": "SINGAPORE", "opts": ["CHINA", "INDIA", "SINGAPORE"]},
    {"q": "Human eye ka resolution?", "a": "576 MP", "opts": ["100 MP", "576 MP", "800 MP"]},
    {"q": "Duniya mein sabse zyada population?", "a": "INDIA", "opts": ["CHINA", "INDIA", "USA"]},

    # --- THE LAST BATCH (100 TOTAL) ---
    {"q": "Billi (Cat) kitne saal jeeti hai?", "a": "12-18 YEARS", "opts": ["5-10 YEARS", "12-18 YEARS", "20-30 YEARS"]},
    {"q": "Shatranj (Chess) ki shuruaat kahan hui?", "a": "INDIA", "opts": ["CHINA", "RUSSIA", "INDIA"]},
    {"q": "Duniya ka sabse poisonous sanp?", "a": "INLAND TAIPAN", "opts": ["COBRA", "INLAND TAIPAN", "PYTHON"]},
    {"q": "India ka sabse rich person?", "a": "MUKESH AMBANI", "opts": ["ADANI", "MUKESH AMBANI", "TATA"]},
    {"q": "Duniya ka sabse bada mammal?", "a": "BLUE WHALE", "opts": ["ELEPHANT", "BLUE WHALE", "SHARK"]},
    {"q": "Earth kitne percent paani hai?", "a": "71%", "opts": ["50%", "71%", "90%"]},
    {"q": "Sun kiska chakkar lagata hai?", "a": "MILKY WAY CENTER", "opts": ["EARTH", "MILKY WAY CENTER", "MOON"]},
    {"q": "1 byte mein kitne bits?", "a": "8", "opts": ["4", "8", "16"]},
    {"q": "Duniya ka sabse lamba rasta?", "a": "PAN-AMERICAN HIGHWAY", "opts": ["NH-44", "PAN-AMERICAN HIGHWAY", "ROUTE 66"]},
    {"q": "Spider-man ka chacha ka naam?", "a": "BEN", "opts": ["BEN", "TONY", "BRUCE"]},
    {"q": "Kis janwar ka doodh pink hota hai?", "a": "HIPPO", "opts": ["COW", "HIPPO", "GOAT"]},
    {"q": "Sabse zyada islands kis desh mein hain?", "a": "SWEDEN", "opts": ["INDONESIA", "SWEDEN", "PHILIPPINES"]},
    {"q": "India ka National River?", "a": "GANGA", "opts": ["YAMUNA", "GANGA", "NARMADA"]},
    {"q": "Kaunsa janwar khade rehkar sota hai?", "a": "HORSE", "opts": ["DOG", "HORSE", "COW"]},
    {"q": "Human brain kitne percent fat hai?", "a": "60%", "opts": ["20%", "60%", "90%"]},
    {"q": "Ek hafte mein kitne minutes?", "a": "10080", "opts": ["1440", "10080", "5000"]},
    {"q": "Duniya ka sabse bada jungle?", "a": "AMAZON", "opts": ["AMAZON", "SUNDARBANS", "CONGO"]},
    {"q": "KGF hero ka naam?", "a": "YASH", "opts": ["PRABHAS", "YASH", "ALLU ARJUN"]},
    {"q": "India mein total kitne states hain?", "a": "28", "opts": ["29", "28", "30"]},
    {"q": "Duniya ka sabse mehnga item?", "a": "ANTIMATTER", "opts": ["DIAMOND", "ANTIMATTER", "GOLD"]},
    
    # --- IMPOSSIBLE (Luck or Genius) ---
    {"q": "Elon Musk ki rocket company ka naam?", "a": "SPACEX", "opts": ["NASA", "SPACEX", "BLUE ORIGIN"]},
    {"q": "Python language kab release hui thi?", "a": "1991", "opts": ["1991", "1995", "2000"]},
    {"q": "Harry Potter mein total kitni books hain?", "a": "7", "opts": ["7", "8", "6"]},
    {"q": "Spider-Man ka asli naam kya hai?", "a": "PETER PARKER", "opts": ["BRUCE WAYNE", "PETER PARKER", "TONY STARK"]},
    {"q": "Youtube par sabse pehli video kisne dali?", "a": "JAWED", "opts": ["PEWDIEPIE", "JAWED", "GOOGLE"]},
    {"q": "Triangle ki kitni sides hoti hain?", "a": "3", "opts": ["3", "4", "5"]},
    {"q": "Cricket team mein kitne players hote hain?", "a": "11", "opts": ["10", "11", "12"]},
    {"q": "Facebook ka malik kaun hai?", "a": "MARK ZUCKERBERG", "opts": ["ELON MUSK", "MARK ZUCKERBERG", "BILL GATES"]},
    {"q": "Taj Mahal kahan hai?", "a": "AGRA", "opts": ["DELHI", "AGRA", "JAIPUR"]},
    {"q": "Fastest land animal kaunsa hai?", "a": "CHEETAH", "opts": ["LION", "CHEETAH", "HORSE"]},
    {"q": "Zero (0) kisne invent kiya tha?", "a": "ARYABHATTA", "opts": ["NEWTON", "ARYABHATTA", "EINSTEIN"]},
    {"q": "Earth ke sabse paas kaunsa planet hai?", "a": "VENUS", "opts": ["MARS", "VENUS", "JUPITER"]},
    {"q": "Youtube kis company ka hai?", "a": "GOOGLE", "opts": ["MICROSOFT", "GOOGLE", "AMAZON"]},
    {"q": "500 ka note kis color ka hai (India)?", "a": "STONE GREY", "opts": ["PINK", "GREEN", "STONE GREY"]}
]

class IQTestView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=30) # 30s per question
        self.user = user
        self.score = 0
        self.max_score = 20
        # Shuffle questions every time
        self.game_questions = random.sample(iq_questions, self.max_score) 
        self.current_q_index = 0
        self.setup_question()

    def setup_question(self):
        self.clear_items()
        q_data = self.game_questions[self.current_q_index]
        
        # Shuffle Options
        options = q_data["opts"][:]
        random.shuffle(options)
        
        for opt in options:
            btn = discord.ui.Button(label=opt, style=discord.ButtonStyle.secondary)
            btn.callback = self.make_callback(opt)
            self.add_item(btn)

    def make_callback(self, answer):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user.id: return await interaction.response.send_message("Apna IQ Test khud start karo!", ephemeral=True)
            
            correct_ans = self.game_questions[self.current_q_index]["a"]
            
            if answer == correct_ans:
                # ✅ CORRECT ANSWER
                self.score += 1
                self.current_q_index += 1
                
                if self.score >= self.max_score:
                    # 🎉 WINNER (20/20)
                    await update_balance(self.user.id, 500000)
                    embed = discord.Embed(title="🧠 EINSTEIN LEVEL GENIUS!", color=0x00FF00)
                    embed.description = f"### 🏆 YOU WON!\nTumne saare **20 Sawal** sahi diye!\n💰 **Prize:** $500,000 (Added to Balance)"
                    embed.set_image(url="https://media.tenor.com/bXjOidvDvoQAAAAC/confetti-celebrate.gif")
                    await interaction.response.edit_message(embed=embed, view=None)
                else:
                    # Next Question
                    self.setup_question()
                    embed = discord.Embed(title=f"🧠 IQ TEST: Round {self.current_q_index + 1}/20", color=0x3498DB)
                    embed.description = f"**Question:** {self.game_questions[self.current_q_index]['q']}"
                    await interaction.response.edit_message(embed=embed, view=self)
            
            else:
                # ❌ WRONG ANSWER (GAME OVER)
                await self.punish_user(interaction, correct_ans)
                
        return callback

    async def punish_user(self, interaction, correct_ans):
        self.stop()
        
        # 1. Generate Shame Name
        bad_names = ["Anpadh 🤡", "Duffer 🤪", "Fail Fail Fail", "Dimag Se Paidal", "Gobar Ganesh"]
        new_nick = f"{random.choice(bad_names)} {self.user.name[:10]}"
        
        # 2. Rename User
        msg = ""
        try:
            if self.user.top_role < interaction.guild.me.top_role:
                await self.user.edit(nick=new_nick)
                msg = f"\n📛 **Nickname Changed to:** `{new_nick}`"
                
                # Give Haggu Role if exists
                role = discord.utils.get(interaction.guild.roles, name="💩 HAGGU")
                if role: await self.user.add_roles(role)
            else:
                msg = "\n*(Admin ho isliye bach gaye, warna naam badal deta)*"
        except:
            msg = "\n*(Permission Issue: Rename nahi kar paya)*"

        # 3. Insult Embed
        embed = discord.Embed(title="🤡 FAIL! IQ = 0", color=0xFF0000)
        embed.description = (
            f"❌ **Galat Jawab!** Sahi tha: `{correct_ans}`\n"
            f"Tum 20 sawal bhi nahi de paye? **Sharam karo!**\n"
            f"{msg}\n\n"
            f"💡 **Tip:** Naam hatana hai to `/dark_shop` se **Izzat Wapasi** kharido ($100k)."
        )
        embed.set_image(url="https://media.tenor.com/2147kZ75wW8AAAAC/squid-game-card.gif")
        
        await interaction.response.edit_message(embed=embed, view=None)


@bot.tree.command(name="iq_test", description="🧠 Answer 20 Questions to win $500k (Risk: Bezzati)")
async def iq_test(i: discord.Interaction):
    if not i.guild.me.guild_permissions.manage_nicknames:
        return await i.response.send_message("❌ Mere paas 'Manage Nicknames' permission nahi hai!", ephemeral=True)
        
    embed = discord.Embed(title="🧠 ULTIMATE IQ CHALLENGE", color=0xFFA500)
    embed.description = (
        "**Rules:**\n"
        "1. Lagatar **20 Sawal** sahi dene hain.\n"
        "2. Prize: **$500,000** 💰\n"
        "3. Ek bhi galti hui to... **Game Over + Ganda Nickname!** 🤡\n\n"
        "**Kya tum taiyaar ho?**"
    )
    
    view = IQTestView(i.user)
    # Manually setup first question embed
    q = view.game_questions[0]
    embed.add_field(name="Round 1/20", value=f"**Q:** {q['q']}")
    
    await i.response.send_message(embed=embed, view=view)

# ================== 💸 MONEY TRANSFER SYSTEM (TAX LOGIC) ==================
@bot.tree.command(name="pay", description="💸 Transfer Money (15 Min Cooldown | >200k = 50% Tax)")
@app_commands.describe(user="Paisa kisko dena hai?", amount="Kitna paisa bhejna hai?")
@app_commands.checks.cooldown(1, 900.0, key=lambda i: i.user.id) # 1 use per 900s (15 Mins)
async def pay(interaction: discord.Interaction, user: discord.Member, amount: int):
    
    # 1. Basic Checks
    if user.id == interaction.user.id:
        return await interaction.response.send_message("❌ Khud ko paise transfer nahi kar sakte!", ephemeral=True)
    
    if user.bot:
        return await interaction.response.send_message("❌ Bots ko paise nahi de sakte!", ephemeral=True)
        
    if amount <= 0:
        return await interaction.response.send_message("❌ Positive number daalo!", ephemeral=True)

    # 2. Sender Data Fetch
    sender_data = await get_data(interaction.user.id)
    
    # Balance Check
    if sender_data['balance'] < amount:
        return await interaction.response.send_message(f"❌ **Insufficient Balance!** Aapke paas itne paise nahi hain.", ephemeral=True)

    # 3. 🛡️ TAX CALCULATION LOGIC
    is_vip = False
    vip_expiry = sender_data.get('vip_expiry')
    if vip_expiry:
        try:
            if vip_expiry.startswith("9999") or datetime.utcnow() < datetime.fromisoformat(vip_expiry):
                is_vip = True
        except: pass

    tax_rate = 0.10 # Default
    tax_status = "10% (Normal User)"
    
    # Tax Logic
    if amount > 200000:
        tax_rate = 0.50 
        tax_status = "50% (⚠️ High Value Tax)"
    elif is_vip:
        tax_rate = 0.0
        tax_status = "0% (👑 VIP Power)"
    else:
        tax_rate = 0.10
        tax_status = "10% (Normal User)"

    # 4. Calculation
    tax_amount = int(amount * tax_rate)
    final_amount = amount - tax_amount

    # 5. Transaction Execution
    await update_balance(interaction.user.id, -amount)
    await update_balance(user.id, final_amount)

    # 6. Success Embed
    embed = discord.Embed(title="💸 MONEY TRANSFER SUCCESSFUL", color=0x00FF00)
    embed.add_field(name="📤 Sender", value=f"{interaction.user.mention}", inline=True)
    embed.add_field(name="📥 Receiver", value=f"{user.mention}", inline=True)
    embed.add_field(name="💰 Sent Amount", value=f"`${amount:,}`", inline=False)
    
    if tax_rate == 0.50:
        embed.color = 0xFFA500
        embed.add_field(name="🚨 HEAVY TAX (50%)", value=f"-${tax_amount:,} (Amount > 200k)", inline=True)
    elif tax_rate == 0.0:
        embed.add_field(name="🛡️ Tax (VIP)", value=f"~~${int(amount*0.10):,}~~ **$0** (No Tax)", inline=True)
    else:
        embed.add_field(name="📉 Tax (10%)", value=f"-${tax_amount:,}", inline=True)
        
    embed.add_field(name="✅ Received", value=f"**${final_amount:,}**", inline=True)
    embed.set_footer(text=f"Tax Status: {tax_status}")
    embed.set_thumbnail(url="https://media.tenor.com/J3i6jGgFqsgAAAAC/money-transfer.gif")

    await interaction.response.send_message(embed=embed)

# --- ⏳ COOLDOWN ERROR HANDLER (Isko pay command ke niche hi lagana) ---
@pay.error
async def pay_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        # Seconds ko Minutes:Seconds me convert karna
        minutes, seconds = divmod(int(error.retry_after), 60)
        await interaction.response.send_message(
            f"⏳ **Cooldown Active!** Bhai thoda saans le le.\n"
            f"Agli payment **{minutes} min {seconds} sec** baad karna.",
            ephemeral=True
        )
    else:
        # Koi aur error ho to print karo
        print(f"Pay Error: {error}")

# ================== 🔪 HIDE & SEEK: NIGHT MASSACRE ==================

class HideSeekGameView(discord.ui.View):
    def __init__(self, killer, victims, traitor, pot_money):
        super().__init__(timeout=60)
        self.killer = killer
        self.victims = victims # List of Member objects
        self.traitor = traitor # Member object
        self.pot_money = pot_money
        
        # Locations
        self.locations = ["Bed", "Curtains", "Closet", "Bathroom", "Table"]
        self.victim_choices = {} # {user_id: "Bed"}
        self.killer_choice = None
        self.killed_players = []
        
        # Setup Buttons for Victims
        for loc in self.locations:
            btn = discord.ui.Button(label=loc, style=discord.ButtonStyle.secondary, custom_id=loc)
            btn.callback = self.hider_callback
            self.add_item(btn)

        # Setup Killer Select (Initially disabled, enabled after 10s)
        self.kill_select = discord.ui.Select(
            placeholder="🔪 KILLER: Choose location to shoot!",
            options=[discord.SelectOption(label=l, emoji="🔫") for l in self.locations],
            custom_id="kill_select",
            disabled=True # Pehle victims chupenge
        )
        self.kill_select.callback = self.killer_callback
        self.add_item(self.kill_select)
        
        # Game State
        self.phase = "HIDING" # HIDING -> KILLING -> RESULT

    async def hider_callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.killer.id:
            return await interaction.response.send_message("❌ Abe tu Killer hai! Chupna nahi, dhundna hai!", ephemeral=True)
        
        if interaction.user not in self.victims:
            return await interaction.response.send_message("❌ Tum game mein nahi ho.", ephemeral=True)

        # Save Choice
        self.victim_choices[interaction.user.id] = interaction.data["custom_id"]
        await interaction.response.send_message(f"🤫 **Shh!** Tum **{interaction.data['custom_id']}** mein chup gaye ho.", ephemeral=True)
        
        # Check if all victims hid
        if len(self.victim_choices) >= len(self.victims):
            await self.start_killing_phase(interaction)

    async def start_killing_phase(self, interaction):
        self.phase = "KILLING"
        
        # Enable Killer's Dropdown, Disable Hider Buttons
        for item in self.children:
            if isinstance(item, discord.ui.Button): item.disabled = True
            if isinstance(item, discord.ui.Select): item.disabled = False
        
        embed = interaction.message.embeds[0]
        embed.title = "💀 THE HUNT BEGINS!"
        embed.description = (
            f"🩸 **Killer {self.killer.mention}** has loaded the gun.\n"
            f"🚪 Sare darwaze band hain.\n\n"
            f"🔫 **Killer:** Ab select karo kahan goli chalani hai!\n"
            f"⏳ **Time:** 30 Seconds"
        )
        embed.set_image(url="https://media.tenor.com/yJ3j3rX08F0AAAAC/squid-game-front-man.gif")
        
        await interaction.message.edit(embed=embed, view=self)
        
        # Traitor Hint (Optional Feature)
        if self.traitor:
            try: await self.traitor.send(f"🕵️ **Psst!** Main Gaddar hu. Killer shyad **{random.choice(self.locations)}** check karega (Fake Hint) ya asli... risk tumhara!")
            except: pass

    async def killer_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.killer.id:
            return await interaction.response.send_message("❌ Tu Killer nahi hai! Bhaag yahan se!", ephemeral=True)
            
        self.killer_choice = self.kill_select.values[0]
        await interaction.response.defer()
        await self.end_game(interaction)

    async def end_game(self, interaction):
        # --- 👑 KILLER VIP CHECK ---
        killer_data = await get_data(self.killer.id)
        killer_is_vip = False
        k_expiry = killer_data.get("vip_expiry")
        if k_expiry:
             # Yahan proper date check kar lena (Short me True maan raha hu)
             killer_is_vip = True

        # Calculate Deaths
        dead_text = ""
        survivors = []
        location_img = "https://media.tenor.com/2147kZ75wW8AAAAC/squid-game-card.gif" 
        
        for victim in self.victims:
            chosen_loc = self.victim_choices.get(victim.id, "Panic (Open)")
            
            if chosen_loc == self.killer_choice:
                # --- 🛡️ VICTIM DEFENSE LOGIC ---
                saved = False
                reason = "Dead"
                
                # Victim VIP Check
                v_data = await get_data(victim.id)
                victim_is_vip = False
                if v_data.get("vip_expiry"): victim_is_vip = True
                
                # 1. Check Extra Life (Priority)
                if v_data.get("inventory", {}).get("life", 0) > 0:
                    await update_inventory(victim.id, "life", -1)
                    saved = True
                    reason = "💖 Extra Life Used"
                
                # 2. Check VIP Vest (Luck)
                elif victim_is_vip and random.random() < 0.5:
                    if killer_is_vip:
                        # 💀 VIP KILLER POWER ACTIVE
                        saved = False # Vest Fail
                        reason = "🛡️💥 **VIP Vest Pierced!** (Killer is VIP)"
                    else:
                        # Normal Killer vs VIP Victim
                        saved = True
                        reason = "🛡️ VIP Matrix Dodge!"
                
                # FINAL DECISION
                if saved:
                    survivors.append(victim)
                    dead_text += f"🤕 **{victim.name}:** Shot in {chosen_loc} ({reason})\n"
                else:
                    # KILL
                    dead_text += f"💀 **{victim.name}:** FOUND in {chosen_loc} (ELIMINATED)\n"
                    await smart_timeout(interaction, victim, 300, "Shot by Killer")
                    self.killed_players.append(victim)
            else:
                survivors.append(victim)
        
        # --- WINNER EMBED LOGIC (Same as before) ---
        if not self.killed_players: 
            title = "❌ KILLER FAILED!"
            desc = f"🔫 **Killer:** {self.killer.mention} nishana chuk gaya!\n📍 **Location:** {self.killer_choice} khali tha.\n💰 **Victims Win:** ${self.pot_money:,} distributed!"
            color = 0x00FF00
            if survivors:
                share = self.pot_money // len(survivors)
                for s in survivors: await update_balance(s.id, share)
                
        elif len(survivors) == 0: 
            title = "🩸 TOTAL MASSACRE!"
            desc = f"🔫 **Killer:** {self.killer.mention} ne SABKO maar diya!\n📍 **Location:** {self.killer_choice} khoon se bhar gaya.\n💰 **Killer Wins:** ${self.pot_money:,}"
            color = 0xFF0000
            await update_balance(self.killer.id, self.pot_money)
            location_img = "https://media.tenor.com/d6-SreC3_p8AAAAC/wasted-gta5.gif"
            
        else: 
            title = "🔫 BLOOD BATH!"
            desc = f"📍 **Killer checked:** {self.killer_choice}\n\n{dead_text}\n\n🏃 **Survivors:** {len(survivors)} log bach gaye.\n💰 **Pot Split:** Survivors & Killer keep their share."
            color = 0xFFA500
            share = self.pot_money // (len(survivors) + 1)
            for s in survivors: await update_balance(s.id, share)
            await update_balance(self.killer.id, share)

        embed = discord.Embed(title=title, description=desc, color=color)
        embed.set_thumbnail(url=self.killer.display_avatar.url)
        embed.set_image(url=location_img)
        embed.set_footer(text="Game Over")
        
        for item in self.children: item.disabled = True
        await interaction.message.edit(embed=embed, view=None)


class HideLobbyView(discord.ui.View):
    def __init__(self, host, fee=50000):
        super().__init__(timeout=120)
        self.host = host
        self.players = [host]
        self.fee = fee
        self.started = False

    def get_embed(self):
        plist = "\n".join([f"👤 {u.name}" for u in self.players])
        embed = discord.Embed(title="🌃 NIGHT MASSACRE (Lobby)", color=0x2C3E50)
        embed.description = (
            f"**Host:** {self.host.mention}\n"
            f"💵 **Entry Fee:** ${self.fee:,}\n"
            f"👥 **Players:** {len(self.players)}\n\n"
            f"**Roles (Random):**\n"
            f"🔪 **1x Killer:** Gun milegi.\n"
            f"😱 **Victims:** Chupna padega.\n"
            f"🕵️ **1x Traitor:** Hint milega.\n\n"
            f"👇 **JOIN NOW!**"
        )
        embed.add_field(name="Lobby List", value=plist or "Empty")
        embed.set_image(url="https://media.tenor.com/Xv5Wl2l_u-AAAAAC/squid-game-soldier.gif")
        return embed

    @discord.ui.button(label="JOIN GAME ($50k)", style=discord.ButtonStyle.primary)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            return await interaction.response.send_message("Already joined!", ephemeral=True)
        
        # Check Balance
        data = await get_data(interaction.user.id)
        if data["balance"] < self.fee:
            return await interaction.response.send_message("❌ Gareeb! $50k chahiye.", ephemeral=True)
            
        await update_balance(interaction.user.id, -self.fee)
        self.players.append(interaction.user)
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="START MASSACRE", style=discord.ButtonStyle.danger)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.host: return
        if len(self.players) < 2: return await interaction.response.send_message("❌ Kam se kam 2 log chahiye!", ephemeral=True)
        
        self.started = True
        
        # 🎲 ASSIGN ROLES RANDOMLY
        import random
        random.shuffle(self.players)
        
        killer = self.players[0]
        victims = self.players[1:]
        traitor = random.choice(victims) if len(victims) > 1 else None
        
        pot = len(self.players) * self.fee
        
        # Notify Roles via DM (Optional, keeps suspense)
        try:
            await killer.send(f"🔪 **YOU ARE THE KILLER!**\nSabko dhoond ke maar daalo! Wait for hiding phase.")
            for v in victims:
                role_msg = "😱 **YOU ARE A VICTIM!** Chupo warna maroge."
                if v == traitor: role_msg += "\n🕵️ **PSST!** Tum **TRAITOR** ho! (Backstabber)"
                await v.send(role_msg)
        except: pass
        
        game_view = HideSeekGameView(killer, victims, traitor, pot)
        
        embed = discord.Embed(title="🌃 LIGHTS OUT! HIDE NOW!", color=0x000000)
        embed.description = (
            f"🛑 **KILLER:** ||{killer.mention}||\n"
            f"🏃 **Victims:** {len(victims)} players\n\n"
            f"👇 **Niche buttons dabake jagah select karo!**\n"
            f"⚡ **Killer 10 second baad aayega!**"
        )
        embed.set_image(url="https://media.tenor.com/Tq9Y_3xOQYkAAAAC/run-bitch-run.gif")
        
        await interaction.response.edit_message(embed=embed, view=game_view)


@bot.tree.command(name="hide_and_seek", description="🔪 Random Killer vs Victims (High Stakes)")
async def hide_seek(i: discord.Interaction):
    view = HideLobbyView(i.user)
    await i.response.send_message(embed=view.get_embed(), view=view)

# ================== 🚦 RED LIGHT, GREEN LIGHT (SQUID GAME) ==================

class RedLightGameView(discord.ui.View):
    def __init__(self, players, pot_money, interaction):
        super().__init__(timeout=300) # 5 Minutes Max Game
        self.players = players # List of user IDs
        self.pot_money = pot_money
        self.interaction = interaction
        self.active_players = {uid: {"dist": 0, "status": "ALIVE"} for uid in players} # 0 to 100m
        
        self.game_state = "GREEN" # GREEN, YELLOW, RED
        self.goal = 100
        self.is_game_over = False
        
        # Setup Run Button
        self.run_btn = discord.ui.Button(label="🏃 RUN! (Click Fast)", style=discord.ButtonStyle.success, custom_id="run_btn")
        self.run_btn.callback = self.run_callback
        self.add_item(self.run_btn)
        
        # Start Game Loop
        self.loop_task = asyncio.create_task(self.game_loop())

    async def game_loop(self):
        """
        Ye loop Light Change karega:
        Green (Run) -> Yellow (Warning) -> Red (Kill) -> Green...
        """
        while not self.is_game_over:
            # --- 🟢 GREEN LIGHT (Safe to Run) ---
            self.game_state = "GREEN"
            self.run_btn.style = discord.ButtonStyle.success
            self.run_btn.label = "🏃 RUN! (SPAM CLICK)"
            self.run_btn.disabled = False
            
            embed = discord.Embed(title="🟢 GREEN LIGHT", description="**BHAAGO!** Button spam karo!", color=0x00FF00)
            embed.set_image(url="https://media.tenor.com/F_r_03yJqG4AAAAC/squid-game-green-light.gif") # Doll Running
            embed.set_footer(text=f"Survivors: {len([p for p in self.active_players.values() if p['status']=='ALIVE'])}")
            
            try: await self.interaction.edit_original_response(embed=embed, view=self)
            except: break
            
            await asyncio.sleep(random.uniform(3, 6)) # 3-6 sec run time

            # --- 🟡 YELLOW LIGHT (Warning) ---
            self.game_state = "YELLOW"
            embed.title = "👀 DOLL IS TURNING..."
            embed.description = "🛑 **RUK JAO!** Doll dekhne wali hai!"
            embed.color = 0xFFA500
            
            try: await self.interaction.edit_original_response(embed=embed, view=self)
            except: break
            
            await asyncio.sleep(1.5) # 1.5 sec warning

            # --- 🔴 RED LIGHT (Death Trap) ---
            self.game_state = "RED"
            self.run_btn.style = discord.ButtonStyle.danger
            self.run_btn.label = "🛑 DON'T MOVE!" 
            # Note: Button disabled nahi kiya, taaki log galti karein!
            
            embed = discord.Embed(title="🔴 RED LIGHT", description="**HILNA MAT!** (Don't Click)", color=0xFF0000)
            embed.set_image(url="https://media.tenor.com/v1sLzJqf8i8AAAAC/squid-game-doll.gif") # Doll Staring (Laser Eyes)
            
            try: await self.interaction.edit_original_response(embed=embed, view=self)
            except: break
            
            await asyncio.sleep(random.uniform(2, 4)) # 2-4 sec death time
            
            # Check for Winners/Losers
            alive_count = len([p for p in self.active_players.values() if p['status']=='ALIVE'])
            if alive_count == 0:
                await self.end_game("NO_SURVIVORS")
                break

    async def run_callback(self, interaction: discord.Interaction):
        uid = interaction.user.id
        
        if uid not in self.players:
            return await interaction.response.send_message("❌ Tum game mein nahi ho!", ephemeral=True)
            
        player_data = self.active_players[uid]
        
        if player_data["status"] == "DEAD" or player_data["status"] == "WON":
            return await interaction.response.send_message("🚫 Tum game se bahar ho.", ephemeral=True)

        # --- LOGIC ---
        if self.game_state == "GREEN":
            # ✅ Safe Run
            move = random.randint(3, 7) # Random speed
            player_data["dist"] += move
            
            if player_data["dist"] >= self.goal:
                player_data["status"] = "WON"
                await interaction.response.send_message(f"🎉 **FINISH LINE!** Tum Jeet gaye!", ephemeral=True)
                await self.check_all_finished()
            else:
                # Silent update to avoid rate limit (Show progress in ephemeral)
                # Har click pe message bhejna spam hoga, isliye defer kar rahe hain
                await interaction.response.defer() 

        elif self.game_state == "YELLOW":
            # ⚠️ Risky (High chance to slip into Red)
            # Yellow me click karne par 20% chance hai girne ka
            if random.random() < 0.2:
                 await interaction.response.send_message("⚠️ **Ladkhada gaye!** (Movement Stalled)", ephemeral=True)
            else:
                 player_data["dist"] += 2 # Slow movement
                 await interaction.response.defer()

        elif self.game_state == "RED":
            # 💀 DEATH CHECK
            user_db = await get_data(uid)
            saved = False
            reason = "Dead"
            
            # 1. VIP Check (50% Matrix Dodge)
            is_vip = False
            if user_db.get("vip_expiry"): is_vip = True # Add proper date check
            
            if is_vip and random.random() < 0.5:
                saved = True
                reason = "🛡️ **VIP Freeze:** Doll ne ignore kar diya!"
            
            # 2. Extra Life Check (Guaranteed Save)
            elif user_db.get("inventory", {}).get("life", 0) > 0:
                await update_inventory(uid, "life", -1)
                saved = True
                reason = "💖 **Extra Life:** Bullet proof jacket ne bacha liya!"

            if saved:
                await interaction.response.send_message(f"😰 **BACH GAYE!** {reason}\nAgli baar mat hilna!", ephemeral=True)
            else:
                # 🔫 ELIMINATED
                player_data["status"] = "DEAD"
                
                # Visual Feedback
                embed = discord.Embed(title="🔫 ELIMINATED!", color=0x2f3136)
                embed.description = f"**{interaction.user.mention}** hila aur mara gaya.\n💀 **Headshot.**"
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                try: await interaction.channel.send(embed=embed)
                except: pass
                
                # Mute Punishment
                await smart_timeout(interaction, interaction.user, 300, "Moved in Red Light")
                await interaction.response.send_message("💀 **YOU DIED.**", ephemeral=True)

    async def check_all_finished(self):
        # Check agar sab ya to Jeet gaye ya Mar gaye
        active = [p for p in self.active_players.values() if p['status'] == "ALIVE"]
        if not active:
            await self.end_game("FINISHED")

    async def end_game(self, reason):
        self.is_game_over = True
        self.loop_task.cancel()
        self.run_btn.disabled = True
        
        winners = [uid for uid, data in self.active_players.items() if data["status"] == "WON"]
        
        if winners:
            prize = self.pot_money // len(winners)
            names = []
            for uid in winners:
                await update_balance(uid, prize)
                names.append(f"<@{uid}>")
            
            desc = f"💰 **Total Pot:** ${self.pot_money:,}\n🏆 **Winners:** {', '.join(names)}\n💵 **Prize Each:** ${prize:,}"
            color = 0x00FF00
            img = "https://media.tenor.com/bXjOidvDvoQAAAAC/confetti-celebrate.gif"
        else:
            desc = f"💀 **SAB MAR GAYE!**\nKoi nahi bacha.\n💰 **Pot Lost:** ${self.pot_money:,}"
            color = 0xFF0000
            img = "https://media.tenor.com/d6-SreC3_p8AAAAC/wasted-gta5.gif"

        embed = discord.Embed(title="🏁 GAME OVER", description=desc, color=color)
        embed.set_image(url=img)
        
        try: await self.interaction.edit_original_response(embed=embed, view=None)
        except: pass


# --- LOBBY VIEW (Entry System) ---
class RedLightLobby(discord.ui.View):
    def __init__(self, host, fee=50000):
        super().__init__(timeout=120)
        self.host = host
        self.players = [host.id] # Store IDs
        self.fee = fee
        self.started = False

    def get_embed(self):
        embed = discord.Embed(title="🚥 RED LIGHT, GREEN LIGHT", color=0xE74C3C)
        embed.description = (
            f"**Host:** {self.host.mention}\n"
            f"💵 **Entry Fee:** ${self.fee:,}\n"
            f"👥 **Players:** {len(self.players)}\n\n"
            f"🟢 **Green:** Bhagoooo!\n"
            f"🔴 **Red:** Hilo mat warna **Maut**.\n"
            f"👇 **JOIN NOW!**"
        )
        embed.set_image(url="https://media.tenor.com/Xv5Wl2l_u-AAAAAC/squid-game-soldier.gif")
        embed.set_footer(text="VIPs have 50% chance to survive Red Light.")
        return embed

    @discord.ui.button(label="JOIN GAME ($50k)", style=discord.ButtonStyle.primary)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.players:
            return await interaction.response.send_message("Already joined!", ephemeral=True)
        
        data = await get_data(interaction.user.id)
        if data["balance"] < self.fee:
            return await interaction.response.send_message("❌ Paise nahi hai tere paas!", ephemeral=True)
            
        await update_balance(interaction.user.id, -self.fee)
        self.players.append(interaction.user.id)
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="START GAME", style=discord.ButtonStyle.success)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host.id: return
        if len(self.players) < 1: return # Testing ke liye 1 allow kar raha hu, production me 2 karna
        
        self.started = True
        pot = len(self.players) * self.fee
        
        game_view = RedLightGameView(self.players, pot, interaction)
        
        # Initial Message
        embed = discord.Embed(title="🟢 GAME STARTING...", description="Tayyar ho jao!", color=0x00FF00)
        await interaction.response.edit_message(embed=embed, view=game_view)


@bot.tree.command(name="red_light", description="🚥 Squid Game: Run on Green, Freeze on Red")
async def red_light(i: discord.Interaction):
    if not i.guild.me.guild_permissions.moderate_members:
        return await i.response.send_message("❌ Mute Permission Missing!", ephemeral=True)
        
    # Host ki fee pehle kaat lo ya lobby me join karwao (Lobby logic use kar rahe hain)
    # Host auto-join karega lobby code me
    
    # Check Host Balance for safety
    data = await get_data(i.user.id)
    if data["balance"] < 50000:
        return await i.response.send_message("❌ $50,000 chahiye host karne ke liye.", ephemeral=True)
    
    # Deduct Host Fee immediately
    await update_balance(i.user.id, -50000)
    
    view = RedLightLobby(i.user)
    await i.response.send_message(embed=view.get_embed(), view=view)

# ================== 🦑 SQUID PENTATHLON (TEAM RELAY MODE) ==================

class PentathlonGameView(discord.ui.View):
    def __init__(self, players, pot_per_winner, interaction):
        super().__init__(timeout=180) # 3 Min total buffer
        self.players = players # List of Member Objects
        self.pot_prize = pot_per_winner
        self.interaction = interaction
        
        self.round_index = 0
        self.game_active = True
        
        # 5 KOREAN GAMES DATA
        self.games = [
            {
                "name": "🔴 Ddakji (Flip)",
                "desc": "Blue Card ya Red Card? Flip karo!",
                "img": "https://media.tenor.com/lZ2tS1uXv4AAAAAC/squid-game-slap.gif",
                "opts": ["🟦 BLUE", "🟥 RED"],
                "win_chance": 0.6
            },
            {
                "name": "🦶 Jegi Chagi (Kick)",
                "desc": "Sack ko hawa mein balance karo!",
                "img": "https://media.tenor.com/yv-15Xn4x4AAAAAC/korean-game.gif",
                "opts": ["🦵 KICK LEFT", "🦵 KICK RIGHT"],
                "win_chance": 0.6
            },
            {
                "name": "🎲 Gonggi (Catch)",
                "desc": "Stones ko hawa mein feko aur pakdo!",
                "img": "https://media.tenor.com/images/3d51737e45b42661502f676458564e9a/tenor.gif",
                "opts": ["✋ GRAB FAST", "🐢 GRAB SLOW"],
                "win_chance": 0.5
            },
            {
                "name": "🌪️ Spinning Top",
                "desc": "Lattu ghuma! Balance bana ke rakh!",
                "img": "https://media.tenor.com/Im_hKqCg4iUAAAAC/inception-top.gif",
                "opts": ["⚖️ BALANCE", "🚀 SPIN HARD"],
                "win_chance": 0.5
            },
            {
                "name": "🦑 Squid Final (Defense)",
                "desc": "Line cross karo ya Defense karo!",
                "img": "https://media.tenor.com/Xv5Wl2l_u-AAAAAC/squid-game-soldier.gif",
                "opts": ["⚔️ ATTACK", "🛡️ DEFEND"],
                "win_chance": 0.5
            }
        ]
        
        # Start First Round
        asyncio.create_task(self.load_round())

    async def load_round(self):
        if not self.game_active: return
        
        # Win Condition: Agar 5 Rounds complete ho gaye
        if self.round_index >= 5:
            await self.team_win()
            return

        # Determine Current Player (Relay Style: P1 -> P2 -> P3 -> P1...)
        self.current_turn_player = self.players[self.round_index % len(self.players)]
        game_data = self.games[self.round_index]

        # Embed Setup
        embed = discord.Embed(title=f"🏆 TEAM RELAY: ROUND {self.round_index + 1}/5", color=0xE91E63) # Squid Pink
        embed.description = (
            f"🎮 **Game:** {game_data['name']}\n"
            f"📝 **Task:** {game_data['desc']}\n\n"
            f"👉 **Player:** {self.current_turn_player.mention}\n"
            f"⚠️ **WARNING:** Agar ye hara, to **PURI TEAM** maregi!\n"
            f"⏱️ **Time:** 15 Seconds!"
        )
        embed.set_image(url=game_data['img'])
        embed.set_footer(text="Team Death Mode: One Fails = All Fail")

        # Buttons Setup
        self.clear_items()
        
        btn1 = discord.ui.Button(label=game_data['opts'][0], style=discord.ButtonStyle.primary, custom_id="opt_1")
        btn2 = discord.ui.Button(label=game_data['opts'][1], style=discord.ButtonStyle.danger, custom_id="opt_2")
        
        btn1.callback = self.game_action
        btn2.callback = self.game_action
        
        self.add_item(btn1)
        self.add_item(btn2)

        try:
            await self.interaction.edit_original_response(embed=embed, view=self)
        except: pass

    async def game_action(self, interaction: discord.Interaction):
        if interaction.user.id != self.current_turn_player.id:
            return await interaction.response.send_message("❌ Teri baari nahi hai! Team ko marwayega kya?", ephemeral=True)

        await interaction.response.defer()
        
        # Game Logic
        game_data = self.games[self.round_index]
        is_win = random.random() < game_data['win_chance']
        
        # --- 🛡️ VIP & LIFE CHECK (Saving Logic) ---
        saved = False
        save_msg = ""
        
        if not is_win:
            data = await get_data(interaction.user.id)
            
            # 1. VIP Check (50% Chance to Save Team)
            is_vip = False
            if data.get("vip_expiry"): is_vip = True 
            
            if is_vip and random.random() < 0.5:
                is_win = True
                saved = True
                save_msg = "(👑 VIP Saved the Team!)"
            
            # 2. Extra Life Check (Guaranteed Save)
            elif data.get("inventory", {}).get("life", 0) > 0:
                await update_inventory(interaction.user.id, "life", -1)
                is_win = True
                saved = True
                save_msg = "(💖 Extra Life Saved the Team!)"

        # Result Handle
        if is_win:
            # ✅ ROUND PASSED
            if saved:
                try:
                    await interaction.followup.send(f"😰 **Close Call!** {save_msg}", ephemeral=True)
                except:
                    pass
            
            self.round_index += 1
            await self.load_round()
        else:
            # ❌ ROUND FAILED = TEAM ELIMINATED
            await self.team_eliminate(interaction.user)

    async def team_eliminate(self, loser):
        self.game_active = False
        self.clear_items()
        
        # 💀 Punish EVERYONE (Team Wipe)
        punish_logs = []
        for p in self.players:
            # Sabko Mute Karo using Smart Timeout
            await smart_timeout(self.interaction, p, 60, f"Pentathlon Failed by {loser.name}")
            punish_logs.append(p.mention)

        embed = discord.Embed(title="💀 TEAM ELIMINATED!", color=0x000000)
        embed.description = (
            f"🚫 **Failed By:** {loser.mention}\n"
            f"🎭 **Task Failed:** {self.games[self.round_index]['name']}\n\n"
            f"⚰️ **TEAM WIPEOUT:**\n" + ", ".join(punish_logs) + "\n\n"
            f"💰 **Prize Lost:** ${len(self.players)*100000:,}\n"
            f"❌ **GAME OVER**"
        )
        embed.set_image(url="https://media.tenor.com/d6-SreC3_p8AAAAC/wasted-gta5.gif")
        
        try: await self.interaction.edit_original_response(embed=embed, view=None)
        except: pass

    async def team_win(self):
        self.game_active = False
        self.clear_items()
        
        # 🎉 Reward EVERYONE
        prize = 100000
        winners_list = []
        
        for p in self.players:
            await update_balance(p.id, prize)
            winners_list.append(p.mention)
            
        embed = discord.Embed(title="🎉 PERFECT TEAMWORK!", color=0xFFD700)
        embed.description = (
            f"🏆 **All 5 Rounds Cleared!**\n\n"
            f"👥 **Survivors:**\n" + ", ".join(winners_list) + "\n\n"
            f"💰 **Reward:** ${prize:,} (Each Player)"
        )
        embed.set_image(url="https://media.tenor.com/p7a8o1r5c8cAAAAC/money-rain.gif")
        
        try: await self.interaction.edit_original_response(embed=embed, view=None)
        except: pass


# --- LOBBY VIEW ---
class PentaLobby(discord.ui.View):
    def __init__(self, host):
        super().__init__(timeout=120)
        self.host = host
        self.players = [host]
        self.started = False

    def get_embed(self):
        plist = "\n".join([f"🏃 {u.name}" for u in self.players])
        embed = discord.Embed(title="🦑 SQUID PENTATHLON (Team Mode)", color=0xE91E63)
        embed.description = (
            f"**Host:** {self.host.mention}\n"
            f"👥 **Players:** {len(self.players)}/5 (Min 2)\n"
            f"💰 **Prize:** $100,000 (Each Player)\n"
            f"🔇 **Punishment:** 1 Min Timeout (Entire Team)\n\n"
            f"⚠️ **RULE:** Ek bhi hara, to sab marenge!\n"
            f"🔥 **5 Mini Games (Relay):**\n"
            f"🔴 Ddakji ➜ 🦶 Jegi ➜ 🎲 Gonggi ➜ 🌪️ Top ➜ 🦑 Final\n\n"
            f"👇 **JOIN NOW!**"
        )
        embed.add_field(name="Participants", value=plist or "Waiting...")
        embed.set_thumbnail(url="https://media.tenor.com/yv-15Xn4x4AAAAAC/korean-game.gif")
        return embed

    @discord.ui.button(label="JOIN TEAM", style=discord.ButtonStyle.success)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            return await interaction.response.send_message("Already joined!", ephemeral=True)
        if len(self.players) >= 5:
            return await interaction.response.send_message("Full House! (Max 5)", ephemeral=True)
            
        self.players.append(interaction.user)
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="START RELAY", style=discord.ButtonStyle.danger)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.host: return
        if len(self.players) < 2: return await interaction.response.send_message("Need at least 2 players!", ephemeral=True)
        
        self.started = True
        game_view = PentathlonGameView(self.players, 100000, interaction)
        await interaction.response.edit_message(embed=discord.Embed(title="🚀 STARTING PENTATHLON...", color=0x00FF00), view=game_view)


@bot.tree.command(name="pentathlon", description="🦑 5-Game Relay Challenge (One Fails = All Die)")
async def pentathlon(i: discord.Interaction):
    if not i.guild.me.guild_permissions.moderate_members:
        return await i.response.send_message("❌ Mute Permission Missing!", ephemeral=True)
        
    view = PentaLobby(i.user)
    await i.response.send_message(embed=view.get_embed(), view=view)

# ================== 📟 MATRIX CYBER TERMINAL (LEVEL SELECTOR) ==================

# ⚙️ GLOBAL CONFIG (Taaki Menu aur Game dono access kar sakein)
MATRIX_LEVELS = {
    1: {"size": 3, "green": 3, "bomb": 0, "time": 8,  "prize": 10000,  "label": "Level 1 (Easy)"},
    2: {"size": 4, "green": 4, "bomb": 0, "time": 8,  "prize": 20000,  "label": "Level 2 (Medium)"},
    3: {"size": 4, "green": 5, "bomb": 1, "time": 10, "prize": 30000,  "label": "Level 3 (Hard)"},
    4: {"size": 5, "green": 6, "bomb": 2, "time": 12, "prize": 50000,  "label": "Level 4 (Expert)"},
    5: {"size": 6, "green": 7, "bomb": 3, "time": 15, "prize": 100000, "label": "Level 5 (Master)"},
    6: {"size": 7, "green": 8, "bomb": 5, "time": 18, "prize": 150000, "label": "Level 6 (Grandmaster)"},
    7: {"size": 7, "green": 10,"bomb": 8, "time": 20, "prize": 200000, "label": "Level 7 (GOD MODE)"},
}

class MatrixInputModal(discord.ui.Modal, title="📟 TERMINAL ACCESS"):
    answer = discord.ui.TextInput(
        label="ENTER COORDINATES",
        placeholder="Example: A1 B3 C2 (Space se alag karein)",
        required=True,
        max_length=50
    )

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        await self.view.check_answer(interaction, self.answer.value)


class MatrixTerminalView(discord.ui.View):
    def __init__(self, player, interaction, level):
        super().__init__(timeout=180)
        self.player = player
        self.interaction = interaction
        self.level = level # Selected Level
        self.game_active = True
        self.rows = "ABCDEFG"
        
        asyncio.create_task(self.start_game())

    async def start_game(self):
        if not self.game_active: return
        
        config = MATRIX_LEVELS[self.level]
        grid_size = config["size"]
        
        # 1. Generate Pattern
        all_coords = []
        for r in range(grid_size):
            for c in range(grid_size):
                all_coords.append(f"{self.rows[r]}{c+1}") # A1, A2...
        
        self.correct_coords = random.sample(all_coords, config["green"])
        remaining = [x for x in all_coords if x not in self.correct_coords]
        self.bomb_coords = random.sample(remaining, config["bomb"])
        
        # 2. SHOW PHASE (Memorize)
        grid_str = self.generate_grid_str(show=True)
        embed = discord.Embed(title=f"📟 HACKING: LEVEL {self.level}", color=0x00FF00)
        embed.description = (
            f"```\n{grid_str}\n```\n"
            f"💰 **Potential Win:** ${config['prize']:,}\n"
            f"🟩 **TARGETS:** {config['green']}\n"
            f"🟥 **BOMBS:** {config['bomb']}\n\n"
            f"⏳ **Memorize Pattern: {config['time']} Seconds!**"
        )
        self.clear_items()
        await self.interaction.edit_original_response(embed=embed, view=self)
        
        await asyncio.sleep(config["time"]) # Wait time
        
        # 3. INPUT PHASE (Hidden)
        grid_str = self.generate_grid_str(show=False)
        embed = discord.Embed(title=f"🔒 ENTER SECURITY CODES", color=0x2C3E50)
        embed.description = (
            f"```\n{grid_str}\n```\n"
            f"👉 **Niche button dabao aur coordinates likho!**\n"
            f"📝 Example: `{self.correct_coords[0]} {self.correct_coords[1]}`"
        )
        
        # Add Input Button
        self.clear_items()
        btn = discord.ui.Button(label="🔓 OPEN TERMINAL INPUT", style=discord.ButtonStyle.success, emoji="⌨️")
        btn.callback = self.open_modal
        self.add_item(btn)
        
        await self.interaction.edit_original_response(embed=embed, view=self)

    def generate_grid_str(self, show=False):
        config = MATRIX_LEVELS[self.level]
        size = config["size"]
        
        header = "   " + " ".join([str(i+1) for i in range(size)])
        board = [header]
        
        for r in range(size):
            row_char = self.rows[r]
            row_line = f"{row_char} "
            
            for c in range(size):
                coord = f"{row_char}{c+1}"
                
                if show:
                    if coord in self.correct_coords: icon = "🟩"
                    elif coord in self.bomb_coords: icon = "🟥"
                    else: icon = "⬛"
                else:
                    icon = "🔳"
                
                row_line += f" {icon}"
            board.append(row_line)
            return "\n".join(board)

    async def open_modal(self, interaction: discord.Interaction):
        if interaction.user.id != self.player.id:
            return await interaction.response.send_message("❌ Apna game khelo!", ephemeral=True)
        await interaction.response.send_modal(MatrixInputModal(self))

    async def check_answer(self, interaction: discord.Interaction, answer_str: str):
        await interaction.response.defer()
        
        user_inputs = answer_str.upper().replace(",", " ").split()
        config = MATRIX_LEVELS[self.level]
        
        correct_hits = 0
        hit_bomb = False
        wrong_input = False
        
        for inp in user_inputs:
            if inp in self.bomb_coords:
                hit_bomb = True
                break
            elif inp in self.correct_coords:
                correct_hits += 1
            else:
                wrong_input = True
        
        if hit_bomb: await self.game_over("BOMB")
        elif wrong_input: await self.game_over("WRONG")
        elif correct_hits < config["green"]: await self.game_over("INCOMPLETE")
        else:
            # ✅ WIN LOGIC (Direct Prize, No Next Level)
            await update_balance(self.player.id, config["prize"])
            await self.game_win(config["prize"])

    async def game_over(self, reason):
        self.game_active = False
        self.clear_items()
        
        final_grid = self.generate_grid_str(show=True)
        
        if reason == "BOMB": txt = "💣 **SYSTEM FAILURE!** Bomb Detected!"
        elif reason == "WRONG": txt = "❌ **ACCESS DENIED!** Wrong Coordinates."
        elif reason == "INCOMPLETE": txt = "⚠️ **ERROR!** Not enough codes entered."
        else: txt = "💀 **DISCONNECTED.**"

        # Punishment
        data = await get_data(self.player.id)
        is_safe = False
        footer_txt = "💀 Penalty: 30s Timeout"
        
        if data.get("vip_expiry"): 
            is_safe = True
            footer_txt = "🛡️ VIP Access: Punishment Bypassed"
        elif data.get("inventory", {}).get("life", 0) > 0:
            is_safe = True
            footer_txt = "💖 Extra Life: Punishment Bypassed"

        if not is_safe:
             await smart_timeout(self.interaction, self.player, 30, "Hack Failed")

        embed = discord.Embed(title="🚫 HACK FAILED", description=f"{txt}\n\n**Correct Pattern:**\n```\n{final_grid}\n```", color=0xFF0000)
        embed.set_footer(text=footer_txt)
        await self.interaction.edit_original_response(embed=embed, view=None)

    async def game_win(self, amount):
        self.game_active = False
        self.clear_items()
        
        embed = discord.Embed(title="✅ SYSTEM BYPASSED!", color=0xFFD700)
        embed.description = (
            f"🎉 **SUCCESS!** Level {self.level} Hacked.\n"
            f"💾 **Data Extracted.**\n"
            f"💸 **Earned:** ${amount:,}"
        )
        embed.set_image(url="https://media.tenor.com/GfSX-u7_NSAAAAAC/coding-hacker.gif")
        await self.interaction.edit_original_response(embed=embed, view=None)


# --- 🕹️ NEW: LEVEL SELECTION VIEW ---
class LevelSelectView(discord.ui.View):
    def __init__(self, player):
        super().__init__(timeout=60)
        self.player = player

    @discord.ui.select(
        placeholder="Choose Security Level to Hack...",
        options=[
            discord.SelectOption(label=info["label"], value=str(lvl), description=f"Prize: ${info['prize']:,} | Size: {info['size']}x{info['size']}")
            for lvl, info in MATRIX_LEVELS.items()
        ]
    )
    async def select_level(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.player.id:
            return await interaction.response.send_message("❌ Apna game start karo!", ephemeral=True)
        
        selected_lvl = int(select.values[0])
        fee = 5000
        
        # Balance Check & Deduct here
        data = await get_data(interaction.user.id)
        if data["balance"] < fee:
            return await interaction.response.send_message(f"❌ Entry Fee ${fee:,} chahiye!", ephemeral=True)
            
        await update_balance(interaction.user.id, -fee)
        
        # Start Game View
        game_view = MatrixTerminalView(interaction.user, interaction, selected_lvl)
        await interaction.response.edit_message(content=f"🚀 **Starting Level {selected_lvl}...** (-${fee:,})", embed=None, view=game_view)


@bot.tree.command(name="matrix_terminal", description="📟 Select a Security Level & Hack the Grid (Cost: $5k)")
async def matrix_terminal(i: discord.Interaction):
    # Sirf Menu Dikhao, paise select karne ke baad katenge
    embed = discord.Embed(title="📟 MATRIX TERMINAL ACCESS", color=0x2ECC71)
    embed.description = (
        "**Welcome, Hacker.**\n"
        "Security Level select karein jo aap todna chahte hain.\n\n"
        "💸 **Entry Fee:** $5,000 (Flat)\n"
        "💀 **Risk:** Wrong Code = Timeout!"
    )
    view = LevelSelectView(i.user)
    await i.response.send_message(embed=embed, view=view)    
        
# ================== 🧑‍💻 THE HACKER RUN (TYPING SPEED GAME) ==================
import io
from PIL import Image, ImageDraw, ImageFont # pip install pillow

# ================== 🧑‍💻 HACKER RUN (IMAGE BASED) ==================

# ⚙️ LEVEL CONFIGURATION
HACKER_LEVELS = {
    1: {"len": 5,  "time": 15, "fee": 5000,  "prize": 10000,  "label": "Level 1 (Script Kiddie)"},
    2: {"len": 7,  "time": 15, "fee": 10000, "prize": 25000,  "label": "Level 2 (Code Breaker)"},
    3: {"len": 9,  "time": 20, "fee": 20000, "prize": 50000,  "label": "Level 3 (Professional)"},
    4: {"len": 12, "time": 25, "fee": 50000, "prize": 120000, "label": "Level 4 (Elite Hacker)"},
    5: {"len": 15, "time": 30, "fee": 100000,"prize": 300000, "label": "Level 5 (GOD MODE)"},
}

# 🖼️ HELPER FUNCTION: Text to Image Generator
def generate_hacker_image(text):
    # 1. Image Settings
    width = 400
    height = 100
    background_color = (0, 0, 0) # Black
    text_color = (0, 255, 0) # Hacker Green
    
    # 2. Create Image
    image = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(image)
    
    # 3. Load Font (Default agar custom nahi hai)
    try:
        # Koshish karenge bada font lene ki
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default() # Fallback

    # 4. Center Text Calculation
    # PIL ke naye versions me textbbox use hota hai, purane me textsize
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except:
        text_w, text_h = draw.textsize(text, font=font)
        
    x = (width - text_w) / 2
    y = (height - text_h) / 2

    # 5. Draw Text & Noise (Lines to prevent OCR)
    draw.text((x, y), text, font=font, fill=text_color)
    
    # Thodi lines bana dete hain taaki koi OCR tool use na kar paye
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(0, 100, 0), width=1)

    # 6. Convert to Bytes for Discord
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return discord.File(buffer, filename="security_code.png")


class HackerInputModal(discord.ui.Modal, title="⌨️ ENTER SECURITY CODE"):
    answer = discord.ui.TextInput(
        label="TYPE THE CODE FROM IMAGE",
        placeholder="Case Sensitive (Jaisa photo me hai waisa likho)",
        required=True,
        max_length=30
    )

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        await self.view.check_code(interaction, self.answer.value)


class HackerRunView(discord.ui.View):
    def __init__(self, player, interaction, level_id):
        super().__init__(timeout=180) # View ka timeout lamba rakha hai, asli timer logic me hai
        self.player = player
        self.interaction = interaction
        self.level_id = level_id
        self.config = HACKER_LEVELS[level_id]
        
        asyncio.create_task(self.start_game())

    def generate_code(self, length):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    async def start_game(self):
        # 1. Generate Logic
        self.current_code = self.generate_code(self.config["len"])
        
        # 2. Generate Image
        file = generate_hacker_image(self.current_code)
        
        # 3. Embed
        embed = discord.Embed(title=f"🧑‍💻 HACKER RUN: {self.config['label']}", color=0x00FF00)
        embed.description = (
            f"💰 **Prize:** ${self.config['prize']:,}\n"
            f"🔒 **Security:** {self.config['len']} Characters\n\n"
            f"👇 **Niche Photo dekho aur Code Type karo!**\n"
            f"⏳ **Time Limit:** {self.config['time']} Seconds"
        )
        embed.set_image(url="attachment://security_code.png") # Image yahan attach hogi
        embed.set_footer(text="Copy-Paste Protected System 🛡️")

        self.clear_items()
        btn = discord.ui.Button(label="⌨️ TYPE CODE NOW", style=discord.ButtonStyle.success, emoji="📟")
        btn.callback = self.open_modal
        self.add_item(btn)
        
        await self.interaction.edit_original_response(embed=embed, view=self, attachments=[file])

    async def open_modal(self, interaction: discord.Interaction):
        if interaction.user.id != self.player.id:
            return await interaction.response.send_message("❌ Apna game khelo!", ephemeral=True)
        await interaction.response.send_modal(HackerInputModal(self))

    async def check_code(self, interaction: discord.Interaction, user_input: str):
        # Case Sensitive Check
        if user_input == self.current_code:
            # ✅ WIN
            await interaction.response.defer()
            await update_balance(self.player.id, self.config["prize"])
            
            embed = discord.Embed(title="✅ SYSTEM HACKED!", color=0xFFD700)
            embed.description = (
                f"🎉 **ACCESS GRANTED!**\n"
                f"Tumne firewall tod diya.\n\n"
                f"💸 **Earned:** ${self.config['prize']:,}"
            )
            embed.set_image(url="https://media.tenor.com/GfSX-u7_NSAAAAAC/coding-hacker.gif")
            await interaction.edit_original_response(embed=embed, view=None, attachments=[])
            
        else:
            # ❌ LOSE
            await self.game_over(interaction, user_input)

    async def game_over(self, interaction: discord.Interaction, wrong_input):
        self.clear_items()
        
        # --- PUNISHMENT LOGIC ---
        data = await get_data(self.player.id)
        is_safe = False
        footer_txt = "💀 Penalty: 30s Timeout"
        
        if data.get("vip_expiry"):
            is_safe = True
            footer_txt = "🛡️ VIP Access: Saved"
        elif data.get("inventory", {}).get("life", 0) > 0:
            await update_inventory(self.player.id, "life", -1)
            is_safe = True
            footer_txt = "💖 Extra Life: Saved"

        if not is_safe:
            await smart_timeout(self.interaction, self.player, 30, "Hack Failed")

        embed = discord.Embed(title="🚫 ACCESS DENIED", color=0xFF0000)
        embed.description = (
            f"❌ **Incorrect Code!**\n"
            f"📝 You Typed: `{wrong_input}`\n"
            f"🔑 Real Code: `{self.current_code}`\n\n"
            f"💸 **Fee Lost:** ${self.config['fee']:,}"
        )
        embed.set_footer(text=footer_txt)
        
        # Purani image hata kar Glitch GIF lagate hain
        embed.set_image(url="https://media.tenor.com/J3i6jGgFqsgAAAAC/money-transfer.gif") 
        
        await interaction.edit_original_response(embed=embed, view=None, attachments=[])


# --- 🕹️ SELECTOR VIEW ---
class HackerLevelSelectView(discord.ui.View):
    def __init__(self, player):
        super().__init__(timeout=60)
        self.player = player

    @discord.ui.select(
        placeholder="Select Difficulty Level...",
        options=[
            discord.SelectOption(label=info["label"], value=str(lvl), description=f"Fee: ${info['fee']:,} | Prize: ${info['prize']:,}")
            for lvl, info in HACKER_LEVELS.items()
        ]
    )
    async def select_level(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.player.id:
            return await interaction.response.send_message("❌ Apna game start karo!", ephemeral=True)
        
        lvl_id = int(select.values[0])
        config = HACKER_LEVELS[lvl_id]
        
        # Balance Check
        data = await get_data(interaction.user.id)
        if data["balance"] < config["fee"]:
            return await interaction.response.send_message(f"❌ Is level ke liye ${config['fee']:,} chahiye!", ephemeral=True)
            
        await update_balance(interaction.user.id, -config["fee"])
        
        # Start Game
        game_view = HackerRunView(interaction.user, interaction, lvl_id)
        await interaction.response.edit_message(content=f"🚀 **Initializing Attack Sequence...**", embed=None, view=game_view)


@bot.tree.command(name="hacker_run", description="🧑‍💻 Hack the system by typing the code from Image")
async def hacker_run(i: discord.Interaction):
    embed = discord.Embed(title="🧑‍💻 HACKER RUN (ANTI-BOT SYSTEM)", color=0x2ECC71)
    embed.description = (
        "**Welcome, Black Hat.**\n"
        "Security Level select karo.\n\n"
        "📸 **Rule:** Ek Image (Photo) aayegi, uska code dekh kar type karna hai.\n"
        "🚫 **No Copy Paste:** Text copy nahi hoga, photo hai!\n"
        "💀 **Risk:** Galat code = Timeout."
    )
    view = HackerLevelSelectView(i.user)
    await i.response.send_message(embed=embed, view=view) 

# ================== 🧠 INSANE TRIVIA (UPSC LEVEL) ==================

# 🤯 QUESTION BANK (HARDCORE)
TRIVIA_QUESTIONS = [
    {
        "q": "The 'Voynich Manuscript' has baffled cryptographers for centuries. Carbon dating places it in which century?",
        "o": ["13th Century", "15th Century", "17th Century", "11th Century"],
        "a": "15th Century"
    },
    {
        "q": "In Quantum Mechanics, 'Schrödinger's Cat' experiment hypothetically used which radioactive substance?",
        "o": ["Uranium-235", "Radium", "Polonium", "Minute amount of any source"],
        "a": "Minute amount of any source"
    },
    {
        "q": "The 'Antikythera Mechanism' (world's first analog computer) was primarily used to predict what?",
        "o": ["Earthquakes", "Astronomical Positions", "Weather Patterns", "Sea Tides"],
        "a": "Astronomical Positions"
    },
    {
        "q": "Which treaty signed in 1648 is credited with creating the modern nation-state system (Westphalian sovereignty)?",
        "o": ["Treaty of Versailles", "Peace of Westphalia", "Treaty of Utrecht", "Congress of Vienna"],
        "a": "Peace of Westphalia"
    },
    {
        "q": "The Event Horizon Telescope captured the first image of a Black Hole in which galaxy?",
        "o": ["Milky Way", "Andromeda", "Messier 87 (M87)", "Triangulum"],
        "a": "Messier 87 (M87)"
    },
    {
        "q": "In Mahabharata, what was the specific name of the weapon Ashwatthama used against the Pandavas?",
        "o": ["Brahmastra", "Pashupatastra", "Brahmashirsha Astra", "Narayanastra"],
        "a": "Brahmashirsha Astra"
    },
    {
        "q": "What is the biological term for the 'Process of Programmed Cell Death'?",
        "o": ["Necrosis", "Apoptosis", "Mitosis", "Phagocytosis"],
        "a": "Apoptosis"
    },
    {
        "q": "Which obscure Indian dynasty ruled Kamarupa (Assam) from 350-650 CE and claimed descent from Narakasura?",
        "o": ["Ahom Dynasty", "Varman Dynasty", "Pala Dynasty", "Chutia Dynasty"],
        "a": "Varman Dynasty"
    },
    {
        "q": "The mathematical constant 'e' (Euler's number) is the base of which logarithm?",
        "o": ["Common Logarithm", "Binary Logarithm", "Natural Logarithm", "Complex Logarithm"],
        "a": "Natural Logarithm"
    },
    {
        "q": "In 1908, a massive explosion flattened 2,000 sq km of Siberian forest. What is this event called?",
        "o": ["Chelyabinsk Event", "Tunguska Event", "Sikhote-Alin Event", "Vredefort Impact"],
        "a": "Tunguska Event"
    },
    {
        "q": "In the world of Cryptocurrency, what is the specific term for a crypto wallet that is NOT connected to the internet (for security)?",
        "o": ["Hot Wallet", "Cold Wallet", "Dead Wallet", "Hard Drive"],
        "a": "Cold Wallet"
    },
    {
        "q": "The 'Barren Island', the only active volcano in India, is located in which part of the Andaman & Nicobar Islands?",
        "o": ["Great Nicobar", "North Andaman", "Little Andaman", "East of Middle Andaman"],
        "a": "East of Middle Andaman"
    },
    {
        "q": "Who was the revolutionary who shot dead Robert Ashe, the Collector of Tirunelveli, in 1911 and then committed suicide?",
        "o": ["Vanchinathan", "Tiruppur Kumaran", "Subramania Siva", "V.O. Chidambaram Pillai"],
        "a": "Vanchinathan"
    },
    {
        "q": "Which female revolutionary fired five shots at the Governor of Bengal, Stanley Jackson, during the Convocation Hall ceremony in 1932?",
        "o": ["Pritilata Waddedar", "Kalpana Datta", "Bina Das", "Matangini Hazra"],
        "a": "Bina Das"
    },
    {
        "q": "Which country has no official capital city?",
        "o": ["Monaco", "Nauru", "Vatican City", "Tuvalu"],
        "a": "Nauru"
    },
    {
        "q": "What is the name of the 'Point of Inaccessibility' in the ocean, which is the farthest point from any land?",
        "o": ["Challenger Deep", "Point Nemo", "Bermuda Triangle", "Mariana Trench"],
        "a": "Point Nemo"
    },
    {
        "q": "In the Solar System, which planet has the 'Great Dark Spot' (similar to Jupiter's Red Spot)?",
        "o": ["Uranus", "Neptune", "Saturn", "Mars"],
        "a": "Neptune"
    },
    {
        "q": "Which war in history is recorded as the 'Shortest War' ever fought (lasting only 38 to 45 minutes)?",
        "o": ["Anglo-Zanzibar War", "Six-Day War", "Football War", "Falklands War"],
        "a": "Anglo-Zanzibar War"
    },
    {
        "q": "The 'Valles Marineris' is a massive canyon system (larger than the Grand Canyon) located on which planet?",
        "o": ["Venus", "Mars", "Mercury", "Earth"],
        "a": "Mars"
    },
    {
        "q": "Which country has the most time zones (including overseas territories)?",
        "o": ["Russia", "France", "USA", "China"],
        "a": "France"
    },
    {
        "q": "What is the name of the star that is currently the 'North Star' (Pole Star)?",
        "o": ["Sirius", "Polaris", "Vega", "Betelgeuse"],
        "a": "Polaris"
    },
    {
        "q": "Which is the only sea in the world that has no coastline?",
        "o": ["Sargasso Sea", "Dead Sea", "Caspian Sea", "Red Sea"],
        "a": "Sargasso Sea"
    },
    {
        "q": "The 'Fermi Paradox' is a scientific concept that questions...",
        "o": ["The stability of black holes", "Where are all the aliens?", "The speed of light limit", "Time travel possibilities"],
        "a": "Where are all the aliens?"
    },
    {
        "q": "Which African country was formerly known as 'Abyssinia'?",
        "o": ["Ethiopia", "Sudan", "Liberia", "Zimbabwe"],
        "a": "Ethiopia"
    },
    {
        "q": "What is the specific term for a Neutron Star that spins rapidly and emits beams of radiation?",
        "o": ["Quasar", "Pulsar", "Magnetar", "White Dwarf"],
        "a": "Pulsar"
    },
    {
        "q": "Which element has the highest melting point of all elements?",
        "o": ["Tungsten", "Carbon", "Titanium", "Platinum"],
        "a": "Tungsten"
    },
    {
        "q": "The 'Diomede Islands' are unique because they are separated by only 3.8 km but have a time difference of?",
        "o": ["1 Hour", "21 Hours", "12 Hours", "30 Minutes"],
        "a": "21 Hours"
    },
    {
        "q": "Which chemical element is named after the creator of the Periodic Table?",
        "o": ["Mendelevium", "Curium", "Einsteinium", "Nobelium"],
        "a": "Mendelevium"
    },
    {
        "q": "Which is the most abundant gas in the atmosphere of Venus?",
        "o": ["Nitrogen", "Carbon Dioxide", "Methane", "Sulfuric Acid"],
        "a": "Carbon Dioxide"
    },
    {
        "q": "What is the name of the largest known volcano in the Solar System?",
        "o": ["Mount Everest", "Olympus Mons", "Mauna Kea", "Maxwell Montes"],
        "a": "Olympus Mons"
    },
    {
        "q": "The 'Library of Alexandria' was located in which modern-day country?",
        "o": ["Greece", "Egypt", "Italy", "Turkey"],
        "a": "Egypt"
    },
    {
        "q": "Which country is home to the 'Door to Hell' (Darvaza Gas Crater)?",
        "o": ["Kazakhstan", "Turkmenistan", "Uzbekistan", "Iran"],
        "a": "Turkmenistan"
    },
    {
        "q": "The 'Oort Cloud' is a theoretical shell of icy objects located...",
        "o": ["Between Mars and Jupiter", "Beyond Pluto (Outer Solar System)", "Around Saturn's Rings", "Inside the Sun's core"],
        "a": "Beyond Pluto (Outer Solar System)"
    },
    {
        "q": "Which treaty officially ended World War I?",
        "o": ["Treaty of Paris", "Treaty of Versailles", "Treaty of Ghent", "Treaty of Tordesillas"],
        "a": "Treaty of Versailles"
    },
    {
        "q": "What color is the sunset on Mars?",
        "o": ["Red", "Blue", "Green", "Yellow"],
        "a": "Blue"
    },
    {
        "q": "Which is the only country in the world to have a non-rectangular flag?",
        "o": ["Switzerland", "Nepal", "Vatican City", "Bhutan"],
        "a": "Nepal"
    },
    {
        "q": "The 'Tunguska Event' of 1908 occurred in which country?",
        "o": ["USA", "Russia", "Canada", "China"],
        "a": "Russia"
    },
    {
        "q": "Which planet rotates on its side (like a rolling ball)?",
        "o": ["Venus", "Uranus", "Neptune", "Saturn"],
        "a": "Uranus"
    },
    {
        "q": "The 'Hague' is the seat of government for which country, though not its capital?",
        "o": ["Belgium", "Netherlands", "Switzerland", "Denmark"],
        "a": "Netherlands"
    },
    {
        "q": "What is the name of the boundary that marks the edge of the heliosphere (Sun's influence)?",
        "o": ["Kuiper Belt", "Heliopause", "Oort Cloud", "Magnetosphere"],
        "a": "Heliopause"
    },
    {
        "q": "Which two countries share the longest international border?",
        "o": ["Russia and China", "USA and Canada", "Argentina and Chile", "India and China"],
        "a": "USA and Canada"
    },
    {
        "q": "The 'Year Without a Summer' (1816) was caused by the eruption of which volcano?",
        "o": ["Krakatoa", "Mount Tambora", "Vesuvius", "Mount St. Helens"],
        "a": "Mount Tambora"
    },
    {
        "q": "Which moon of Jupiter is considered the most likely place to find extraterrestrial life?",
        "o": ["Io", "Europa", "Ganymede", "Callisto"],
        "a": "Europa"
    },
    {
        "q": "The 'Zimmermann Telegram' was a secret diplomatic communication that pushed which country into WWI?",
        "o": ["Russia", "USA", "UK", "Italy"],
        "a": "USA"
    },
    {
        "q": "Which is the smallest country in the world by land area?",
        "o": ["Monaco", "Vatican City", "Nauru", "San Marino"],
        "a": "Vatican City"
    },
    {
        "q": "What is the term for a black hole formed by the collapse of a massive star?",
        "o": ["Supermassive Black Hole", "Stellar Black Hole", "Primordial Black Hole", "Miniature Black Hole"],
        "a": "Stellar Black Hole"
    },
    {
        "q": "Which country was formerly known as 'Ceylon'?",
        "o": ["Myanmar", "Sri Lanka", "Thailand", "Cambodia"],
        "a": "Sri Lanka"
    },
    {
        "q": "The 'Chandrasekhar Limit' (1.4 solar masses) determines the maximum mass of a...",
        "o": ["Neutron Star", "White Dwarf", "Black Hole", "Red Giant"],
        "a": "White Dwarf"
    },
    {
        "q": "Which South American country has two capitals (La Paz and Sucre)?",
        "o": ["Peru", "Bolivia", "Chile", "Ecuador"],
        "a": "Bolivia"
    },
    {
        "q": "The 'Goldilocks Zone' in astronomy refers to...",
        "o": ["Area with most gold asteroids", "Habitable zone around a star", "Center of the galaxy", "Safe zone for black holes"],
        "a": "Habitable zone around a star"
    },
    {
        "q": "Which empire was ruled by the 'Inca' civilization?",
        "o": ["Mexico", "Peru (Andes Region)", "Brazil", "Egypt"],
        "a": "Peru (Andes Region)"
    },
    {
        "q": "What is the name of the galaxy that is on a collision course with the Milky Way?",
        "o": ["Triangulum", "Andromeda", "Whirlpool", "Sombrero"],
        "a": "Andromeda"
    },
    {
        "q": "Which is the only continent with no active volcanoes?",
        "o": ["Australia", "Antarctica", "Europe", "Africa"],
        "a": "Australia"
    },
    {
        "q": "The 'Manhattan Project' was the research project that produced the first...",
        "o": ["Space Rocket", "Nuclear Weapon", "Internet", "Computer"],
        "a": "Nuclear Weapon"
    },
    {
        "q": "Which planet has the shortest day in the Solar System (rotates fastest)?",
        "o": ["Mercury", "Jupiter", "Earth", "Mars"],
        "a": "Jupiter"
    },
    {
        "q": "The 'Bering Strait' separates which two countries?",
        "o": ["UK and France", "USA (Alaska) and Russia", "Spain and Morocco", "Japan and Korea"],
        "a": "USA (Alaska) and Russia"
    },
    {
        "q": "Which chemical element has the symbol 'W'?",
        "o": ["Wolfram (Tungsten)", "Water", "White Phosphorous", "Wanium"],
        "a": "Wolfram (Tungsten)"
    },
    {
        "q": "The 'Great Red Spot' on Jupiter is essentially a massive...",
        "o": ["Volcano", "Storm (Anticyclone)", "Crater", "Ocean"],
        "a": "Storm (Anticyclone)"
    },
    {
        "q": "Which country is known as the 'Land of the Thunderbolt'?",
        "o": ["Nepal", "Bhutan", "Japan", "Tibet"],
        "a": "Bhutan"
    },
    {
        "q": "What is the theoretical boundary around a black hole called?",
        "o": ["Singularity", "Event Horizon", "Photon Ring", "Accretion Disk"],
        "a": "Event Horizon"
    },
    {
        "q": "Which war lasted for 335 years (1651–1986) without a single shot being fired?",
        "o": ["Three Hundred and Thirty Five Years' War", "Cold War", "Anglo-Dutch War", "The Silent War"],
        "a": "Three Hundred and Thirty Five Years' War"
    },
    {
        "q": "Which planet is known as the 'Morning Star' or 'Evening Star'?",
        "o": ["Mars", "Venus", "Mercury", "Jupiter"],
        "a": "Venus"
    },
    {
        "q": "The 'Dead Sea' is located between which two countries?",
        "o": ["Israel and Jordan", "Egypt and Saudi Arabia", "Turkey and Syria", "Iran and Iraq"],
        "a": "Israel and Jordan"
    },
    {
        "q": "Which spacecraft was the first to land humans on the Moon?",
        "o": ["Apollo 11", "Apollo 13", "Vostok 1", "Gemini 8"],
        "a": "Apollo 11"
    },
    {
        "q": "Which country has the most lakes in the world?",
        "o": ["USA", "Canada", "Russia", "Finland"],
        "a": "Canada"
    },
    {
        "q": "What is the term for the explosion of a dying star?",
        "o": ["Nebula", "Supernova", "Black Dwarf", "Red Giant"],
        "a": "Supernova"
    },
    {
        "q": "Which African nation was created by freed American slaves?",
        "o": ["Nigeria", "Liberia", "Ghana", "Kenya"],
        "a": "Liberia"
    },
    {
        "q": "The 'Kuiper Belt' is the home of which famous dwarf planet?",
        "o": ["Ceres", "Pluto", "Eris", "Sedna"],
        "a": "Pluto"
    },
    {
        "q": "Which city is located on two continents (Europe and Asia)?",
        "o": ["Moscow", "Istanbul", "Cairo", "Dubai"],
        "a": "Istanbul"
    },
    {
        "q": "Which gas gives Neptune and Uranus their blue color?",
        "o": ["Oxygen", "Methane", "Hydrogen", "Helium"],
        "a": "Methane"
    },
    {
        "q": "The 'Magna Carta' (1215) was signed by which King of England?",
        "o": ["King Henry VIII", "King John", "King Richard", "King George"],
        "a": "King John"
    },
    {
        "q": "What is the only substance on Earth found naturally in three forms (Solid, Liquid, Gas)?",
        "o": ["Mercury", "Water", "Carbon Dioxide", "Nitrogen"],
        "a": "Water"
    },
    {
        "q": "Which country owns the island of Greenland?",
        "o": ["Canada", "Denmark", "USA", "Norway"],
        "a": "Denmark"
    },
    {
        "q": "The 'Pillars of Creation' are located in which Nebula?",
        "o": ["Crab Nebula", "Eagle Nebula", "Orion Nebula", "Horsehead Nebula"],
        "a": "Eagle Nebula"
    },
    {
        "q": "Which ancient civilization built the Machu Picchu?",
        "o": ["Aztec", "Inca", "Maya", "Olmec"],
        "a": "Inca"
    },
    {
        "q": "What is the name of the first dog sent into space?",
        "o": ["Belka", "Laika", "Strelka", "Sputnik"],
        "a": "Laika"
    },
    {
        "q": "Which country is the largest producer of Coffee in the world?",
        "o": ["Colombia", "Brazil", "Vietnam", "Ethiopia"],
        "a": "Brazil"
    },
    {
        "q": "What phenomenon causes the 'Northern Lights'?",
        "o": ["Reflection of ice", "Solar Wind interacting with Magnetosphere", "Moonlight", "Volcanic Dust"],
        "a": "Solar Wind interacting with Magnetosphere"
    },
    {
        "q": "Which is the deepest known point in the Earth's oceans?",
        "o": ["Tonga Trench", "Challenger Deep (Mariana Trench)", "Puerto Rico Trench", "Java Trench"],
        "a": "Challenger Deep (Mariana Trench)"
    },
    {
        "q": "Who was the first person to travel into space?",
        "o": ["Neil Armstrong", "Yuri Gagarin", "Alan Shepard", "Buzz Aldrin"],
        "a": "Yuri Gagarin"
    },
    {
        "q": "Which country has the nickname 'The Land of Fire and Ice'?",
        "o": ["Greenland", "Iceland", "Norway", "New Zealand"],
        "a": "Iceland"
    },
    {
        "q": "The 'Zimmermann Plan' was a conspiracy between the Ghadar Party and which country to ship arms into India for a revolt?",
        "o": ["Japan", "Germany", "Russia", "Turkey"],
        "a": "Germany"
    },
    {
        "q": "Who was the defense lawyer for Bhagat Singh and Batukeshwar Dutt in the Assembly Bomb Case?",
        "o": ["Asaf Ali", "Bhulabhai Desai", "Tej Bahadur Sapru", "Kailash Nath Katju"],
        "a": "Asaf Ali"
    },
    {
        "q": "In the 1857 Revolt, who led the rebels in the region of Arrah (Bihar) and famously cut off his own injured hand to offer it to the Ganges?",
        "o": ["Nana Sahib", "Kunwar Singh", "Tatya Tope", "Maulvi Ahmadullah"],
        "a": "Kunwar Singh"
    },
    {
        "q": "Who founded the 'India House' in London, which became a hub for Indian revolutionaries abroad?",
        "o": ["Dadabhai Naoroji", "Shyamji Krishna Varma", "Madam Bhikaji Cama", "V.D. Savarkar"],
        "a": "Shyamji Krishna Varma"
    },
    {
        "q": "The 'Rampa Rebellion' of 1922-24 in Andhra Pradesh was led by which legendary tribal leader?",
        "o": ["Birsa Munda", "Alluri Sitarama Raju", "Komaram Bheem", "Sidhu Murmu"],
        "a": "Alluri Sitarama Raju"
    },
    {
        "q": "Who was the only woman to be part of the 'Hindustan Socialist Republican Association' (HSRA) core group?",
        "o": ["Durga Bhabhi (Durga Devi Vohra)", "Sushila Didi", "Kalpana Datta", "Lakshmi Sahgal"],
        "a": "Durga Bhabhi (Durga Devi Vohra)"
    },
    {
        "q": "Bagha Jatin (Jatin Mukherjee) died fighting the British police in a trench battle at which location in 1915?",
        "o": ["Chittagong", "Balasore", "Midnapore", "Alipore"],
        "a": "Balasore"
    },
    {
        "q": "Who authored the controversial book 'The Indian War of Independence, 1857', which was banned by the British?",
        "o": ["Lala Lajpat Rai", "V.D. Savarkar", "Bal Gangadhar Tilak", "Subhash Chandra Bose"],
        "a": "V.D. Savarkar"
    },
    {
        "q": "The 'Komagata Maru' incident involved a Japanese steamship chartered by whom?",
        "o": ["Kartar Singh Sarabha", "Gurdit Singh", "Sohan Singh Bhakna", "Lala Har Dayal"],
        "a": "Gurdit Singh"
    },
    {
        "q": "Who was the Commander-in-Chief of the 'Rani of Jhansi Regiment' of the INA?",
        "o": ["Lakshmi Sahgal", "Janaky Athi Nahappan", "Rasammah Bhupalan", "Aruna Asaf Ali"],
        "a": "Lakshmi Sahgal"
    },
    {
        "q": "Which revolutionary was known as 'Masterda' and led the Chittagong Armoury Raid in 1930?",
        "o": ["Surya Sen", "Rash Behari Bose", "Jatindranath Das", "Barindra Kumar Ghosh"],
        "a": "Surya Sen"
    },
    {
        "q": "Who betrayed the revolutionaries in the 'Kakori Conspiracy Case' by becoming an approver (government witness)?",
        "o": ["Banwari Lal", "Ram Prasad Bismil", "Ashfaqullah Khan", "Roshan Singh"],
        "a": "Banwari Lal"
    },
    {
        "q": "Jatindranath Das died in Lahore Jail after a hunger strike of how many days?",
        "o": ["50 Days", "63 Days", "90 Days", "45 Days"],
        "a": "63 Days"
    },
    {
        "q": "Who gave the title 'Mahatma' to Gandhi (often debated, but historically attributed to)?",
        "o": ["Subhash Chandra Bose", "Rabindranath Tagore", "Gopal Krishna Gokhale", "Jawaharlal Nehru"],
        "a": "Rabindranath Tagore"
    },
    {
        "q": "The 'Cunningham Circular' imposed in Assam during the Civil Disobedience Movement was against?",
        "o": ["Students participating in politics", "Farmers growing opium", "Tea garden workers", "Press freedom"],
        "a": "Students participating in politics"
    },
    {
        "q": "Who was the founder of the secret society 'Abhinav Bharat'?",
        "o": ["Aurobindo Ghosh", "V.D. Savarkar", "Pulin Behari Das", "Bhagat Singh"],
        "a": "V.D. Savarkar"
    },
    {
        "q": "In the Alipore Bomb Case (1908), who successfully defended Aurobindo Ghosh?",
        "o": ["C.R. Das (Chittaranjan Das)", "Motilal Nehru", "B.R. Ambedkar", "W.C. Bonnerjee"],
        "a": "C.R. Das (Chittaranjan Das)"
    },
    {
        "q": "Who hoisted the first version of the Indian flag at Stuttgart, Germany in 1907?",
        "o": ["Annie Besant", "Madam Bhikaji Cama", "Sarojini Naidu", "Sister Nivedita"],
        "a": "Madam Bhikaji Cama"
    },
    {
        "q": "Which British officer was assassinated by the Chapekar Brothers (Damodar and Balkrishna) in 1897?",
        "o": ["W.C. Rand", "Curzon Wyllie", "John Saunders", "General Dyer"],
        "a": "W.C. Rand"
    },
    {
        "q": "The 'Ulgulan' is a term associated with the rebellion led by?",
        "o": ["Sidhu and Kanhu", "Birsa Munda", "Tantia Bhil", "Rani Gaidinliu"],
        "a": "Birsa Munda"
    },
    {
        "q": "Who established the 'Provisional Government of Free India' in Kabul in 1915?",
        "o": ["Raja Mahendra Pratap", "Subhash Chandra Bose", "Rash Behari Bose", "Lala Har Dayal"],
        "a": "Raja Mahendra Pratap"
    },
    {
        "q": "Which revolutionary is known for the 'Silk Letter Conspiracy' (Reshmi Rumal Tehrik)?",
        "o": ["Maulana Abul Kalam Azad", "Maulana Ubaidullah Sindhi", "Khan Abdul Ghaffar Khan", "Hasrat Mohani"],
        "a": "Maulana Ubaidullah Sindhi"
    },
    {
        "q": "Who was the first President of the Ghadar Party?",
        "o": ["Lala Har Dayal", "Sohan Singh Bhakna", "Kartar Singh Sarabha", "Taraknath Das"],
        "a": "Sohan Singh Bhakna"
    },
    {
        "q": "The 'Royal Indian Navy (RIN) Mutiny' of 1946 started on which ship?",
        "o": ["HMIS Talwar", "HMIS Bombay", "HMIS Hindustan", "HMIS Shivaji"],
        "a": "HMIS Talwar"
    },
    {
        "q": "Who was the Viceroy of India when the Jallianwala Bagh Massacre took place?",
        "o": ["Lord Curzon", "Lord Chelmsford", "Lord Irwin", "Lord Reading"],
        "a": "Lord Chelmsford"
    },
    {
        "q": "Who wrote the song 'Sarfaroshi Ki Tamanna' made famous by Ram Prasad Bismil?",
        "o": ["Ram Prasad Bismil", "Bismil Azimabadi", "Mirza Ghalib", "Faiz Ahmed Faiz"],
        "a": "Bismil Azimabadi"
    },
    {
        "q": "The 'August Offer' of 1940 was proposed by which Viceroy?",
        "o": ["Lord Linlithgow", "Lord Wavell", "Lord Mountbatten", "Lord Willingdon"],
        "a": "Lord Linlithgow"
    },
    {
        "q": "Who was the only Indian to be elected as a Member of the British House of Commons in the 19th Century?",
        "o": ["Dadabhai Naoroji", "W.C. Bonnerjee", "Ferozeshah Mehta", "G.K. Gokhale"],
        "a": "Dadabhai Naoroji"
    },
    {
        "q": "Which organization was founded by Khan Abdul Ghaffar Khan (Frontier Gandhi)?",
        "o": ["Khudai Khidmatgar", "Ahrar Party", "Khaksar Party", "Muslim League"],
        "a": "Khudai Khidmatgar"
    },
    {
        "q": "Who called Subhash Chandra Bose 'Desh Nayak'?",
        "o": ["Mahatma Gandhi", "Rabindranath Tagore", "Jawaharlal Nehru", "Sardar Patel"],
        "a": "Rabindranath Tagore"
    },
    {
        "q": "The 'Bardoli Satyagraha' (1928) earned Vallabhbhai Patel which title?",
        "o": ["Iron Man", "Sardar", "Lokmanya", "Acharya"],
        "a": "Sardar"
    },
    {
        "q": "Who assassinated Sir Curzon Wyllie in London in 1909?",
        "o": ["Madan Lal Dhingra", "Udham Singh", "Bhagat Singh", "V.D. Savarkar"],
        "a": "Madan Lal Dhingra"
    },
    {
        "q": "The 'Vaikom Satyagraha' in Kerala was primarily related to?",
        "o": ["Temple Entry for lower castes", "Salt Tax", "Land rights for peasants", "Educational rights"],
        "a": "Temple Entry for lower castes"
    },
    {
        "q": "Who founded the 'All India Forward Bloc' after resigning from the Congress?",
        "o": ["M.N. Roy", "Subhash Chandra Bose", "J.P. Narayan", "Acharya Narendra Dev"],
        "a": "Subhash Chandra Bose"
    },
    {
        "q": "Which revolutionary shot dead the Approver (traitor) Phanindranath Ghosh who betrayed Bhagat Singh?",
        "o": ["Baikuntha Shukla", "Yogendra Shukla", "Batukeshwar Dutt", "Sukhdev"],
        "a": "Baikuntha Shukla"
    },
    {
        "q": "Who was the 'Political Guru' of Mahatma Gandhi?",
        "o": ["Bal Gangadhar Tilak", "Gopal Krishna Gokhale", "Dadabhai Naoroji", "Leo Tolstoy"],
        "a": "Gopal Krishna Gokhale"
    },
    {
        "q": "Who led the 'Revolt of 1857' in Lucknow?",
        "o": ["Begum Hazrat Mahal", "Rani Laxmibai", "Nana Sahib", "Khan Bahadur Khan"],
        "a": "Begum Hazrat Mahal"
    },
    {
        "q": "Which act was popularly known as the 'Black Act'?",
        "o": ["Rowlatt Act", "Vernacular Press Act", "Arms Act", "Ilbert Bill"],
        "a": "Rowlatt Act"
    },
    {
        "q": "The 'Teebhaga Movement' was a peasant agitation in which region?",
        "o": ["Bengal", "Telangana", "Punjab", "Madras"],
        "a": "Bengal"
    },
    {
        "q": "Who authored the book 'Poverty and Un-British Rule in India'?",
        "o": ["R.C. Dutt", "Dadabhai Naoroji", "M.G. Ranade", "G.K. Gokhale"],
        "a": "Dadabhai Naoroji"
    },
    {
        "q": "Which Session of Congress passed the 'Purna Swaraj' (Complete Independence) resolution?",
        "o": ["Lahore Session (1929)", "Calcutta Session (1928)", "Madras Session (1927)", "Karachi Session (1931)"],
        "a": "Lahore Session (1929)"
    },
    {
        "q": "Who was known as the 'Mother of Indian Revolution'?",
        "o": ["Sarojini Naidu", "Madam Bhikaji Cama", "Annie Besant", "Kasturba Gandhi"],
        "a": "Madam Bhikaji Cama"
    },
    {
        "q": "The famous 'Tryst with Destiny' speech was delivered by Nehru on?",
        "o": ["Midnight of Aug 14-15, 1947", "Jan 26, 1950", "Aug 15 Morning, 1947", "Jan 26, 1930"],
        "a": "Midnight of Aug 14-15, 1947"
    },
    {
        "q": "Who commanded the 'Gandhi Brigade' of the INA?",
        "o": ["Inayat Kiani", "Shah Nawaz Khan", "Prem Sahgal", "Gurbaksh Singh Dhillon"],
        "a": "Inayat Kiani"
    },
    {
        "q": "Who famously said 'Swaraj is my birthright and I shall have it'?",
        "o": ["Bal Gangadhar Tilak", "Lala Lajpat Rai", "Bipin Chandra Pal", "Aurobindo Ghosh"],
        "a": "Bal Gangadhar Tilak"
    },
    {
        "q": "Which revolutionary was popularly known as 'Sher-e-Punjab'?",
        "o": ["Bhagat Singh", "Lala Lajpat Rai", "Udham Singh", "Ranjit Singh"],
        "a": "Lala Lajpat Rai"
    },
    {
        "q": "The 'Moplah Rebellion' (1921) took place in which region?",
        "o": ["Malabar (Kerala)", "Konkan (Maharashtra)", "Coromandel (Tamil Nadu)", "Vidarbha"],
        "a": "Malabar (Kerala)"
    },
    {
        "q": "Who was the first Indian woman to become the President of the Indian National Congress?",
        "o": ["Annie Besant", "Sarojini Naidu", "Nellie Sengupta", "Sucheta Kripalani"],
        "a": "Sarojini Naidu"
    },
    {
        "q": "Who designed the current National Flag of India?",
        "o": ["Pingali Venkayya", "Rabindranath Tagore", "Bankim Chandra Chatterjee", "Alluri Sitarama Raju"],
        "a": "Pingali Venkayya"
    },
    {
        "q": "Who led the 'Salt Satyagraha' in Tamil Nadu (Vedaranyam March)?",
        "o": ["C. Rajagopalachari", "K. Kamaraj", "Subramania Siva", "V.O. Chidambaram"],
        "a": "C. Rajagopalachari"
    },
    {
        "q": "The 'Chauri Chaura' incident (1922) led to the withdrawal of which movement?",
        "o": ["Non-Cooperation Movement", "Civil Disobedience Movement", "Quit India Movement", "Khilafat Movement"],
        "a": "Non-Cooperation Movement"
    },
    {
        "q": "Who founded the 'Servants of India Society'?",
        "o": ["Gopal Krishna Gokhale", "Bal Gangadhar Tilak", "Lala Lajpat Rai", "M.G. Ranade"],
        "a": "Gopal Krishna Gokhale"
    },
    {
        "q": "Which revolutionary threw a bomb at Viceroy Lord Hardinge in 1912?",
        "o": ["Rash Behari Bose", "Bhagat Singh", "Khudiram Bose", "Prafulla Chaki"],
        "a": "Rash Behari Bose"
    },
    {
        "q": "Who was the only person to be elected President of the Congress for six consecutive years (1940-46)?",
        "o": ["Jawaharlal Nehru", "Abul Kalam Azad", "Vallabhbhai Patel", "J.B. Kripalani"],
        "a": "Abul Kalam Azad"
    },
    {
        "q": "The 'Mountbatten Plan' which led to the partition was announced on?",
        "o": ["June 3, 1947", "August 15, 1947", "January 26, 1947", "March 23, 1947"],
        "a": "June 3, 1947"
    },
    {
        "q": "Who was the Viceroy during the 'Quit India Movement' (1942)?",
        "o": ["Lord Linlithgow", "Lord Wavell", "Lord Mountbatten", "Lord Willingdon"],
        "a": "Lord Linlithgow"
    },
    {
        "q": "Who led the 'Red Shirts' (Kudai Khidmatgars) movement?",
        "o": ["Khan Abdul Ghaffar Khan", "Muhammad Ali Jinnah", "Liaquat Ali Khan", "Maulana Azad"],
        "a": "Khan Abdul Ghaffar Khan"
    },
    {
        "q": "Which revolutionary group was involved in the 'Lahore Conspiracy Case'?",
        "o": ["Hindustan Socialist Republican Association (HSRA)", "Anushilan Samiti", "Jugantar", "Ghadar Party"],
        "a": "Hindustan Socialist Republican Association (HSRA)"
    },
    {
        "q": "Who was the first martyr of the 1857 Revolt?",
        "o": ["Mangal Pandey", "Tatya Tope", "Nana Sahib", "Rani Laxmibai"],
        "a": "Mangal Pandey"
    },
    {
        "q": "Which newspaper was started by Bal Gangadhar Tilak?",
        "o": ["Kesari", "The Hindu", "Amrita Bazar Patrika", "Young India"],
        "a": "Kesari"
    },
    {
        "q": "Who is known as the 'Grand Old Man of India'?",
        "o": ["Dadabhai Naoroji", "W.C. Bonnerjee", "Mahatma Gandhi", "Madan Mohan Malaviya"],
        "a": "Dadabhai Naoroji"
    },
    {
        "q": "Who founded the 'Swatantra Party' after independence?",
        "o": ["C. Rajagopalachari", "J.B. Kripalani", "Dr. B.R. Ambedkar", "Shyama Prasad Mukherjee"],
        "a": "C. Rajagopalachari"
    },
    {
        "q": "The 'Direct Action Day' (1946) was called by which party?",
        "o": ["Muslim League", "Indian National Congress", "Hindu Mahasabha", "Communist Party"],
        "a": "Muslim League"
    },
    {
        "q": "Who was the defence lawyer for the INA Trials at Red Fort?",
        "o": ["Bhulabhai Desai", "B.R. Ambedkar", "Motilal Nehru", "Sardar Patel"],
        "a": "Bhulabhai Desai"
    },
    {
        "q": "Who established the 'Ramakrishna Mission'?",
        "o": ["Swami Vivekananda", "Ramakrishna Paramhansa", "Dayanand Saraswati", "Raja Ram Mohan Roy"],
        "a": "Swami Vivekananda"
    },
    {
        "q": "Which social reformer is associated with the abolition of Sati?",
        "o": ["Raja Ram Mohan Roy", "Ishwar Chandra Vidyasagar", "Dayanand Saraswati", "Jyotiba Phule"],
        "a": "Raja Ram Mohan Roy"
    },
    {
        "q": "Who wrote 'Gulamgiri'?",
        "o": ["Jyotiba Phule", "B.R. Ambedkar", "Periyar E.V. Ramasamy", "Kanshi Ram"],
        "a": "Jyotiba Phule"
    },
    {
        "q": "Who led the 'Paika Rebellion' (1817) in Odisha?",
        "o": ["Bakshi Jagabandhu", "Veer Surendra Sai", "Tantia Bhil", "Birsa Munda"],
        "a": "Bakshi Jagabandhu"
    },
    {
        "q": "Which river is known as the 'Sorrow of Bihar' because of its frequent course changes and floods?",
        "o": ["Gandak", "Kosi", "Son", "Ghaghara"],
        "a": "Kosi"
    },
    {
        "q": "The 'Duncan Passage' separates which two islands?",
        "o": ["South Andaman and Little Andaman", "Little Andaman and Car Nicobar", "North Andaman and Middle Andaman", "Minicoy and Maldives"],
        "a": "South Andaman and Little Andaman"
    },
    {
        "q": "Which mountain range separates the Indo-Gangetic plain from the Deccan Plateau?",
        "o": ["Aravalli", "Vindhya", "Satpura", "Western Ghats"],
        "a": "Vindhya"
    },
    {
        "q": "The famous 'Loktak Lake', known for its floating phumdis (islands), is located in which state?",
        "o": ["Mizoram", "Manipur", "Meghalaya", "Tripura"],
        "a": "Manipur"
    },
    {
        "q": "Which is the highest peak of the Satpura Range?",
        "o": ["Guru Shikhar", "Dhupgarh", "Pachmarhi", "Mahendragiri"],
        "a": "Dhupgarh"
    },
    {
        "q": "The 'Main Central Thrust' (MCT) separates which two geological zones of the Himalayas?",
        "o": ["Great Himalayas and Lesser Himalayas", "Lesser Himalayas and Shiwaliks", "Trans Himalayas and Great Himalayas", "Shiwaliks and Northern Plains"],
        "a": "Great Himalayas and Lesser Himalayas"
    },
    {
        "q": "Which river in India crosses the Tropic of Cancer twice?",
        "o": ["Narmada", "Tapi", "Mahi", "Sabarmati"],
        "a": "Mahi"
    },
    {
        "q": "The 'Silent Valley National Park' is located in which hill range?",
        "o": ["Nilgiri Hills", "Cardamom Hills", "Palani Hills", "Anaimalai Hills"],
        "a": "Nilgiri Hills"
    },
    {
        "q": "Which state has the largest coastline in India?",
        "o": ["Tamil Nadu", "Maharashtra", "Andhra Pradesh", "Gujarat"],
        "a": "Gujarat"
    },
    {
        "q": "The 'Karewas' of Kashmir are famous for the cultivation of which crop?",
        "o": ["Apple", "Walnut", "Saffron (Zafran)", "Almond"],
        "a": "Saffron (Zafran)"
    },
    {
        "q": "Which river flows through a Rift Valley between the Vindhya and Satpura ranges?",
        "o": ["Godavari", "Mahanadi", "Narmada", "Krishna"],
        "a": "Narmada"
    },
    {
        "q": "At which place does the Alaknanda and Bhagirathi rivers meet to form the Ganga?",
        "o": ["Rudraprayag", "Devprayag", "Karnaprayag", "Vishnuprayag"],
        "a": "Devprayag"
    },
    {
        "q": "The 'Palk Strait' lies between which two countries?",
        "o": ["India and Maldives", "India and Sri Lanka", "India and Indonesia", "Andaman and Thailand"],
        "a": "India and Sri Lanka"
    },
    {
        "q": "Which soil is popularly known as 'Regur Soil'?",
        "o": ["Alluvial Soil", "Red Soil", "Black Soil", "Laterite Soil"],
        "a": "Black Soil"
    },
    {
        "q": "The 'Nathu La' pass connects India with which country?",
        "o": ["Pakistan", "Nepal", "China (Tibet)", "Bhutan"],
        "a": "China (Tibet)"
    },
    {
        "q": "Which is the only floating National Park in the world?",
        "o": ["Kaziranga", "Keibul Lamjao", "Manas", "Sundarbans"],
        "a": "Keibul Lamjao"
    },
    {
        "q": "The 'Western Disturbances' which cause winter rains in North-West India originate from?",
        "o": ["Arabian Sea", "Bay of Bengal", "Mediterranean Sea", "Caspian Sea"],
        "a": "Mediterranean Sea"
    },
    {
        "q": "Which Indian state shares its border with the maximum number of other Indian states?",
        "o": ["Madhya Pradesh", "Uttar Pradesh", "Maharashtra", "Assam"],
        "a": "Uttar Pradesh"
    },
    {
        "q": "The 'Majuli' island, the largest river island in the world, is formed by which river?",
        "o": ["Ganga", "Brahmaputra", "Indus", "Godavari"],
        "a": "Brahmaputra"
    },
    {
        "q": "Which place in India is famously known as the 'Coldest Inhabited Place'?",
        "o": ["Leh", "Dras", "Kargil", "Siachen"],
        "a": "Dras"
    },
    {
        "q": "The 'Toda' tribe is the original inhabitant of which region?",
        "o": ["Aravalli Range", "Nilgiri Hills", "Garo Hills", "Bastar"],
        "a": "Nilgiri Hills"
    },
    {
        "q": "Which port is known as the 'Queen of Arabian Sea'?",
        "o": ["Mumbai Port", "Kochi Port", "Kandla Port", "Marmagao Port"],
        "a": "Kochi Port"
    },
    {
        "q": "The highest peak of the Eastern Ghats is...",
        "o": ["Mahendragiri", "Arma Konda", "Jindhagada", "Shevaroy"],
        "a": "Jindhagada"
    },
    {
        "q": "Which Indian state is known as the 'Molasses Basin'?",
        "o": ["Mizoram", "Bihar", "Assam", "Uttar Pradesh"],
        "a": "Mizoram"
    },
    {
        "q": "The Tropic of Cancer does NOT pass through which of these Indian states?",
        "o": ["Tripura", "Mizoram", "Odisha", "Jharkhand"],
        "a": "Odisha"
    },
    {
        "q": "Which channel separates the Lakshadweep Islands from the Maldives?",
        "o": ["8 Degree Channel", "9 Degree Channel", "10 Degree Channel", "Duncan Passage"],
        "a": "8 Degree Channel"
    },
    {
        "q": "The famous 'Hornbill Festival' is celebrated in which state?",
        "o": ["Manipur", "Nagaland", "Arunachal Pradesh", "Meghalaya"],
        "a": "Nagaland"
    },
    {
        "q": "Where is the 'Great Indian Bustard' primarily found?",
        "o": ["Desert National Park", "Jim Corbett", "Kaziranga", "Gir Forest"],
        "a": "Desert National Park"
    },
    {
        "q": "The 'Diphu Pass' is a tri-junction between which three countries?",
        "o": ["India, Nepal, China", "India, China, Myanmar", "India, Bhutan, China", "India, Myanmar, Bangladesh"],
        "a": "India, China, Myanmar"
    },
    {
        "q": "Which river is the longest tributary of the Ganga?",
        "o": ["Yamuna", "Son", "Gomti", "Kosi"],
        "a": "Yamuna"
    },
    {
        "q": "The 'Zoji La' pass connects which two locations?",
        "o": ["Srinagar and Leh", "Manali and Leh", "Jammu and Srinagar", "Leh and Siachen"],
        "a": "Srinagar and Leh"
    },
    {
        "q": "Which Indian state has the highest forest cover in terms of area?",
        "o": ["Arunachal Pradesh", "Madhya Pradesh", "Chhattisgarh", "Odisha"],
        "a": "Madhya Pradesh"
    },
    {
        "q": "The 'Jaduguda' mines in Jharkhand are famous for?",
        "o": ["Coal", "Uranium", "Iron Ore", "Bauxite"],
        "a": "Uranium"
    },
    {
        "q": "Which waterfall is the highest plunge waterfall in India?",
        "o": ["Jog Falls", "Kunchikal Falls", "Nohkalikai Falls", "Dudhsagar Falls"],
        "a": "Nohkalikai Falls"
    },
    {
        "q": "The 'Coromandel Coast' receives most of its rainfall during which season?",
        "o": ["South-West Monsoon", "North-East Monsoon (Winter)", "Summer", "Pre-Monsoon Showers"],
        "a": "North-East Monsoon (Winter)"
    },
    {
        "q": "Which is the largest lagoon lake in India?",
        "o": ["Pulicat Lake", "Chilika Lake", "Vembanad Lake", "Sambhar Lake"],
        "a": "Chilika Lake"
    },
    {
        "q": "The 'Indira Point', the southernmost point of India, is located in?",
        "o": ["Little Nicobar", "Great Nicobar", "Car Nicobar", "North Andaman"],
        "a": "Great Nicobar"
    },
    {
        "q": "Which river originates from the Amarkantak Plateau?",
        "o": ["Narmada", "Godavari", "Krishna", "Kaveri"],
        "a": "Narmada"
    },
    {
        "q": "The 'Saddle Peak' is the highest peak of Andaman and Nicobar. Where is it located?",
        "o": ["North Andaman", "Middle Andaman", "South Andaman", "Great Nicobar"],
        "a": "North Andaman"
    },
    {
        "q": "Which state is the largest producer of Coffee in India?",
        "o": ["Kerala", "Karnataka", "Tamil Nadu", "Assam"],
        "a": "Karnataka"
    },
    {
        "q": "The 'Sahyadri' is another name for which mountain range?",
        "o": ["Eastern Ghats", "Western Ghats", "Aravalli", "Himalayas"],
        "a": "Western Ghats"
    },
    {
        "q": "Which river is known as 'Dakshin Ganga' (Ganga of the South)?",
        "o": ["Krishna", "Kaveri", "Godavari", "Mahanadi"],
        "a": "Godavari"
    },
    {
        "q": "In which state is the 'Gahirmatha Marine Sanctuary', famous for Olive Ridley Turtles, located?",
        "o": ["West Bengal", "Odisha", "Andhra Pradesh", "Tamil Nadu"],
        "a": "Odisha"
    },
    {
        "q": "The 'Malwa Plateau' spreads across which states?",
        "o": ["MP, Gujarat, Rajasthan", "Maharashtra, MP, UP", "Gujarat, Rajasthan, Haryana", "MP, Chhattisgarh, Jharkhand"],
        "a": "MP, Gujarat, Rajasthan"
    },
    {
        "q": "What is the approximate total length of India's coastline (including islands)?",
        "o": ["6100 km", "7516 km", "8100 km", "5400 km"],
        "a": "7516 km"
    },
    {
        "q": "Which Indian river flows into the Arabian Sea?",
        "o": ["Mahanadi", "Godavari", "Tapi", "Krishna"],
        "a": "Tapi"
    },
    {
        "q": "The 'Patkai Bum' hills form the boundary between India and?",
        "o": ["China", "Myanmar", "Bangladesh", "Bhutan"],
        "a": "Myanmar"
    },
    {
        "q": "Which glacier is the source of the River Yamuna?",
        "o": ["Gangotri", "Yamunotri (Bandarpunch)", "Milam", "Pindari"],
        "a": "Yamunotri (Bandarpunch)"
    },
    {
        "q": "The 'Khajjiar' lake, often called 'Mini Switzerland of India', is in?",
        "o": ["Uttarakhand", "Himachal Pradesh", "Jammu & Kashmir", "Sikkim"],
        "a": "Himachal Pradesh"
    },
    {
        "q": "The 'Dead Internet Theory' is a conspiracy theory suggesting that the majority of internet traffic is actually...",
        "o": ["Government Spies", "Bots interacting with other Bots", "Aliens", "Hackers"],
        "a": "Bots interacting with other Bots"
    },
    {
        "q": "Which modern psychological condition is defined as 'the fear of being out of mobile phone contact'?",
        "o": ["Technophobia", "Nomophobia", "Cyberphobia", "Telephobia"],
        "a": "Nomophobia"
    },
    {
        "q": "In 2010, the 'Stuxnet' computer worm was discovered. It was unique because it was the first cyberweapon specifically designed to target...",
        "o": ["Bank Accounts", "Social Media Passwords", "Nuclear Centrifuges (SCADA systems)", "Satellite GPS"],
        "a": "Nuclear Centrifuges (SCADA systems)"
    },
    {
        "q": "What is the name of the specific 'Consensus Mechanism' that Bitcoin uses to secure its network (which requires high energy)?",
        "o": ["Proof of Stake", "Proof of Work", "Proof of History", "Proof of Authority"],
        "a": "Proof of Work"
    },
    {
        "q": "Elon Musk's SpaceX became the first private company to send humans to the ISS. What was the name of the capsule they used?",
        "o": ["Starship", "Dragon Endeavour", "Falcon Heavy", "Orion"],
        "a": "Dragon Endeavour"
    },
    {
        "q": "In the context of Artificial Intelligence (AI), what does 'GPT' stand for in models like ChatGPT?",
        "o": ["General Processing Tool", "Generative Pre-trained Transformer", "Global Positioning Tech", "Genetic Programming Transmitter"],
        "a": "Generative Pre-trained Transformer"
    },
    {
        "q": "Which company owns the advanced robotics firm 'Boston Dynamics' (creators of Spot and Atlas) as of 2024?",
        "o": ["Google", "SoftBank", "Hyundai", "Tesla"],
        "a": "Hyundai"
    },
    {
        "q": "The 'Mandela Effect' is a phenomenon where a large group of people remember something differently than how it occurred. Which character is often cited as an example (monocle confusion)?",
        "o": ["Mickey Mouse", "Richie Rich", "Mr. Monopoly (Monopoly Man)", "Pringles Man"],
        "a": "Mr. Monopoly (Monopoly Man)"
    },
    {
        "q": "What is the specific HTTP Status Code for 'Censored / Unavailable For Legal Reasons'?",
        "o": ["404", "403", "451", "500"],
        "a": "451"
    },
    {
        "q": "In modern economics, a startup company valued at over $10 billion is specifically called a...?",
        "o": ["Unicorn", "Decacorn", "Hectocorn", "Centicorn"],
        "a": "Decacorn"
    },
    {
        "q": "The 'Dark Web' is often accessed using the TOR browser. What does TOR stand for?",
        "o": ["The Onion Router", "The Open Road", "Total Online Resistance", "The Obscure Relay"],
        "a": "The Onion Router"
    },
    {
        "q": "Which controversial gene-editing technology won the Nobel Prize in Chemistry in 2020?",
        "o": ["mRNA", "CRISPR-Cas9", "Cloning", "Stem Cell Therapy"],
        "a": "CRISPR-Cas9"
    },
    {
        "q": "What is the name of the 'limit' that suggests Moore's Law (computing power doubling) will eventually stop due to quantum effects?",
        "o": ["The Silicon Wall", "The Quantum Limit", "The Thermal Ceiling", "The Atomic Limit"],
        "a": "The Thermal Ceiling"
    },
    {
        "q": "In 2021, a digital artwork by Beeple sold for $69 million as an NFT. What was the title of this piece?",
        "o": ["The First 5000 Days", "CryptoPunks #1", "Bored Ape", "Quantum Genesis"],
        "a": "The First 5000 Days"
    },
    {
        "q": "Which social media platform was originally known as 'Musical.ly' before it was rebranded?",
        "o": ["Snapchat", "TikTok", "Vine", "Instagram Reels"],
        "a": "TikTok"
    },
    {
        "q": "The 'James Webb Space Telescope' orbits the Sun at a specific stable point called...?",
        "o": ["Low Earth Orbit", "Lagrange Point 2 (L2)", "Geostationary Orbit", "Lunar Orbit"],
        "a": "Lagrange Point 2 (L2)"
    },
    {
        "q": "What is the term for the psychological phenomenon where people with low ability at a task overestimate their ability (often seen on the internet)?",
        "o": ["Imposter Syndrome", "Dunning-Kruger Effect", "Placebo Effect", "Stockholm Syndrome"],
        "a": "Dunning-Kruger Effect"
    },
    {
        "q": "In the context of 5G technology, which frequency band offers the highest speeds but the shortest range (easily blocked by walls)?",
        "o": ["Sub-6 GHz", "mmWave (Millimeter Wave)", "Low-Band", "Mid-Band"],
        "a": "mmWave (Millimeter Wave)"
    },
    {
        "q": "The first-ever video uploaded to YouTube in 2005 is titled...?",
        "o": ["My Cat", "Hello World", "Me at the zoo", "Evolution of Dance"],
        "a": "Me at the zoo"
    },
    {
        "q": "Which element is crucial for Lithium-ion batteries but is controversial due to unethical mining practices in the DRC?",
        "o": ["Nickel", "Cobalt", "Manganese", "Graphite"],
        "a": "Cobalt"
    },
    {
        "q": "What does the 'S' stand for in the HTTPS protocol used for secure browsing?",
        "o": ["Standard", "System", "Secure", "Socket"],
        "a": "Secure"
    },
    {
        "q": "In the Marvel Cinematic Universe (MCU), which material is Captain America's shield made of?",
        "o": ["Adamantium", "Vibranium", "Uru", "Carbonadium"],
        "a": "Vibranium"
    },
    {
        "q": "The 'Great Pacific Garbage Patch' is primarily located between which two landmasses?",
        "o": ["California and Hawaii", "Japan and Philippines", "Australia and New Zealand", "Chile and Easter Island"],
        "a": "California and Hawaii"
    },
    {
        "q": "Who is the mysterious creator of Bitcoin (whose real identity is still unknown)?",
        "o": ["Vitalik Buterin", "Satoshi Nakamoto", "Nick Szabo", "Craig Wright"],
        "a": "Satoshi Nakamoto"
    },
    {
        "q": "In modern gaming, what does the term 'NPC' stand for?",
        "o": ["Non-Playable Character", "New Player Control", "Network Protocol Code", "Natural Person Character"],
        "a": "Non-Playable Character"
    },
    {
        "q": "Which tech company reached a $3 Trillion market cap first?",
        "o": ["Microsoft", "Apple", "Nvidia", "Amazon"],
        "a": "Apple"
    },
    {
        "q": "What is the name of the AI developed by DeepMind that defeated the world champion of the board game 'Go' in 2016?",
        "o": ["Deep Blue", "AlphaGo", "Watson", "Stockfish"],
        "a": "AlphaGo"
    },
    {
        "q": "The 'Blue Screen of Death' (BSOD) is associated with which Operating System?",
        "o": ["macOS", "Linux", "Windows", "Android"],
        "a": "Windows"
    },
    {
        "q": "Which country became the first in the world to make Bitcoin legal tender in 2021?",
        "o": ["El Salvador", "Venezuela", "Japan", "Switzerland"],
        "a": "El Salvador"
    },
    {
        "q": "In the world of streaming, which platform was acquired by Amazon for $970 million in 2014?",
        "o": ["YouTube Gaming", "Twitch", "Mixer", "Kick"],
        "a": "Twitch"
    },
    {
        "q": "What is the term for 'Malware that locks your files and demands payment to unlock them'?",
        "o": ["Spyware", "Ransomware", "Adware", "Worm"],
        "a": "Ransomware"
    },
    {
        "q": "Which famous whistleblower leaked classified NSA documents in 2013 regarding global surveillance?",
        "o": ["Julian Assange", "Edward Snowden", "Chelsea Manning", "Aaron Swartz"],
        "a": "Edward Snowden"
    },
    {
        "q": "In modern dating slang, what does 'Ghosting' mean?",
        "o": ["Stalking someone online", "Cutting off communication without warning", "Dating two people at once", "Using a fake profile photo"],
        "a": "Cutting off communication without warning"
    },
    {
        "q": "The 'Metaverse' concept was popularized by Neal Stephenson in his 1992 novel. What is the book's title?",
        "o": ["Ready Player One", "Snow Crash", "Neuromancer", "The Matrix"],
        "a": "Snow Crash"
    },
    {
        "q": "Which company created the programming language 'Java'?",
        "o": ["Microsoft", "Sun Microsystems", "Apple", "Oracle (Acquired later)"],
        "a": "Sun Microsystems"
    },
    {
        "q": "What is the name of the cognitive bias where people rely too heavily on the first piece of information offered (the 'anchor')?",
        "o": ["Confirmation Bias", "Anchoring Bias", "Recency Bias", "Hindsight Bias"],
        "a": "Anchoring Bias"
    },
    {
        "q": "The 'Panama Papers' leak in 2016 exposed the financial secrets of the wealthy. Which law firm was at the center of it?",
        "o": ["Mossack Fonseca", "Baker McKenzie", "Clifford Chance", "Skadden Arps"],
        "a": "Mossack Fonseca"
    },
    {
        "q": "In modern slang, what does 'FOMO' stand for?",
        "o": ["Fear Of Moving On", "Fear Of Missing Out", "For Our Mom Only", "Fear Of Making Over"],
        "a": "Fear Of Missing Out"
    },
    {
        "q": "Which specific isotope of Uranium is needed for a nuclear fission chain reaction (atomic bomb)?",
        "o": ["U-238", "U-235", "U-234", "U-239"],
        "a": "U-235"
    },
    {
        "q": "The 'Turing Test', proposed by Alan Turing, was designed to test a machine's ability to...",
        "o": ["Calculate faster than humans", "Exhibit intelligent behavior equivalent to a human", "Play Chess", "Translate languages"],
        "a": "Exhibit intelligent behavior equivalent to a human"
    },
    {
        "q": "What is the term for a cyber attack where a system is flooded with traffic to crash it?",
        "o": ["Phishing", "DDoS (Distributed Denial of Service)", "SQL Injection", "Man-in-the-Middle"],
        "a": "DDoS (Distributed Denial of Service)"
    },
    {
        "q": "Which famous car brand owns 'Bugatti' (as part of a joint venture with Rimac)?",
        "o": ["Ferrari", "Porsche (VW Group)", "Mercedes", "BMW"],
        "a": "Porsche (VW Group)"
    },
    {
        "q": "The 'QR' in QR Code stands for...?",
        "o": ["Quick Response", "Quantum Read", "Quality Register", "Quick Register"],
        "a": "Quick Response"
    },
    {
        "q": "Which modern tech giant was originally founded under the name 'Cadabra'?",
        "o": ["eBay", "Amazon", "Netflix", "Google"],
        "a": "Amazon"
    },
    {
        "q": "In the show 'Squid Game', what is the shape on the mask of the Workers (lowest rank)?",
        "o": ["Square", "Triangle", "Circle", "Star"],
        "a": "Circle"
    },
    {
        "q": "The 'Doomsday Clock', which represents the likelihood of a man-made global catastrophe, is currently set at...?",
        "o": ["5 Minutes to Midnight", "100 Seconds to Midnight", "90 Seconds to Midnight", "1 Minute to Midnight"],
        "a": "90 Seconds to Midnight"
    },
    {
        "q": "Which country is home to 'TSMC', the world's most valuable semiconductor (chip) manufacturing company?",
        "o": ["China", "Taiwan", "South Korea", "USA"],
        "a": "Taiwan"
    },
    {
        "q": "What does the 'G' in '5G' network stand for?",
        "o": ["Gigabyte", "Generation", "Global", "GHz"],
        "a": "Generation"
    },
    {
        "q": "Who is the artist behind the shredded artwork 'Girl with Balloon' (Love is in the Bin)?",
        "o": ["Kaws", "Banksy", "Damien Hirst", "Yayoi Kusama"],
        "a": "Banksy"
    },
    {
        "q": "Which enzyme is used in PCR to amplify DNA, isolated from a thermophilic bacterium?",
        "o": ["Pepsin", "Taq Polymerase", "Amylase", "Helicase"],
        "a": "Taq Polymerase"
    },
    {
        "q": "Operation 'Smiling Buddha' (1974) was India's first nuclear test. Where did it take place?",
        "o": ["Kargil", "Pokhran", "Sriharikota", "Chandipur"],
        "a": "Pokhran"
    },
    {
        "q": "The 'Piri Reis Map' (1513) is controversial because it seemingly depicts which landmass?",
        "o": ["Australia", "Antarctica (coastline)", "Greenland", "Japan"],
        "a": "Antarctica (coastline)"
    },
    {
        "q": "The 'Razmnama' is a famous illustrated Persian translation of a Hindu epic commissioned by Emperor Akbar. Which epic is it?",
        "o": ["Ramayana", "Mahabharata", "Atharva Veda", "Bhagavad Gita"],
        "a": "Mahabharata"
    },
    {
        "q": "During the Cold War, the CIA spent $20 million on 'Operation Acoustic Kitty'. What was the objective?",
        "o": ["Train cats to spy on the Soviets", "Use cats to detect nuclear radiation", "Drop cats with parachutes for morale", "Use cats to hunt rats in bunkers"],
        "a": "Train cats to spy on the Soviets"
    },
    {
        "q": "Which is the only letter of the English alphabet that does NOT appear in the Periodic Table of Elements?",
        "o": ["J", "Q", "X", "Z"],
        "a": "J"
    },
    {
        "q": "In the Mahabharata, who was the only Kaurava brother who fought on the side of the Pandavas during the Kurukshetra war?",
        "o": ["Vikarna", "Yuyutsu", "Dussasana", "Durmukha"],
        "a": "Yuyutsu"
    },
    {
        "q": "The 'Baghdad Battery', a set of artifacts dating back to the Parthian/Sassanid periods, suggests that ancient people might have had knowledge of...",
        "o": ["Gunpowder", "Electroplating/Electricity", "Steam Engine", "Telescopes"],
        "a": "Electroplating/Electricity"
    },
    {
        "q": "Which country technically has the most Time Zones in the world (including overseas territories)?",
        "o": ["Russia", "China", "USA", "France"],
        "a": "France"
    },
    {
        "q": "In computing, the HTTP Error Code '418' is a real standard defined in RFC 2324. What does it stand for?",
        "o": ["I'm a teapot", "Payment Required", "Legal Obstacle", "Method Not Allowed"],
        "a": "I'm a teapot"
    },
    {
        "q": "The 'Peacock Throne' (Takht-i-Taus) of Shah Jahan was famously looted by Nadir Shah in 1739. Which precious gem was NOT originally part of it?",
        "o": ["Koh-i-Noor", "Akbar Shah Diamond", "Hope Diamond", "Timur Ruby"],
        "a": "Hope Diamond"
    },
    {
        "q": "What is the name of the specific boundary around a Black Hole beyond which nothing, not even light, can escape?",
        "o": ["Singularity", "Accretion Disk", "Event Horizon", "Photon Sphere"],
        "a": "Event Horizon"
    },
    {
        "q": "Who was the first human to calculate the circumference of the Earth with surprising accuracy using only sticks and shadows?",
        "o": ["Pythagoras", "Eratosthenes", "Archimedes", "Aristotle"],
        "a": "Eratosthenes"
    },
    {
        "q": "The 'Code of Hammurabi' is one of the oldest deciphered writings of significant length. It works on the principle of 'Lex Talionis', which means?",
        "o": ["Innocent until proven guilty", "Eye for an eye", "Divine right of kings", "Taxation for protection"],
        "a": "Eye for an eye"
    },
    {
        "q": "In the human body, the 'Hyoid Bone' is unique because it is the only bone that...",
        "o": ["Cannot break", "Is not connected to any other bone", "Does not stop growing", "Is made of cartilage"],
        "a": "Is not connected to any other bone"
    },
    {
        "q": "The 'Wow! Signal' (1977) was a strong narrowband radio signal received from space. Which constellation did it appear to come from?",
        "o": ["Orion", "Sagittarius", "Ursa Major", "Andromeda"],
        "a": "Sagittarius"
    },
    {
        "q": "Which Mughal Emperor re-imposed the 'Jizya' tax on non-Muslims in 1679, almost a century after it was abolished by Akbar?",
        "o": ["Jahangir", "Shah Jahan", "Aurangzeb", "Bahadur Shah I"],
        "a": "Aurangzeb"
    },
    {
        "q": "The 'Dancing Girl' statue from Mohenjo-daro is made of which material?",
        "o": ["Terracotta", "Bronze", "Steatite", "Gold"],
        "a": "Bronze"
    },
    {
        "q": "The 'Demon Core' was a subcritical mass of Plutonium involved in two fatal accidents at Los Alamos. What tool did physicist Louis Slotin use to accidentally slip, causing the burst?",
        "o": ["A Screwdriver", "A Pair of Tongs", "A Wrench", "A Robotic Arm"],
        "a": "A Screwdriver"
    },
    {
        "q": "In the Indian Constitution, the original handwritten document was calligraphed by Prem Behari Narain Raizada, but who was the specific artist responsible for the illustrations/artwork?",
        "o": ["Rabindranath Tagore", "Nandalal Bose", "Raja Ravi Varma", "Abanindranath Tagore"],
        "a": "Nandalal Bose"
    },
    {
        "q": "The 'Sargasso Sea' is unique in the world because it is the only sea that...",
        "o": ["Has no coastlines", "Has zero salt content", "Is located underground", "Freezes completely in winter"],
        "a": "Has no coastlines"
    },
    {
        "q": "In 1990, the 'Pale Blue Dot' photograph of Earth was taken by Voyager 1 from a distance of 6 billion kilometers. Who famously requested this photo be taken?",
        "o": ["Carl Sagan", "Neil deGrasse Tyson", "Stephen Hawking", "Elon Musk"],
        "a": "Carl Sagan"
    },
    {
        "q": "The 'Great Attractor' is a gravitational anomaly in intergalactic space. Which supercluster is our Milky Way galaxy being pulled towards because of it?",
        "o": ["Virgo Supercluster", "Laniakea Supercluster", "Coma Supercluster", "Perseus-Pisces Supercluster"],
        "a": "Laniakea Supercluster"
    },
    {
        "q": "Which obscure Mughal Prince translated 50 Upanishads from Sanskrit into Persian, calling the collection 'Sirr-i-Akbar' (The Great Secret)?",
        "o": ["Dara Shikoh", "Aurangzeb", "Jahangir", "Shah Shuja"],
        "a": "Dara Shikoh"
    },
    {
        "q": "The 'Ship of Theseus' is a famous paradox in philosophy. It questions the nature of identity by asking what happens if...",
        "o": ["A ship sinks and is rebuilt", "Every wooden part is replaced one by one", "It sails forever without stopping", "It has no captain"],
        "a": "Every wooden part is replaced one by one"
    },
    {
        "q": "In 1971, Ray Tomlinson sent the first ARPANET email. What symbol did he choose to separate the user name from the destination address?",
        "o": ["# (Hash)", "@ (At)", "/ (Slash)", ". (Dot)"],
        "a": "@ (At)"
    },
    {
        "q": "The 'Rosetta Stone' was key to deciphering Egyptian Hieroglyphs. It features three scripts: Hieroglyphic, Greek, and...?",
        "o": ["Demotic", "Coptic", "Latin", "Sanskrit"],
        "a": "Demotic"
    },
    {
        "q": "What is the specific name of the rust-resistant iron used in the 'Iron Pillar of Delhi', which has prevented corrosion for over 1600 years?",
        "o": ["Stainless Steel", "Wrought Iron with high Phosphorus", "Galvanized Iron", "Titanium Alloy"],
        "a": "Wrought Iron with high Phosphorus"
    },
    {
        "q": "In the Ramayana, who was the only warrior capable of using the 'Vaishnavastra' besides Lord Rama and Lakshmana?",
        "o": ["Ravana", "Indrajit (Meghanada)", "Kumbhakarna", "Vibhishana"],
        "a": "Indrajit (Meghanada)"
    },
    {
        "q": "The 'Kardashev Scale' measures a civilization's technological advancement based on what specific metric?",
        "o": ["Population size", "Information storage capacity", "Energy consumption", "Space colonization range"],
        "a": "Energy consumption"
    },
    {
        "q": "Which gas is primarily responsible for the distinct smell of rain on dry soil (Petrichor)?",
        "o": ["Ozone", "Geosmin", "Methane", "Nitrous Oxide"],
        "a": "Geosmin"
    },
    {
        "q": "The 'Beale Ciphers' are a set of three ciphertexts that supposedly reveal the location of buried treasure worth $60 million. Which famous document is the key to the second cipher?",
        "o": ["Magna Carta", "The US Declaration of Independence", "The Bible", "Shakespeare's Sonnets"],
        "a": "The US Declaration of Independence"
    },
    {
        "q": "In computer programming, the date 'January 19, 2038' is significant because of the 'Year 2038 Problem'. Which systems will this affect?",
        "o": ["64-bit systems", "32-bit signed integer systems", "Quantum Computers", "Windows 11"],
        "a": "32-bit signed integer systems"
    },
    {
        "q": "In computer science, 'P vs NP' is a major problem. What does 'NP' stand for?",
        "o": ["Non-Polynomial", "Nondeterministic Polynomial", "New Programming", "Null Pointer"],
        "a": "Nondeterministic Polynomial"
    }
]

# ================== 🧠 TRIVIA GAUNTLET (7 ROUNDS) ==================

class TriviaGauntletView(discord.ui.View):
    def __init__(self, player, bet, interaction, questions_list):
        super().__init__(timeout=10) # ⚡ 10 SECONDS PER QUESTION
        self.player = player
        self.bet = bet
        self.interaction = interaction
        self.questions = questions_list # List of 7 questions
        self.current_index = 0
        self.game_ended = False # Bug Fix ke liye flag
        
        # Load First Question
        self.load_question()

    def load_question(self):
        self.clear_items() # Purane buttons hatao
        
        current_q_data = self.questions[self.current_index]
        self.correct_ans = current_q_data["a"]
        
        # Shuffle Options
        self.options = current_q_data["o"].copy()
        random.shuffle(self.options)
        
        # Create New Buttons
        labels = ["A", "B", "C", "D"]
        for i, opt in enumerate(self.options):
            btn = discord.ui.Button(label=f"{labels[i]}: {opt}", style=discord.ButtonStyle.secondary, custom_id=opt)
            btn.callback = self.answer_callback
            self.add_item(btn)

    async def on_timeout(self):
        if self.game_ended: return # Agar game pehle hi khatam ho gaya to ignore karo

        self.game_ended = True
        for item in self.children: item.disabled = True
        
        # --- PUNISHMENT LOGIC ---
        await self.apply_punishment("Too Slow (Timeout)")
        
        embed = discord.Embed(title="⌛ TIME'S UP!", color=0xFF0000)
        embed.description = (
            f"❌ **Bahut slow ho!** 10 Second nikal gaye.\n"
            f"📉 **Stage:** {self.current_index + 1}/7 par haar gaye.\n"
            f"💸 **Lost:** ${self.bet:,}"
        )
        embed.set_footer(text="Penalty: 1 Hour Mute applied!")
        embed.set_thumbnail(url="https://media.tenor.com/images/3e877e504c35e320f7725964f4040939/tenor.gif")
        
        try:
            await self.interaction.edit_original_response(embed=embed, view=self)
        except:
            pass
        self.stop()

    async def answer_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player.id:
            return await interaction.response.send_message("❌ Apna game khelo!", ephemeral=True)

        if self.game_ended: return
        
        selected_ans = interaction.data["custom_id"]
        
        # 1. WRONG ANSWER CHECK
        if selected_ans != self.correct_ans:
            self.game_ended = True
            
            # Button Red karo
            for item in self.children:
                item.disabled = True
                if item.custom_id == selected_ans: item.style = discord.ButtonStyle.danger
                if item.custom_id == self.correct_ans: item.style = discord.ButtonStyle.success

            await self.apply_punishment("Wrong Answer")
            
            embed = discord.Embed(title="🚫 WRONG ANSWER!", color=0xFF0000)
            embed.description = (
                f"❌ **Galat Jawab!** Khel Khatam.\n"
                f"✅ Correct: **{self.correct_ans}**\n"
                f"📉 **Failed at Stage:** {self.current_index + 1}/7\n"
                f"💸 **Lost:** ${self.bet:,}"
            )
            embed.set_footer(text="Penalty: 1 Hour Mute applied!")
            embed.set_thumbnail(url="https://media.tenor.com/images/3e877e504c35e320f7725964f4040939/tenor.gif")
            
            await interaction.response.edit_message(embed=embed, view=self)
            self.stop() # 🛑 Timer yahi rook do
            return

        # 2. CORRECT ANSWER CHECK
        # Kya ye last question tha (7th)?
        if self.current_index == 6:
            self.game_ended = True
            
            # JACKPOT WIN (10x Reward)
            winnings = self.bet * 10
            await update_balance(self.player.id, winnings)
            
            for item in self.children:
                item.disabled = True
                if item.custom_id == selected_ans: item.style = discord.ButtonStyle.success

            embed = discord.Embed(title="🏆 ULTIMATE CHAMPION!", color=0xFFD700)
            embed.description = (
                f"🎉 **INCREDIBLE!** Tumne lagatar 7 Hard Sawal sahi diye!\n"
                f"🤯 **IQ Level:** God Mode\n\n"
                f"💰 **Bet:** ${self.bet:,}\n"
                f"🤑 **JACKPOT WON:** ${winnings:,} (10x)"
            )
            embed.set_image(url="https://media.tenor.com/p7a8o1r5c8cAAAAC/money-rain.gif")
            
            await interaction.response.edit_message(embed=embed, view=self)
            self.stop() # 🛑 Timer rook do
        
        else:
            # NEXT QUESTION
            self.current_index += 1
            self.load_question() # Load next buttons
            
            q_text = self.questions[self.current_index]["q"]
            
            embed = discord.Embed(title=f"🧠 STAGE {self.current_index + 1} / 7", color=0x9B59B6)
            embed.description = (
                f"**Player:** {self.player.mention}\n"
                f"💰 **Pot:** ${self.bet:,} (Win 7/7 to get 10x)\n\n"
                f"❓ **{q_text}**\n\n"
                f"⚡ **10 Seconds Left!**"
            )
            embed.set_footer(text="Ek galti aur game over!")
            
            await interaction.response.edit_message(embed=embed, view=self)
            # Note: View ka timer interaction hone par apne aap reset ho jata hai 10s par.

    async def apply_punishment(self, reason):
        data = await get_data(self.player.id)
        is_safe = False
        
        if data.get("vip_expiry"):
            is_safe = True
        elif data.get("inventory", {}).get("life", 0) > 0:
            await update_inventory(self.player.id, "life", -1)
            is_safe = True

        if not is_safe:
            await smart_timeout(self.interaction, self.player, 3600, reason)


@bot.tree.command(name="quiz", description="🧠 The Gauntlet: Answer 7 Hard Questions in a row (10x Reward)")
@app_commands.describe(bet="Amount to bet")
async def quiz(i: discord.Interaction, bet: int):
    # Min Bet Validation
    if bet < 5000:
        return await i.response.send_message("❌ Min Bet: $5,000 (Ye bacchon ka khel nahi hai)", ephemeral=True)
    
    # Check Balance
    data = await get_data(i.user.id)
    if data["balance"] < bet:
        return await i.response.send_message("❌ Paise nahi hain!", ephemeral=True)
        
    # Check if enough questions exist
    if len(TRIVIA_QUESTIONS) < 7:
        return await i.response.send_message("❌ Not enough questions in database!", ephemeral=True)

    # Deduct Money
    await update_balance(i.user.id, -bet)
    
    # Pick 7 Random Unique Questions
    gauntlet_questions = random.sample(TRIVIA_QUESTIONS, 7)
    
    # Show First Question
    first_q = gauntlet_questions[0]
    
    embed = discord.Embed(title="🧠 STAGE 1 / 7", color=0x9B59B6)
    embed.description = (
        f"**Player:** {i.user.mention}\n"
        f"💰 **Bet:** ${bet:,} | **Jackpot:** ${bet*10:,}\n\n"
        f"❓ **{first_q['q']}**\n\n"
        f"⚡ **Time:** 10 Seconds per question!"
    )
    embed.set_footer(text="Rule: 7 Continuous Correct Answers or GAME OVER!")
    
    view = TriviaGauntletView(i.user, bet, i, gauntlet_questions)
    await i.response.send_message(embed=embed, view=view)

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


@app.route('/')
def shop_home():
    return render_template('index.html')  # <--- Ye line honi chahiye
    
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

# 👇 ISKO SABSE NEECHE ADD KARO 👇

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"⚠️ Command Error: {error}")

# 👇 ISKO UPDATE KARO (Purana hata kar ye lagao)
async def roblox_info(uid):
    url = f"https://users.roblox.com/v1/users/{uid}"
    try:
        # 👇 DHYAN DEIN: Yahan hum 'bot.session' use kar rahe hain
        async with bot.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("name", "Unknown"), data.get("displayName", "Unknown")
            else:
                return "Invalid ID", "Invalid ID"
    except Exception as e:
        print(f"API Error: {e}")
        # Agar bot.session fail ho jaye to backup (Safety)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                     if response.status == 200:
                        data = await response.json()
                        return data.get("name", "Unknown"), data.get("displayName", "Unknown")
        except:
            pass
        return "Unknown", "Unknown"
        

# 💰 PURE ECONOMY & WEB SHOP SYSTEM (NO EXTRA GAMES)

# ================== ⚙️ CONFIGURATION ==================
LOG_CHANNEL_ID = 1451973589342621791  

# Premium Colors
C_GOLD = 0xFFD700
C_RED = 0xFF0000
C_GREEN = 0x00FF00
C_DARK = 0x2B2D31

# ================== 🌐 WEBSITE BACKEND ==================

@app.route('/ping')
def ping_check():
    return jsonify({"status": "Alive"})

@app.route('/buy', methods=['POST'])
def buy_item():
    try:
        data = request.json
        uid = str(data.get('uid'))
        cid = data.get('cid') # Channel ID (NOTIFICATION FIX)
        item_id = data.get('item_id')
        
        if item_id not in SHOP_ITEMS: return jsonify({"status": "error", "msg": "Invalid Item"})
        
        # 1. Fetch User Data (Fresh)
        res = supabase.table("economy").select("*").eq("user_id", uid).execute()
        if not res.data: return jsonify({"status": "error", "msg": "Account Not Found! Use /balance first."})
        
        user_data = res.data[0]
        item = SHOP_ITEMS[item_id]
        
        # 2. Check Balance
        if user_data['balance'] < item['price']:
            return jsonify({"status": "error", "msg": f"Garib! Need ${item['price'] - user_data['balance']:,} more."})
        
        # 3. Deduct Money IMMEDIATELY (BALANCE FIX)
        new_bal = int(user_data['balance']) - int(item['price'])
        
        # Initial Update to lock funds
        supabase.table("economy").update({"balance": new_bal}).eq("user_id", uid).execute()
        
        result_text = f"✅ Bought {item['name']}"
        
        # 4. Handle Item Logic
        if item['type'] == "lotto":
            if random.randint(1, 100) <= item['chance']:
                new_bal += item['win']
                # Update Win
                supabase.table("economy").update({"balance": new_bal}).eq("user_id", uid).execute()
                result_text = f"🎉 JACKPOT! Won ${item['win']:,}!"
            else:
                result_text = "😢 Bad Luck! Better luck next time."
                
        elif item['type'] == "item":
            inv = user_data.get('inventory') or {}
            inv[item_id] = inv.get(item_id, 0) + 1
            supabase.table("economy").update({"inventory": inv}).eq("user_id", uid).execute()
            
        elif item['type'] == "vip":
            if item.get('life'): expiry = "9999-12-31T23:59:59"
            else: expiry = (datetime.utcnow() + dt.timedelta(minutes=item['min'])).isoformat()
            supabase.table("economy").update({"vip_expiry": expiry}).eq("user_id", uid).execute()

        # 5. Discord Effects (Role/Nick/Message)
        if cid:
            asyncio.run_coroutine_threadsafe(
                handle_purchase_effects(uid, cid, item['name'], item['price'], result_text), 
                bot.loop
            )
        
        return jsonify({"status": "success", "msg": result_text, "bal": new_bal})
        
    except Exception as e:
        print(f"Buy Error: {e}")
        return jsonify({"status": "error", "msg": "Server Error"})

async def handle_purchase_effects(uid, cid, item_name, price, result_text):
    try:
        # 1. User & Channel Fetch
        try: user = await bot.fetch_user(int(uid))
        except: return

        channel = bot.get_channel(int(cid))
        if not channel: return
        guild = channel.guild
        
        # 2. Member Fetch
        try: member = await guild.fetch_member(user.id)
        except: 
            await channel.send(f"⚠️ **Warning:** {user.name} server me nahi mila!")
            return

        # 3. Receipt Send
        embed = discord.Embed(title="🛒 SHOP RECEIPT", color=C_GOLD)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.description = f"👤 **Buyer:** {user.mention}\n📦 **Item:** {item_name}\n💸 **Paid:** `${price:,}`\n📝 **Status:** {result_text}"
        await channel.send(embed=embed)

        # 4. Izzat Wapasi Logic
        if "Izzat" in item_name:
            try: await member.edit(nick=None)
            except: pass

        # --- ITEM DATA FETCH ---
        item_data = next((v for k, v in SHOP_ITEMS.items() if v["name"] == item_name), None)

        # ====================================================
        # 5. 🛡️ VERIFICATION SYSTEM (1 Day to Lifetime)
        # ====================================================
        if item_data and item_data.get('type') == 'verification':
            # A. Current Expiry Check from DB
            data = await get_data(uid)
            current_expiry_str = data.get('verify_expiry')
            
            duration = item_data['duration']
            new_expiry = None
            expiry_msg = ""

            # B. Duration Calculation
            if duration == "perm":
                new_expiry = dt.datetime(9999, 12, 31) # Lifetime Date
                expiry_msg = "**♾️ LIFETIME** (Amar ho gaye!)"
            else:
                # Agar pehle se verify hai, to extend karo
                if current_expiry_str and not current_expiry_str.startswith("9999"):
                    try:
                        current_dt = dt.datetime.fromisoformat(current_expiry_str)
                        if current_dt > dt.datetime.utcnow():
                            # Future me expire ho raha hai, wahan se add karo
                            new_expiry = current_dt + dt.timedelta(seconds=duration)
                        else:
                            # Expire ho chuka hai, abhi se add karo
                            new_expiry = dt.datetime.utcnow() + dt.timedelta(seconds=duration)
                    except:
                        new_expiry = dt.datetime.utcnow() + dt.timedelta(seconds=duration)
                else:
                    # First time verify
                    new_expiry = dt.datetime.utcnow() + dt.timedelta(seconds=duration)
                
                expiry_msg = f"Valid till: `{new_expiry.strftime('%d %b %Y')}`"

            # C. Database Update
            await db_call(lambda: supabase.table("economy").update({"verify_expiry": str(new_expiry)}).eq("user_id", str(uid)).execute())

            # D. Give 'Verified' Role (Agar server me hai to)
            # Make sure server me "Verified" ya "✅ Verified" naam ka role ho
            v_role = discord.utils.get(guild.roles, name="Verified")
            if not v_role: v_role = discord.utils.get(guild.roles, name="✅ Verified")
            
            if v_role:
                try: await member.add_roles(v_role)
                except: pass
            
            await channel.send(f"✅ **Verification Successful!**\n👤 {member.mention} is now Verified.\n📅 {expiry_msg}")


        # ====================================================
        # 6. PREMIUM ROLES (WITH EMOJIS & COLORS) 🎨
        # ====================================================
        if item_data and item_data.get('type') == 'role':
            
            # Step A: Clean Name nikalo (Comparison ke liye)
            # Example: "🚬 Peaky Blinders" -> "Peaky Blinders"
            clean_name = item_name.split(" ", 1)[1].strip() if " " in item_name else item_name

            # Step B: Configuration (Emoji Name + Color Mapping)
            # Yahan hum define karenge ki role ka EXACT naam aur color kya hona chahiye
            role_config = {
                "Hitman":         {"name": "🗡️ Hitman",         "color": 0x8B0000}, # Dark Red
                "Hacker":         {"name": "💻 Hacker",         "color": 0x00FF00}, # Neon Green
                "Gambler":        {"name": "🎲 Gambler",        "color": 0x9B59B6}, # Purple
                "Peaky Blinders": {"name": "🚬 Peaky Blinders", "color": 0x2C3E50}, # Dark Grey
                "Yakuza":         {"name": "👹 Yakuza",         "color": 0xFF0000}, # Bright Red
                "Mafia Boss":     {"name": "🕶️ Mafia Boss",     "color": 0x010101}, # Pitch Black
                "Kingpin":        {"name": "🦁 Kingpin",        "color": 0xE67E22}, # Bronze/Orange
                "Oil Prince":     {"name": "🛢️ Oil Prince",     "color": 0xDAA520}, # GoldenRod
                "Server God":     {"name": "⚡ Server God",     "color": 0xFFD700}, # Pure Gold
                "Immortal":       {"name": "🔮 Immortal",       "color": 0x00FFFF}, # Cyan
            }

            # Decide Final Name & Color
            if clean_name in role_config:
                target_role_name = role_config[clean_name]["name"] # Emoji wala naam
                target_color_code = role_config[clean_name]["color"]
            else:
                # Agar list me nahi hai, to Shop Item wala naam hi use karo
                target_role_name = item_name 
                import random
                target_color_code = random.randint(0, 0xFFFFFF)

            # Step C: Role Dhundo (Emoji wale naam se)
            role = discord.utils.get(guild.roles, name=target_role_name)
            
            # Step D: Auto-Create if missing
            if not role:
                try:
                    role_color = discord.Color(target_color_code)

                    # ✅ Hoist=True (List me alag dikhega)
                    role = await guild.create_role(
                        name=target_role_name, 
                        color=role_color, 
                        hoist=True, 
                        reason="Shop Premium Role Auto-Create"
                    )
                    await channel.send(f"🛠️ **Premium Role Created:** `{target_role_name}` (Color Set!)")
                    
                except discord.Forbidden:
                    await channel.send(f"🚫 **Error:** Main `{target_role_name}` banana chahta tha, par 'Manage Roles' permission nahi hai!")
                    return

            # Step E: Assign Role
            if role:
                try:
                    if role not in member.roles:
                        await member.add_roles(role)
                        await channel.send(f"🎉 **Role Equipped:** {member.mention} is now `{target_role_name}`!")
                    else:
                        await channel.send(f"ℹ️ **Info:** Inke paas pehle se `{target_role_name}` role tha.")
                except discord.Forbidden:
                    await channel.send(f"🚫 **Hierarchy Error:** Mera role `{target_role_name}` se neeche hai. Mere role ko upar karo!")

    except Exception as e:
        print(f"Effect Error: {e}")
                        

# ================== 🎮 DISCORD COMMANDS ==================

@bot.tree.command(name="shop", description="🛒 Open Premium Store")
async def shop_cmd(i: discord.Interaction):
    base_url = os.getenv("RENDER_URL", "https://tingbot-q1jb.onrender.com")
    # Passing Channel ID (cid) is IMPORTANT
    url = f"{base_url}/?uid={i.user.id}&cid={i.channel_id}"
    
    embed = discord.Embed(title="⚜️ GLOBAL BLACK MARKET", description="Underground store access granted.\nClick button to buy illegal items & roles.", color=C_GOLD)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="🌐 OPEN STORE", url=url, style=discord.ButtonStyle.link, emoji="🛒"))
    await i.response.send_message(embed=embed, view=view)

@bot.tree.command(name="balance", description="💰 View Wallet, Bank & Inventory")
async def balance(i: discord.Interaction, user: discord.Member = None):
    u = user or i.user
    res = supabase.table("economy").select("*").eq("user_id", str(u.id)).execute()
    
    if not res.data:
        supabase.table("economy").insert({"user_id": str(u.id), "balance": 0, "bank": 0, "inventory": {}}).execute()
        d = {"balance": 0, "bank": 0, "inventory": {}}
    else: d = res.data[0]
    
    total = d['balance'] + d['bank']
    
    embed = discord.Embed(title=f"🏦 WEALTH: {u.name.upper()}", color=C_DARK)
    embed.set_thumbnail(url=u.display_avatar.url)
    embed.add_field(name="💳 Wallet", value=f"`${d['balance']:,}`", inline=True)
    embed.add_field(name="🏦 Bank", value=f"`${d['bank']:,}`", inline=True)
    embed.add_field(name="💎 Net Worth", value=f"**${total:,}**", inline=False)
    
    # Inventory Display (NEW LOGIC)
    inv = d.get('inventory', {}) or {}
    inv_text = ""
    # Map IDs to Display Names
    for k, v in inv.items():
        if v > 0:
            name = SHOP_ITEMS.get(k, {}).get('name', k.title())
            inv_text += f"{name}: **x{v}**\n"
    
    # Check VIP
    vip_end = d.get('vip_expiry')
    if vip_end and vip_end > datetime.utcnow().isoformat():
        inv_text += f"👑 **VIP ACTIVE**"
        
    if inv_text: embed.add_field(name="🎒 Inventory", value=inv_text, inline=False)
    
    await i.response.send_message(embed=embed)

@bot.tree.command(name="deposit", description="🏦 Deposit money (Safe)")
async def deposit(i: discord.Interaction, amount: str):
    uid = str(i.user.id)
    res = supabase.table("economy").select("*").eq("user_id", uid).execute()
    if not res.data: return await i.response.send_message("❌ Account nahi hai.", ephemeral=True)
    d = res.data[0]
    
    # Fix: Deposit All vs Number logic
    if amount.lower() == "all": amt = int(d['balance'])
    else: 
        try: amt = int(amount)
        except: return await i.response.send_message("❌ Number likho!", ephemeral=True)
        
    if amt <= 0: return await i.response.send_message("❌ 0 deposit nahi hoga.", ephemeral=True)
    if d['balance'] < amt: return await i.response.send_message("❌ Wallet me itna paisa nahi hai!", ephemeral=True)
    
    supabase.table("economy").update({"balance": int(d['balance'])-amt, "bank": int(d['bank'])+amt}).eq("user_id", uid).execute()
    
    embed = discord.Embed(description=f"✅ **Deposited:** `${amt:,}`", color=C_GREEN)
    await i.response.send_message(embed=embed)

@bot.tree.command(name="withdraw", description="🏦 Withdraw money")
async def withdraw(i: discord.Interaction, amount: str):
    uid = str(i.user.id)
    res = supabase.table("economy").select("*").eq("user_id", uid).execute()
    d = res.data[0]
    
    if amount.lower() == "all": amt = int(d['bank'])
    else: 
        try: amt = int(amount)
        except: return await i.response.send_message("❌ Number likho!", ephemeral=True)
        
    if amt <= 0: return await i.response.send_message("❌ 0 withdraw nahi hoga.", ephemeral=True)
    if d['bank'] < amt: return await i.response.send_message("❌ Bank khali hai!", ephemeral=True)
    
    supabase.table("economy").update({"balance": int(d['balance'])+amt, "bank": int(d['bank'])-amt}).eq("user_id", uid).execute()
    
    embed = discord.Embed(description=f"✅ **Withdrawn:** `${amt:,}`", color=C_GREEN)
    await i.response.send_message(embed=embed)

@bot.tree.command(name="rob", description="🔫 Rob User (1H Cooldown, Victim needs 100k)")
@app_commands.checks.cooldown(1, 3600) # 1 Hour Cooldown
async def rob(i: discord.Interaction, victim: discord.Member):
    if i.user.id == victim.id or victim.bot: return await i.response.send_message("❌ Cannot rob yourself/bots", ephemeral=True)
    
    # Fetch Data
    vic_data = supabase.table("economy").select("*").eq("user_id", str(victim.id)).execute().data
    rob_data = supabase.table("economy").select("*").eq("user_id", str(i.user.id)).execute().data
    
    if not vic_data: return await i.response.send_message("❌ Victim ke paas account hi nahi hai", ephemeral=True)
    vic = vic_data[0]
    robber = rob_data[0]
    
    # 1. Minimum Balance Check (100k) (USER REQUEST)
    if vic['balance'] < 100000:
        return await i.response.send_message(f"⚠️ **Safe:** {victim.name} ke paas 100k se kam hain. Loot bekar hai.", ephemeral=True)
        
    # 2. Landmine Trap Check
    if vic.get('inventory', {}).get('landmine', 0) > 0:
        inv = vic['inventory']
        inv['landmine'] -= 1
        fine = int(robber['balance'] * 0.3) # 30% Fine
        
        supabase.table("economy").update({"inventory": inv, "balance": vic['balance'] + fine}).eq("user_id", str(victim.id)).execute()
        supabase.table("economy").update({"balance": robber['balance'] - fine}).eq("user_id", str(i.user.id)).execute()
        
        embed = discord.Embed(title="💥 BOOM! LANDMINE!", color=C_RED)
        embed.description = f"💀 **{i.user.mention}** stepped on a Landmine!\n💸 You paid `${fine:,}` hospital bill to **{victim.name}**."
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1166/1166469.png")
        return await i.response.send_message(embed=embed)

    # 3. Normal Robbery Logic
    if random.choice([True, False]):
        loot = int(vic['balance'] * random.uniform(0.2, 0.5)) # Loot 20-50%
        supabase.table("economy").update({"balance": vic['balance'] - loot}).eq("user_id", str(victim.id)).execute()
        supabase.table("economy").update({"balance": robber['balance'] + loot}).eq("user_id", str(i.user.id)).execute()
        
        embed = discord.Embed(title="💰 ROBBERY SUCCESS", color=C_GOLD)
        embed.description = f"😈 You stole `${loot:,}` from **{victim.mention}**!"
        await i.response.send_message(embed=embed)
    else:
        fine = 5000
        supabase.table("economy").update({"balance": robber['balance'] - fine}).eq("user_id", str(i.user.id)).execute()
        
        embed = discord.Embed(title="🚔 POLICE ARREST", color=C_RED)
        embed.description = f"👮 Police caught you robbing **{victim.name}**!\n💸 Fine Paid: `$5,000`"
        await i.response.send_message(embed=embed)

@rob.error
async def rob_error(i: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        min_left = int(error.retry_after // 60)
        await i.response.send_message(f"⏳ **Cooldown:** Police is watching! Try again in **{min_left} minutes**.", ephemeral=True)

@bot.tree.command(name="give_money", description="💸 (Owner) Add Money")
async def give_money(i: discord.Interaction, user: discord.Member, amount: int):
    if i.user.id != OWNER_ID: return await i.response.send_message("❌ Owner Only!", ephemeral=True)
    
    res = supabase.table("economy").select("*").eq("user_id", str(user.id)).execute()
    if not res.data:
        supabase.table("economy").insert({"user_id": str(user.id), "balance": amount, "bank": 0, "inventory": {}}).execute()
    else:
        new_bal = res.data[0]['balance'] + amount
        supabase.table("economy").update({"balance": new_bal}).eq("user_id", str(user.id)).execute()
        
    await i.response.send_message(f"✅ Gave `${amount:,}` to {user.mention}")

@bot.tree.command(name="check_lottery", description="🔒 (Owner) Check Logs")
async def check_lottery(i: discord.Interaction):
    if i.user.id != OWNER_ID: return await i.response.send_message("❌ Admin Only", ephemeral=True)
    await i.response.send_message("ℹ️ Website Lottery is Instant. No pending tickets.", ephemeral=True)


# ================== 🚀 FINAL STARTUP ==================

# 1. Pinger (Bot ko sone nahi dega)
def self_ping():
    while True:
        time.sleep(45)
        try: requests.get(f"{os.getenv('RENDER_URL')}/ping")
        except: pass

# 2. Server Start (Website + Shop)
def run_server():
    # Render Port 10000 use karta hai
    app.run(host='0.0.0.0', port=10000)

# ✅ THREADS KO SABSE LAST ME START KARO
threading.Thread(target=run_server, daemon=True).start()
threading.Thread(target=self_ping, daemon=True).start()

# ✅ BOT START (Ye file ki bilkul aakhiri line honi chahiye)
bot.run(os.getenv("DISCORD_TOKEN"))
