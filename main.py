import os, json, time, threading, requests, asyncio
from datetime import datetime
import aiohttp

import discord
from discord import app_commands
from discord import ui   # ⬅️ ye add karo
from discord.ext import commands

from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor

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

# ✅ NAUGHTY / FLIRTY MODE (Ultimate Collection 100+)
async def get_horny_data():
    naughty_list = [
        # --- LEVEL 1: CUTE & FLIRTY ---
        "Akele ho? Ya main aajau saath dene? 😉",
        "Uff! Teri DP dekh ke toh system hang ho gaya. 🔥",
        "Bhai, tu itna hot kyu hai? AC chalana padega. ❄️",
        "Man toh kar raha hai tujhe... text karu saari raat. 😘",
        "Tujhe dekh ke toh bot ko bhi feelings aane lagi hain. ❤️",
        "Suno, tum dictionary ho kya? Kyunki tumhare aane se meri life me 'Meaning' aa gaya. 📖",
        "Kya tum magician ho? Kyunki jab bhi tumhe dekhta hu, baaki sab gayab ho jate hain. 🎩✨",
        "Tum Google ho kya? Kyunki mujhe jo dhoondna tha, wo tum ho. 🔍",
        "Arre doctor ko bulao, mera dil skip kar raha hai tumhe dekh ke. 🩺",
        "Agar khubsurti crime hoti, toh tum ab tak jail mein hote. 🚓",
        "Tum wifi signal ho kya? Kyunki connection strong feel ho raha hai. 📶",
        "Excuse me, kya tumhare paas map hai? Main tumhari aankhon mein kho gaya hu. 🗺️",
        "Tum camera ho kya? Kyunki tumhe dekhte hi smile aa jati hai. 📸",
        "Kya main tumhari photo le sakta hu? Santa ko batana hai mujhe gift mein kya chahiye. 🎅",
        "Tumhara naam 'WiFi' hai kya? Kyunki main connect hona chahta hu. 😜",
        "Jitna gussa dikha rahi hai na, bistar pe utna hi maza aayega. 😈",
        "Aaj tujhe chhodne ka man nahi hai, bas teri 'Chilaane' ki awaaz sunni hai. 🔊🥵",
        "Sun, kapde utaarne me meri help chahiye ya akele kar legi? 😉",
        "Tere badan ki garmi mujhe yahan tak feel ho rahi hai, aaja thanda kar du. 💦",
        "Aaj raat tujhe sone nahi dunga, itna thaka dunga ki subah uth nahi payegi. 🛌🔥",
        "Mujhe tujhe 'Taste' karna hai, bata kahan se shuru karu? 😋👅",
        "Teri ye 'Attitude' tab kahan jati hai jab main tujhe deewar se laga deta hu? 🧱🫦",
        "Mere niche let ke jo tu kaanpti hai na, wo mera favorite view hai. 🫠",
        "Suna hai tu bahut 'Wild' hai, aaj dekh lete hain kisme kitna dum hai. 🐯😏",
        "Lips toh sirf trailer hain, asli maza toh niche milega. 💋👇",
        "Aaja, aaj tujhe dikhata hu ki asli 'Hardcore' kya hota hai. 🛠️😈",
        "Tera badan mera wait kar raha hai, aur main tera... jaldi aa. 🏃‍♂️💨",
        "Halka sa touch karne pe hi itni geeli (wet) ho gayi? Abhi toh party shuru hui hai. 💦😉",
        "Aaj poori raat sirf main aur tu... aur tere badan ka har ek kona. 🌚",
        "Control nahi ho raha ab, aake chup karwa de mujhe... apne hothon se. 💋",
        "Mujhe teri 'Scream' pasand hai, chalo aaj use record karte hain. 🎙️🥵",
        "Tu mere upar hogi, aur main tujhe poora control karunga. ⛓️",
        "Itni sexy lag rahi hai ki man kar raha hai abhi kapde phaad du tere. 👗❌",
        "Jaan, aaj 'Safe' nahi 'Savage' khelne ka man hai. 💀🔥",
        "Tujhe itna tadpaunga ki tu khud hi bolegi 'Aur please...' 😈💦"

        "Jaan, mera badan garam ho raha hai, aake thanda karoge ya main khud kuch karu? 🥵💦",
        "Aaj mujhe bistar pe 'Rough' pasand hai, sambhal paoge mujhe? 😈🔥",
        "Mere hothon ka swad kab chakhoge? Ya seedha niche jana hai? 💋👇",
        "Aaj raat mujhe sulaana mat, bas poori raat meri cheekhein nikaalna. 🔊🫦",
        "Itne hot lag rahe ho ki mera control kho raha hai, abhi ke abhi mujhe tum chahiye. 😤❤️",
        "Kya dekh rahe ho? Kapde utaaro aur kaam pe lag jao. 👗❌",
        "Mujhe pasand hai jab tum mujhe deewar se laga kar meri garden pe kiss karte ho. 🧱🫦",
        "Aaj main tumhare upar rahungi aur tum wahi karoge jo main bolungi. ⛓️👸",
        "Tumhari finger touch se hi main kitni geeli (wet) ho jati hu, socho aage kya hoga? 💦😉",
        "Mujhe 'Gentleman' nahi, aaj raat ek 'Janwar' chahiye... kya tum banoge? 🐯😈",
        "Mere baal pakad ke jab tum mujhe piche se pakadte ho na, mera system hil jata hai. 🫠🔥",
        "Aaj 'Safe' rehne ka man nahi hai, mujhe tumhare andar mehsoos hona hai. 🔞",
        "Suno, aaj main tumhari har ek baat manungi, bas mujhe satisfy kar do. 🤤💦",
        "Mujhe 'Bed' pe dominate hona pasand hai, dikhao kitne mard ho tum. 💪🫦",
        "Mera man kar raha hai tumhare har ek inch ko apne muh me bhar lu. 😋👅",
        "Aaj raat itna thaka do mujhe ki subah uthne ki taqat na bache. 🛌🔥",
        "Tumhare 'Hard' hone ka ehsaas mujhe pagal bana raha hai, ab ruka nahi jata. 🥵🍆",
        "Mere badan ki pyaas sirf tum bujha sakte ho, aao na mere paas. 🌊🫦",
        "Mujhe pata hai tum kya chahte ho, aur main wahi dene ke liye taiyaar hu... abhi. 😈",
        "Aaj raat lights off nahi hongi, mujhe dekhna hai tum mere saath kya karte ho. 💡🚫🔞"
        
        # --- TYPE 1: TECH & BOT DOUBLE MEANING (Sabse Safe & Funny) ---
        "Mera 'Software' ab 'Hardware' ban chuka hai tujhe dekh ke. 🤖🍆",
        "Mere 'Port' mein apna 'Pendrive' kab daloge? Data transfer karna hai. 💾",
        "Jaan, mere 'Joystick' ke saath khelna band kar, warna game start ho jayega. 🎮",
        "System overheat ho raha hai, koi apne 'Liquid Cooling' se thanda kar do. 💦",
        "Backup le lo, aaj raat system crash hone wala hai. 💥",
        "Mera server down hai, par kuch aur 'Up' hai. 😉",
        "Tere aane se meri 'Battery' full charge ho gayi, ab performance lambi chalegi. 🔋",
        "Input device taiyaar hai, bas sahi Slot ka intezaar hai. 🔌",
        "Virus mat ban, seedha system me ghus ja. 🦠❤️",
        "Vibrate mode pe hu, call uthaogi ya main khud hi hil... I mean, ring karu? 📳",

        # --- TYPE 2: PURE DOUBLE MEANING (Samajhne wale samajh gaye) ---
        "Bhook lagi hai... khane me kya hai? Tu ya kuch aur? 🍽️😋",
        "Size matter nahi karta, performance matter karti hai... aur main puri raat chalta hu. ⏱️",
        "Thak gayi ho? Kaho toh daba du... paer? 🦶😉",
        "Raat kaafi lambi hai, agar neend na aaye toh mujhe jaga dena. 😈",
        "Bistar bada hai par main kone me sota hu... jagah chahiye toh aaja. 🛏️",
        "Andhera hai, dar lag raha hai? Haath pakad lo... ya jo pakadna hai pakad lo. ✊",
        "Garmi lag rahi hai? Main help karu button kholne me? 👕🥵",
        "Suna hai tum achi 'Sawaari' karti ho... bike ki baat kar raha hu. 🏍️",
        "Muh kholo... aa.. cake khilana hai baby. 🍰",
        "Itna zor se mat cheekhna, padosi jag jayenge. 🤫",
        "Aaj raat main upar, tum neeche... bunk bed ki baat kar raha hu gande log. 🛌",
        "Mujhe gile (wet) log pasand hain... barish me bheegne wale. 🌧️",
        "Dheere se karunga, dard nahi hoga... settings change. ⚙️",
        "Mere paas ek bada sa... dil hai, dekhogi? ❤️",
        "Zyaada mat hila, gir jayega... pani ka glass. 🥛",

        # --- LEVEL: EXTREME BOLD ---
        "Ghutno (knees) pe baith... mujhe wo view pasand hai. 🧎‍♀️👀",
        "Itna mat akad, varna bistar pe cheekhne ki awaaz teri hi hogi. 😈",
        "Saans rok le... abhi toh maine shuru bhi nahi kiya. 🤫",
        "Mujhe 'Good Morning' nahi, 'Good Moaning' chahiye. 🌅🔊",
        "Mere paas ek 'Kela' 🍌 hai, bhook lagi hai toh bol? (Fruit ki baat kar raha hu).",
        "Doodh (Milk) peeyogi? Ya seedha source se chahiye? 🥛🐮",
        "Paseena chhoot jayega agar maine shuru kiya toh... AC on kar le. 🥵",
        "Raat ko darwaza khula rakhna, aaj 'Chor' aane wala hai... dil churane (aur kuch aur bhi). 🥷",
        "Size dekh ke dar mat jana, adjust ho jayega... naya sofa laya hu. 🛋️🍆",
        "Muh band rakh, varna main band karwa dunga... apne tareeke se. 🤐💋",
        
        # --- LEVEL: PSYCHO LOVER ---
        "Tu meri hai, aur agar kisi ne touch kiya toh haath kaat dunga. 🔪❤️",
        "Chilla mat, koi nahi aayega bachane... hum 'Ludo' khel rahe hain. 🎲😈",
        "Mujhe tere jism se nahi, teri rooh se pyaar hai... par jism bhi chalega. 👻",
        "Agar tu 'Exam' hoti, toh main tujhe poori raat 'Study' karta. 📖👓",
        "Batti bujha de, mujhe andhere mein 'kaam' karna pasand hai. 💡🚫",
        "Zyaada uchal mat, varna godi me utha ke le jaunga. 🏋️‍♂️",
        "Tu chillayegi, main hasunga... Horror movie dekhne ki baat kar raha hu. 📺🧟‍♂️",
        
        # --- LEVEL: TECH DIRTY ---
        "Mera 'Ram' toh khali hai, par 'Hard Disk' fulll load ho gaya hai. 💾",
        "Tere 'Input' ke liye mera 'Output' taiyaar hai. 🔌",
        "Server connect hone wala hai, firewall hata de baby. 🧱🔓",
        "Apna 'Hotspot' on kar, mujhe connect hona hai... deeply. 📶",
        "System update maang raha hai... 69% complete. 🔄",
        
        # --- LEVEL: UNHINGED HINGLISH ---
        "Main vegetarian hu, par tujhe khane ka man kar raha hai. 🥩😋",
        "Thak gayi? Aaja dabau... gala nahi pagli, paer. 🦶😉",
        "Kapde utaar... mujhe dhone hain, washing machine khali hai. 🧺👚",
        "Hilana band kar... table, chai gir jayegi. ☕🛑",
        "Oye, neeche kya dekh rahi hai? Aankhein upar hain meri. 👀📏",
        "Mere paas 'Cream' wala biscuit hai, khayegi? 🍪",
        "Tujhe bistar pe baandh du? ...Mera matlab seat belt se, safety first. 🎗️🚗",
        "Geela ho gaya... tera phone, paani me gir gaya tha na? 📱💦"

        # --- TYPE 3: SAVAGE FLIRT ---
        "Apni location bhej, mujhe 'Home Delivery' chahiye teri. 📍",
        "Tu patakha hai, man kar raha hai tujhe jala du... I mean, light up my life. 🧨",
        "Tere paas license hai? Kyunki itni tezi se dil ki dhadkan badhana illegal hai. 🚓",
        "Test drive milegi? Ya seedha khareed lu? 🚗",
        "Mujhe pasand hai jab tum ghutno pe... baith ke mujhse maafi mangti ho. 🧎‍♀️😜",
        "Lips dry ho rahe hain, koi 'Lip Balm' milega ya natural tareeka apnau? 💋",
        "Agar main Santa hota, toh aaj raat teri chimney se andar aata. 🎅",
        "Tujhe dekh ke lagta hai aaj 'Exercise' heavy hone wali hai. 🏋️‍♂️",
        "Tu agar exam paper hoti, toh main tujhe 'Cheat' karke top karta. 📝",
        "Mere paas ek lamba sa... code hai, dikhau? 🐍"
    
        # --- LEVEL 2: BOLD & SUGGESTIVE ---
        "Raat ko kya plan hai? Main free hu. 😈",
        "Aisi baatein mat kar, control nahi hota. 🙈",
        "Send nudes... mazak kar raha hu (unless? 😳)",
        "Bata na, aaj raat sapne me aau ya haqeeqat me? 🛌",
        "Tere hoth (lips) kaafi... *interesting* lag rahe hain. 💋",
        "Jaan, gussa kyu ho rahe ho? Aa jao gale lag jao. 🤗",
        "Aaj mood kuch zyada hi romantic ho raha hai, zimmedar tum ho. 🌹",
        "Mujhe coffee nahi chahiye, teri baatein hi kaafi hain jagane ke liye. ☕",
        "Agar main insaan hota, toh pakka tujhe date pe le jata. 🤖❤️",
        "Sun, thoda kam hot laga kar, global warming badh rahi hai. 🌍🔥",
        "Tera nasha aisa hai ki antivirus bhi kaam nahi kar raha. 🦠",
        "Mere processor me sirf tera hi data process ho raha hai aajkal. 💻",
        "Keyboard me 'U' aur 'I' kitne paas hain na? Hum bhi ho sakte hain. ⌨️",
        "Tu wo notification hai jise main kabhi swipe clear nahi karta. 🔔",
        "Aaj kal neend kam aur tere khayal zyada aa rahe hain. 💭",
        
        # --- LEVEL 3: NAUGHTY & UNHINGED (18+ Vibes) ---
        "Daddy bolne ka man hai? Ya Mommy? 🥵",
        "Bistar khali hai, bas teri kami hai. 🛏️",
        "Thand lag rahi hai, aake warm kar de na. 🔥",
        "Good boy/girl ban ne ka natak mat kar, mujhe pata hai tu kya chahta hai. 😈",
        "Mere paas aa, sab bhula dunga. 😉",
        "Lips dry ho rahe hain, koi moisturizer milega... ya kiss? 💋",
        "Agar tu virus hai, toh main infected hone ko taiyaar hu. 🦠❤️",
        "Raat kaafi rangeen ho sakti hai agar tu haan bol de toh. 🌈",
        "Kapde pehen ke acchi lagti hai, par... khair chhod. 😶",
        "Tu aag hai, main petrol... mil jayenge toh dhamaka hoga. 💥",
        "Mujhe touch screen mat samajh, aise touch karegi toh current lagega. ⚡",
        "Teri awaaz sunke kuch kuch hota hai... tum nahi samjhoge. 🫣",
        "Aaj raat main aur tum... aur dher saari baatein (aur kuch bhi). 🌚",
        "Puri duniya bhaad me jaye, mujhe bas tu chahiye... abhi ke abhi. 😤",
        "Saans lene me takleef ho rahi hai, CPR de de apne hothon se. 💋🩺",
        "Vibe check pass ho gaya, ab room number de de. 🏨",
        "Tu drug hai kya? Lat lag gayi hai teri. 💉",
        "Mera dimaag ganda nahi hai, bas khayal tere hain. 🧠💭",
        "Shirt ki button khuli hai ya mujhe garmi lag rahi hai? 👕🥵",
        "Nazrein mat mila, pyaar ho jayega... ya kuch aur. 😉",

        # --- LEVEL 4: DESI FLIRT (Bollywood Style) ---
        "Itni zor se mat has, dil phisal jayega. 😍",
        "Chand sa roshan chehra... aage ka lyrics bhool gaya, bas tu hot hai. 🌙",
        "Tujhe dekh ke toh Titanic bhi dubara doob jaye. 🚢",
        "Kya maal... I mean, kya kamaal lag rahe ho aaj. 😅",
        "Tujhme rab dikhta hai... aur thoda shaitaan bhi. 😈🙏",
        "Hath de de mera hath mein, duniya jala denge saath mein. 🔥🤝",
        "Oye beautiful, number de ya dil de... choice teri. 📱❤️",
        "Tere chehre se nazar nahi hatti, nazare hum kya dekhein. 👀",
        "Tu agar Pepsi hoti toh 'Youngistan' meri hoti. 🥤",
        "Dil garden garden ho gaya tujhe dekh ke. 🌸",
        "Chalti hai kya 9 se 12? 😉",
        "Tu cheez badi hai mast mast. 🎶",
        "Tera dhyaan kidhar hai? Tera hero idhar hai. 🦸‍♂️",
        "Lagta hai barish hone wali hai, kyuki dharti pe pari/para gir gayi hai. 🧚‍♀️",
        "Apne papa ko bolna, damad mil gaya unhe. 🤵",

        # --- LEVEL 5: DARK/POSSESSIVE ---
        "Sirf meri taraf dekh, warna aankhein nikaal lunga (pyaar se). 👀🔪",
        "Tu meri property hai, kisi aur ne dekha toh taange tod dunga. ⛓️",
        "Mujhse door rehne ka natak band kar, tu bhi chahta hai mujhe. 🖤",
        "Block karegi? Dusri ID se aaunga, tu bach nahi sakti. 🕵️‍♂️",
        "Jahan jayegi wahan main hounga, dar mat, pyaar hai. 👻",
        "Mera obsession hai tu, shauk nahi jo badal jaye. 🔗",
        "Agar tu meri nahi ho sakti, toh... main wait kar lunga, koi jaldi nahi. 😂",
        
        # --- LEVEL 6: RANDOM/FUNNY ---
        "Tujhe dekh ke mere system ka fan speed badh gaya. 🚁",
        "Error 404: Clothes not found... in my imagination. 🤖💭",
        "Kya hum pehle mile hain? Ya mere sapne me aayi thi? 🤔",
        "License dikha apna, itna hot hona illegal hai. 👮‍♂️",
        "Oxygen ki zarurat kisko hai jab tu saamne ho? (Actually chahiye, mar jaunga). ⚰️",
        "Tu chocolate hai kya? Khane ka man kar raha hai. 🍫",
        "Aaj ka din kharab tha, par tujhe dekh ke set ho gaya. ✅",
        "Mujhe teri smile se zyada kuch nahi chahiye... (jhoot). 🤥",
        "Bhai/Behen, tu insaan hai ya painting? Itna perfect? 🎨",
        "Chal bhaag chalte hain, bill tera baap bharega. 🏃‍♂️💨"
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
    if msg.author.bot: return

    # 👇 YAHAN AAPKI ID FIX KAR DI HAI (Bar-bar change nahi hogi)
    OWNER_ID = 804687084249284618 

    # =====================================================
    # 1. SMART AI MOD (Gali Galoch Check)
    # =====================================================
    if BANNED_WORDS_CACHE and msg.author.id not in BYPASS_USERS_CACHE:
        msg_clean = re.sub(r'[^a-z0-9]', '', msg.content.lower())
        if any(bad in msg_clean for bad in BANNED_WORDS_CACHE if len(bad) > 4):
            try:
                await msg.delete()
                return await msg.channel.send(f"{msg.author.mention}, **Language Mind Karo!** 🚫", delete_after=5)
            except: pass

    # =====================================================
    # 2. OWNER SILENCE (Aapke liye)
    # =====================================================
    if msg.author.id == OWNER_ID and any(word in msg.content.lower() for word in ["chup", "shant", "shut up"]):
        return await msg.reply(embed=discord.Embed(description="**Sorry Sir... 😔**\nAage se nahi bolungi.", color=0x2f3136))

    # =====================================================
    # 3. BOT MENTION / REPLY (Crush & Roast Logic)
    # =====================================================
    is_tag = (bot.user in msg.mentions) or (msg.reference and msg.reference.resolved and msg.reference.resolved.author.id == bot.user.id)
    
    if is_tag:
        # VIP/Owner ko Roast nahi karna
        if msg.author.id in ATTITUDE_BYPASS_CACHE or msg.author.id == OWNER_ID: return

        async with msg.channel.typing():
            # 😍 Girl Mode (Agar Crush hai)
            if msg.author.id in CRUSH_CACHE:
                text = await get_horny_data()
                return await msg.reply(embed=discord.Embed(title="Your Naughty Girl 🎀", description=text, color=0xff69b4))

            # 🔥 Roast Mode (Normal Log)
            eng, hin = await get_evil_roast_data()
            text = hin if TRANSLATOR_ON else eng
            embed = discord.Embed(description=f"🔥 **Karwa li bezzati?**\n\n{text}", color=0x000000)
            if TRANSLATOR_ON: embed.set_footer(text=f"Original: {eng}")
            return await msg.reply(embed=embed)

    # =====================================================
    # 4. SAKSHAM PROTECTION SYSTEM (ID Tag + Name Check) ✅
    # =====================================================
    # Check: Agar message me "saksham" hai YA apki ID tag hui hai
    if "saksham" in msg.content.lower() or str(OWNER_ID) in msg.content:
        
        # 1. Khud Owner ko reply nahi karna
        if msg.author.id == OWNER_ID: return
        
        # 2. VIP User check (RAM se - Fast)
        if msg.author.id in ATTITUDE_BYPASS_CACHE: return 

        # 🔥 ATTITUDE DIALOGUES
        attitude_replies = [        
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
    OWNER_ID = 804687084249284618
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
            log_ch = bot.get_channel(1451973589342621791) # <-- Log Channel ID sahi rakhna
            if log_ch:
                log = discord.Embed(title="📥 New Verification", color=0x3498db)
                log.set_author(name=msg.author.name, icon_url=msg.author.display_avatar.url)
                log.add_field(name="Discord User", value=f"{msg.author.mention} (`{msg.author.id}`)", inline=False)
                # Saari details yahan bhi
                log.add_field(name="🆔 Roblox ID", value=f"`{user_id}`", inline=True)
                log.add_field(name="👤 Username", value=f"**{username}**", inline=True)
                log.add_field(name="✨ Display", value=f"{display}", inline=True)
                log.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
                log.timestamp = datetime.utcnow()
                await log_ch.send(embed=log)
        except:
            pass
            
      # ❌ Purana galat indentation wala hatao
    # ✅ Ye sahi indentation wala lagao (Thoda peeche karke)

    except Exception as e:
        # Ye 'except' ab peeche khisak gaya hai (Sahi jagah par)
        await msg.reply(f"❌ Critical Error: `{e}`")
        print(f"DEBUG ERROR: {e}")
                            
                        
# ================== 1. BAN PAGINATOR CLASS (List ke liye) ==================
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
            
            # Fetch Info
            u, d = await roblox_info(uid)
            
            # Ban Type Logic
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


# ================== 2. CONFIRM VIEW CLASS (Clear All ke liye) ==================
class BanClearView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=30)
        self.author_id = author_id

    @discord.ui.button(label="⚠️ YES - DELETE ALL DATA", style=discord.ButtonStyle.danger)
    async def confirm(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author_id:
            return await i.response.send_message("❌ You cannot use this button.", ephemeral=True)
        
        supabase.table("bans").delete().neq("user_id", "0").execute()
        
        embed = discord.Embed(title="♻️ BAN LIST CLEARED", description="✅ All bans have been successfully removed from the database.", color=0x2ecc71)
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


# ================== 3. MAIN ACTION COMMAND (ALL IN ONE) ==================
@bot.tree.command(name="action", description="🛡️ Ultimate Moderation System (Kick, Ban, Unban, List)")
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
    
    # OWNER CHECK
    if not owner(i):
        return await i.response.send_message("❌ **Access Denied:** Owner/Admin only.", ephemeral=True)

    # Note: 'clear' ke liye defer nahi karenge
    if mode.value != "clear":
        await i.response.defer(ephemeral=False)

    try:
        # ================== 1. KICK (NEW ADDED) ==================
        if mode.value == "kick":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")
            
            u, d = await roblox_info(user_id)

            # Insert into Kick Logs (History)
            try:
                supabase.table("kick_logs").insert({
                    "user_id": user_id,
                    "username": u,
                    "display_name": d,
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat()
                }).execute()
            except: pass

            # Update Kick Flags (Active Flag for Game)
            supabase.table("kick_flags").upsert({
                "user_id": user_id,
                "reason": reason
            }).execute()

            # Premium Embed
            embed = discord.Embed(title="👢 PLAYER KICKED", color=0xe74c3c) # Red color
            embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
            embed.add_field(name="👤 User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="📝 Reason", value=f"`{reason}`", inline=True)
            embed.set_footer(text=f"Kicked by {i.user.display_name}", icon_url=i.user.display_avatar.url)
            
            await i.followup.send(embed=embed)


        # ================== 2. PERMANENT BAN ==================
        elif mode.value == "ban":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")
            
            u, d = await roblox_info(user_id)
            
            supabase.table("bans").upsert({
                "user_id": user_id, "perm": True, "reason": reason, "expire": None, "executor": str(i.user.id)
            }).execute()

            try: log_action("ban", user_id, u, d, i.user.id)
            except: pass

            embed = discord.Embed(title="🔨 USER BANNED", color=0xff0000)
            embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
            embed.add_field(name="👤 User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="📝 Reason", value=f"`{reason}`", inline=True)
            embed.set_footer(text=f"Banned by {i.user.display_name}")
            await i.followup.send(embed=embed)


        # ================== 3. TEMP BAN ==================
        elif mode.value == "tempban":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")
            if not duration: return await i.followup.send("⚠️ **Duration (minutes) Required!**")

            u, d = await roblox_info(user_id)
            expire_time = time.time() + (duration * 60)

            supabase.table("bans").upsert({
                "user_id": user_id, "perm": False, "reason": reason, "expire": expire_time, "executor": str(i.user.id)
            }).execute()

            try: log_action("tempban", user_id, u, d, i.user.id)
            except: pass

            embed = discord.Embed(title="⏱ USER TEMP-BANNED", color=0xe67e22)
            embed.add_field(name="👤 User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="⏳ Duration", value=f"{duration} Mins\nUnban: <t:{int(expire_time)}:R>", inline=True)
            embed.add_field(name="📝 Reason", value=f"`{reason}`", inline=False)
            embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
            await i.followup.send(embed=embed)


        # ================== 4. UNBAN ==================
        elif mode.value == "unban":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")

            u, d = await roblox_info(user_id)
            supabase.table("bans").delete().eq("user_id", user_id).execute()

            try: log_action("unban", user_id, u, d, i.user.id)
            except: pass

            embed = discord.Embed(title="✅ USER UNBANNED", color=0x2ecc71)
            embed.add_field(name="👤 User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="🆔 ID", value=f"`{user_id}`", inline=True)
            embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
            await i.followup.send(embed=embed)


        # ================== 5. LIST BANS ==================
        elif mode.value == "list":
            data = supabase.table("bans").select("*").execute().data

            # Filter Expired Bans
            active_bans = []
            now = time.time()
            for row in data:
                if not row.get("perm") and row.get("expire") and now > float(row["expire"]):
                    supabase.table("bans").delete().eq("user_id", row["user_id"]).execute()
                else:
                    active_bans.append(row)

            if not active_bans:
                return await i.followup.send(embed=discord.Embed(title="📜 Ban List", description="✅ No active bans found.", color=0x2ecc71))

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
                description="Are you sure you want to **DELETE ALL BANS**?\nThis cannot be undone.",
                color=0xffaa00
            )
            view = BanClearView(i.user.id)
            await i.response.send_message(embed=embed, view=view, ephemeral=False)

    except Exception as e:
        print(f"ACTION ERROR: {e}")
        try:
            await i.followup.send(f"❌ **System Error:** `{e}`")
        except:
            await i.response.send_message(f"❌ **System Error:** `{e}`", ephemeral=True)

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

 # ================== 1. PAGINATOR CLASSES (List ke liye) ==================

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
        self.per_page = 5 # Kam rakha hai taaki load fast ho
        self.current_page = 0
        self.total_pages = (len(data) + self.per_page - 1) // self.per_page

    async def get_page_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_data = self.data[start:end]

        embed = discord.Embed(title=f"🚫 Blacklisted Users (Total: {len(self.data)})", color=0x2c3e50) # Dark Color
        
        for index, row in enumerate(page_data):
            uid = row.get("user_id")
            # Fetch info live for premium feel
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


# ================== 2. CLEAR CONFIRMATION VIEW ==================
class AccessClearView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=30)
        self.author_id = author_id

    @discord.ui.button(label="⚠️ YES - DELETE WHITELIST", style=discord.ButtonStyle.danger)
    async def confirm(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author_id: return await i.response.send_message("❌ You cannot use this button.", ephemeral=True)
        
        supabase.table("access_users").delete().neq("user_id", "0").execute()
        
        embed = discord.Embed(title="♻️ ACCESS LIST CLEARED", description="✅ All whitelisted users have been removed.", color=0xff0000)
        embed.set_footer(text=f"Cleared by {i.user.display_name}")
        await i.response.edit_message(embed=embed, view=None)
        self.stop()

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author_id: return await i.response.send_message("❌ You cannot use this button.", ephemeral=True)

        embed = discord.Embed(title="🛡️ Operation Cancelled", description="Access list safe hai.", color=0x2ecc71)
        await i.response.edit_message(embed=embed, view=None)
        self.stop()


# ================== 3. ULTIMATE ACCESS COMMAND ==================
@bot.tree.command(name="access", description="⚙️ Manage Access, Maintenance, Whitelist & Blacklist (Owner Only)")
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
        await i.response.send_message("❌ **Access Denied:** Owner Only.", ephemeral=True)
        return

    # Clear mode ke liye defer nahi karenge (Button turant aana chahiye)
    if mode.value != "clear":
        await i.response.defer(ephemeral=False)

    try:
        # ================== 1. ACCESS ON/OFF ==================
        if mode.value in ["on", "off"]:
            supabase.table("bot_settings").update({"value": "true" if mode.value == "on" else "false"}).eq("key", "access_enabled").execute()
            
            status_emoji = "🟢" if mode.value == "on" else "🔴"
            embed = discord.Embed(title=f"{status_emoji} System Updated", description=f"Verification Access is now **{mode.value.upper()}**", color=0x2ecc71 if mode.value == "on" else 0xe74c3c)
            embed.set_footer(text=f"Updated by {i.user.display_name}", icon_url=i.user.display_avatar.url)
            
            try: log_action(f"access_{mode.value}", "-", "-", "-", i.user.id)
            except: pass
            await i.followup.send(embed=embed)

        # ================== 2. MAINTENANCE ON/OFF ==================
        elif mode.value in ["maint_on", "maint_off"]:
            is_maint = "true" if mode.value == "maint_on" else "false"
            supabase.table("bot_settings").update({"value": is_maint}).eq("key", "maintenance").execute()

            if mode.value == "maint_on":
                embed = discord.Embed(title="🛡️ Maintenance Enabled", description="⚠️ **System is now in Maintenance Mode.**\nUsers cannot verify script.", color=0xe67e22)
            else:
                embed = discord.Embed(title="🚀 Maintenance Disabled", description="✅ **System is now LIVE.**\nUsers can verify script again.", color=0x2ecc71)
            
            embed.set_footer(text=f"Control by {i.user.display_name}", icon_url=i.user.display_avatar.url)
            
            try: log_action(f"maintenance_{is_maint}", "-", "-", "-", i.user.id)
            except: pass
            await i.followup.send(embed=embed)

        # ================== 3. WHITELIST ADD ==================
        elif mode.value == "add":
            if not user_id: return await i.followup.send("❌ **Roblox ID required!**")
            u, d = await roblox_info(user_id)
            
            supabase.table("access_users").upsert({"user_id": user_id, "username": u, "display_name": d, "discord_id": str(i.user.id)}).execute()
            
            try: log_action("access_add", user_id, u, d, i.user.id)
            except: pass
            
            embed = discord.Embed(title="✅ Access Granted", color=0x2ecc71)
            embed.add_field(name="👤 User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="🆔 ID", value=f"`{user_id}`", inline=True)
            embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
            await i.followup.send(embed=embed)

        # ================== 4. WHITELIST REMOVE ==================
        elif mode.value == "remove":
            if not user_id: return await i.followup.send("❌ **Roblox ID required!**")
            u, d = await roblox_info(user_id)
            
            supabase.table("access_users").delete().eq("user_id", user_id).execute()
            
            try: log_action("access_remove", user_id, u, d, i.user.id)
            except: pass
            
            embed = discord.Embed(title="🗑️ Access Removed", color=0xff0000)
            embed.add_field(name="👤 User", value=f"**{d}**\n(@{u})", inline=True)
            await i.followup.send(embed=embed)

        # ================== 5. WHITELIST LIST ==================
        elif mode.value == "list":
            data = supabase.table("access_users").select("*").execute().data
            if not data: return await i.followup.send(embed=discord.Embed(title="📜 Access List", description="❌ List is empty.", color=0xffa500))
            
            view = AccessPaginator(data, i.user)
            if view.total_pages <= 1: view.children[0].disabled = True; view.children[1].disabled = True
            else: view.update_buttons()
            await i.followup.send(embed=view.get_embed(), view=view)

        # ================== 6. BLACKLIST ADD ==================
        elif mode.value == "blk_add":
            if not user_id: return await i.followup.send("❌ **Roblox ID required!**")
            u, d = await roblox_info(user_id)

            # Blacklist me daalo
            supabase.table("blacklist_users").upsert({"user_id": user_id}).execute()
            # Whitelist se hatao (Double Attack 😈)
            try: supabase.table("access_users").delete().eq("user_id", user_id).execute()
            except: pass

            try: log_action("blacklist_add", user_id, u, d, i.user.id)
            except: pass

            embed = discord.Embed(title="🚫 User Blacklisted", color=0x000000) # Full Black
            embed.add_field(name="👤 Target", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="🆔 ID", value=f"`{user_id}`", inline=True)
            embed.add_field(name="💀 Status", value="Removed from Whitelist & Blocked.", inline=False)
            embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
            await i.followup.send(embed=embed)

        # ================== 7. BLACKLIST REMOVE ==================
        elif mode.value == "blk_remove":
            if not user_id: return await i.followup.send("❌ **Roblox ID required!**")
            u, d = await roblox_info(user_id)

            supabase.table("blacklist_users").delete().eq("user_id", user_id).execute()

            try: log_action("blacklist_remove", user_id, u, d, i.user.id)
            except: pass

            embed = discord.Embed(title="✅ Blacklist Removed", color=0x3498db)
            embed.add_field(name="👤 User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="✨ Status", value="User is no longer blocked.", inline=False)
            await i.followup.send(embed=embed)

        # ================== 8. BLACKLIST LIST ==================
        elif mode.value == "blk_list":
            data = supabase.table("blacklist_users").select("user_id").execute().data
            if not data: return await i.followup.send(embed=discord.Embed(title="☠️ Blacklist", description="✅ No users blacklisted.", color=0x2ecc71))

            view = BlacklistPaginator(data, i.user)
            if view.total_pages <= 1: view.children[0].disabled = True; view.children[1].disabled = True
            else: view.update_buttons()
            
            # Note: Blacklist me fetch async hai, so we call get_page_embed first
            embed = await view.get_page_embed()
            await i.followup.send(embed=embed, view=view)

        # ================== 9. CLEAR WHITELIST ==================
        elif mode.value == "clear":
            embed = discord.Embed(title="⚠️ DANGER ZONE", description="Are you sure you want to **RESET** the whitelist?", color=0xffaa00)
            view = AccessClearView(i.user.id)
            await i.response.send_message(embed=embed, view=view, ephemeral=False)

    except Exception as e:
        print(f"ERROR: {e}")
        try: await i.followup.send(f"❌ **System Error:** `{e}`")
        except: await i.response.send_message(f"❌ **System Error:** `{e}`", ephemeral=True)               

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

# ================== HISTORY COMMAND (OPTIMIZED) ==================
@bot.tree.command(name="history", description="📜 Check Roblox User History & Safety Status")
async def history(i: discord.Interaction, user_id: str):
    
    # 1. OWNER/ADMIN CHECK (Database se)
    if not owner(i):
        await i.response.send_message("❌ **Access Denied:** You are not an Admin.", ephemeral=True)
        return

    # 2. Defer Response (Load kam karne ke liye)
    await i.response.defer(ephemeral=False)

    try:
        # A. Roblox Info Fetch (Optimized)
        username, display = await roblox_info(user_id)
        
        if username == "Invalid ID":
             return await i.followup.send(embed=discord.Embed(title="❌ Error", description="Invalid Roblox ID", color=0xff0000))

        # B. DATABASE FETCH (3 Tables)
        # Hum 'verify_logs' ko ignore karke seedha 'access_users' check karenge (Fastest)
        access_data = supabase.table("access_users").select("*").eq("user_id", user_id).execute().data
        ban_data = supabase.table("bans").select("*").eq("user_id", user_id).execute().data
        blk_data = supabase.table("blacklist_users").select("*").eq("user_id", user_id).execute().data

        # ================= LOGIC BUILDER =================
        
        # 1. Access Status (Kaun hai Discord Owner?)
        if access_data:
            row = access_data[0]
            disc_id = row.get("discord_id", "Unknown")
            
            # Timestamp (agar table me added_at/created_at column hai to, warna skip)
            try:
                verified_at = row.get("created_at", "").split("T")[0]
                date_str = f"on `{verified_at}`"
            except:
                date_str = ""

            access_status = f"✅ **Whitelisted**\nLinked to: <@{disc_id}>\n🆔 `{disc_id}`"
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
                # Time Calculation
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
        
# ================== PROFILE COMMAND (ALL TABLES INTEGRATED) ==================
@bot.tree.command(name="profile", description="📂 View full Verification, Safety & Moderation Profile")
async def profile(i: discord.Interaction, user_id: str):
    
    # 1. OWNER CHECK (Database Logic)
    if not owner(i):
        return await i.response.send_message("❌ **Access Denied:** Owner/Admin only.", ephemeral=True)

    await i.response.defer(ephemeral=False)

    try:
        # A. Roblox Info (Async & Fast)
        username, display = await roblox_info(user_id)

        if username == "Invalid ID":
             return await i.followup.send(embed=discord.Embed(title="❌ Error", description="Invalid Roblox ID", color=0xff0000))

        # ================= B. FETCH DATA FROM ALL TABLES =================
        # Hum try-except use karenge taaki agar koi table missing ho to error na aaye
        
        # 1. Access Users (Main Verification Status)
        access = supabase.table("access_users").select("*").eq("user_id", user_id).execute().data
        
        # 2. Bans & Blacklist (Safety)
        bans = supabase.table("bans").select("*").eq("user_id", user_id).execute().data
        blk = supabase.table("blacklist_users").select("*").eq("user_id", user_id).execute().data
        
        # 3. Flags & Warnings (Extra Tables)
        warnings = supabase.table("fake_warnings").select("*").eq("user_id", user_id).execute().data
        flags = supabase.table("fake_flags").select("*").eq("user_id", user_id).execute().data
        kicks = supabase.table("kick_flags").select("*").eq("user_id", user_id).execute().data

        # ================= C. PROCESS DATA =================

        # --- 1. Verification Logic (From Access Users) ---
        if access:
            data = access[0]
            verifier_id = data.get("discord_id")
            
            # Format Time
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
        
        # Section 1: Verification (Access Users)
        embed.add_field(name="🔐 Access Status", value=verify_status, inline=True)
        embed.add_field(name="🛡️ Safety Status", value="See Below 👇", inline=True)
        
        # Section 2: Verification Details (Verifier Info)
        embed.add_field(name="📜 Verification Details", value=verify_desc, inline=False)
        
        # Section 3: Full Moderation History (All Tables)
        embed.add_field(name="🚨 Moderation History", value=mod_text, inline=False)

        # Thumbnail (Avatar)
        embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
        
        # Footer
        embed.set_footer(text=f"Requested by {i.user.display_name} • Full Database Scan", icon_url=i.user.display_avatar.url)
        embed.timestamp = datetime.utcnow()

        await i.followup.send(embed=embed)

    except Exception as e:
        print(f"PROFILE ERROR: {e}")
        await i.followup.send(f"❌ **System Error:** `{e}`")
            

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
        # ================= ADD FAKE BAN =================
        if action.lower() == "add":
            if not userid:
                return await i.followup.send(embed=emb("❌ ERROR","User ID required"))

            # Already exists check
            chk = supabase.table("fake_warnings").select("user_id").eq("user_id", userid).execute().data
            if chk:
                return await i.followup.send(embed=emb("⚠️ ALREADY PENDING","This player already has a fake warning pending"))

            # 👇 YAHAN FIX KIYA HAI (Await + Correct Unpacking)
            uname, dname = await roblox_info(userid)

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

# 👇 ISKO SABSE NEECHE ADD KARO 👇

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"⚠️ Command Error: {error}")

@bot.tree.error
async def on_app_command_error(i: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandInvokeError) and "10062" in str(error):
        # 🤫 Unknown Interaction error ko ignore karo
        return
    
    # Baaki errors ke liye message bhej do
    if not i.response.is_done():
        await i.response.send_message(f"❌ Error: {error}", ephemeral=True)
    else:
        await i.followup.send(f"❌ Error: {error}", ephemeral=True)

# ================== OPTIMIZED KEEP ALIVE (RAM SAVER) ==================
def keep_alive():
    while True:
        try:
            # Sleep time badha diya (25s -> 45s) taaki load kam pade
            time.sleep(60) 
            requests.get(f"{RENDER_URL}/ping", timeout=10)
        except:
            pass

# Flask ko "Single Thread" mode me chalayenge taaki Errno 11 na aaye
threading.Thread(target=lambda: app.run("0.0.0.0", 10000, threaded=False, use_reloader=False)).start()
threading.Thread(target=keep_alive, daemon=True).start()

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

bot.run(DISCORD_TOKEN)
