import os, json, time, threading, requests, asyncio
from datetime import datetime
import aiohttp
from discord.ext import commands
from gtts import gTTS
import edge_tts

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


# ================== 3. MAIN ACTION COMMAND (FIXED: ALL MODES) ==================
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
    
    if not owner(i):
        return await i.response.send_message("❌ **Access Denied:** Owner/Admin only.", ephemeral=True)

    # Note: 'clear' ke liye defer nahi karenge (Button turant aana chahiye)
    if mode.value != "clear":
        await i.response.defer(ephemeral=False)

    try:
        # ================== 1. KICK ==================
        if mode.value == "kick":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")
            u, d = await roblox_info(user_id)

            # ✅ FIX: Async DB Call
            await db_call(lambda: supabase.table("kick_logs").insert({
                "user_id": user_id, "username": u, "display_name": d, "reason": reason, "timestamp": datetime.utcnow().isoformat()
            }).execute())

            # ✅ FIX: Async DB Call
            await db_call(lambda: supabase.table("kick_flags").upsert({
                "user_id": user_id, "reason": reason
            }).execute())

            embed = discord.Embed(title="👢 PLAYER KICKED", color=0xe74c3c)
            embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
            embed.add_field(name="👤 User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="📝 Reason", value=f"`{reason}`", inline=True)
            embed.set_footer(text=f"Kicked by {i.user.display_name}", icon_url=i.user.display_avatar.url)
            await i.followup.send(embed=embed)


        # ================== 2. PERMANENT BAN ==================
        elif mode.value == "ban":
            if not user_id: return await i.followup.send("❌ **Roblox ID Required!**")
            u, d = await roblox_info(user_id)
            
            # ✅ FIX: Async DB Call
            await db_call(lambda: supabase.table("bans").upsert({
                "user_id": user_id, "perm": True, "reason": reason, "expire": None, "executor": str(i.user.id)
            }).execute())

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
            if not duration: return await i.followup.send("⚠️ **Duration Required!**")

            u, d = await roblox_info(user_id)
            expire_time = time.time() + (duration * 60)

            # ✅ FIX: Async DB Call
            await db_call(lambda: supabase.table("bans").upsert({
                "user_id": user_id, "perm": False, "reason": reason, "expire": expire_time, "executor": str(i.user.id)
            }).execute())

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
            
            # ✅ FIX: Async DB Call
            await db_call(lambda: supabase.table("bans").delete().eq("user_id", user_id).execute())

            try: log_action("unban", user_id, u, d, i.user.id)
            except: pass

            embed = discord.Embed(title="✅ USER UNBANNED", color=0x2ecc71)
            embed.add_field(name="👤 User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="🆔 ID", value=f"`{user_id}`", inline=True)
            embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
            await i.followup.send(embed=embed)


        # ================== 5. LIST BANS ==================
        elif mode.value == "list":
            # ✅ FIX: Async DB Call for fetching list
            data_req = await db_call(lambda: supabase.table("bans").select("*").execute())
            data = data_req.data if data_req else []

            # Filter Expired Bans
            active_bans = []
            now = time.time()
            for row in data:
                if not row.get("perm") and row.get("expire") and now > float(row["expire"]):
                    # Expired ban delete karo (Background me)
                    asyncio.create_task(db_call(lambda: supabase.table("bans").delete().eq("user_id", row["user_id"]).execute()))
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

# ================== FINAL PLAYSOUND (SIMPLE OWNER CHECK) ==================

# 1. Autocomplete (List dikhane ke liye)
async def sound_autocomplete(i: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    folder_path = "./sounds"
    if not os.path.exists(folder_path): return []
    files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
    return [app_commands.Choice(name=f, value=f) for f in files if current.lower() in f.lower()][:25]

# 2. Command
@bot.tree.command(name="playsound", description="📂 GitHub sounds play karo (Owner Only)")
@app_commands.describe(filename="Sound select karo")
@app_commands.autocomplete(filename=sound_autocomplete)
async def playsound(i: discord.Interaction, filename: str):
    
    # 🔥 Waisa check jaisa tum chahte the 🔥
    if not owner(i):
        return await i.response.send_message("❌ **Access Denied:** Sirf Owner allowed hai!", ephemeral=True)

    # --- Iske aage VC aur Play logic ---

    if not i.user.voice:
        return await i.response.send_message("⚠️ Pehle VC join kar bhai!", ephemeral=True)

    await i.response.defer()

    try:
        file_path = f"./sounds/{filename}"
        
        # VC Connect Logic
        try:
            vc = await i.user.voice.channel.connect()
        except:
            vc = i.guild.voice_client

        if vc.is_playing(): vc.stop()

        # Play Audio
        vc.play(discord.FFmpegPCMAudio(source=file_path, executable="./ffmpeg"))
        
        await i.followup.send(f"🎶 **Playing:** `{filename}` 🌚")

    except Exception as e:
        await i.followup.send(f"❌ Error: {e}")            

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


# 2️⃣ VC ROAST (Premium Embed + Auto Voice)
@bot.tree.command(name="vcroast", description="Brutal Gaali Mode 🔊💀")
async def vcroast(interaction: discord.Interaction):
    if not has_voice_access(interaction):
        await interaction.response.send_message("🚫 **Access Denied:** Sirf VIP log chala sakte hain!", ephemeral=True)
        return

    # Premium Embed Response
    embed = create_premium_embed("💀 Brutal Mode On", f"**{current_voice['name']}** is connecting to roast you... 🔥")
    await interaction.response.send_message(embed=embed)
    
    # ☢️ LIST
    gaali_list = [
        "Teri maa ki chut mein haathi ka lund, saale nalle tu paida hi galti se hua tha.",
        "Teri maa ki chut mein JCB chala dungi, saari akad bahar nikal jayegi madarchod.",
        "Bhosadike, teri bhen ko itna chodungi ki wo chalna bhool jayegi, sirf reng ke chalegi.",
        "Saale suar ke pille, teri maa ki gaand mein cactus uga dungi, jab bhi hagegi mujhe yaad karegi.",
        "Teri shakal dekh ke lagta hai bhagwan ne tatti ko insaan ka roop de diya hai.",
        "Madarchod, tere khandan ki auratein mere lund ka wait karti hain, jaake pooch le.",
        "Abe randi ke, teri gaand mein rod daal ke mooh se nikalungi, human kebab bana dungi tera.",
        "Teri maa ka bhosada itna bada hai ki usme main apna poora ghar bana lu.",
        "Chutiye, tujhe paida karke teri maa ne duniya pe bojh badha diya hai, jaake mar ja.",
        "Teri bhen ki chut mein bomb laga ke uda dungi, chithade milenge seedha chand pe.",
        "Saale hijde ki aulad, mere saamne aawaz mat nikalna warna wahi gaad dungi.",
        "Teri maa ki chut mein itne lund daalungi ki wo traffic jam ho jayegi.",
        "Bhosadike, tera baap bhi rota hoga ki kis manhoos ghadi mein tujhe paida kiya.",
        "Randi ke pille, teri gaand mein mirchi ka powder bhar ke dande se andar kar dungi.",
        "Teri bhen ki chut public toilet ban gayi hai, jo aata hai moot ke chala jata hai.",
        "Madarchod, tujhe zinda jala ke teri raakh ko gutter mein bahana chahiye."
        "Bhenchod, apni shakal dekhi hai? Aisa lagta hai gutter ke dhakkan pe kisi ne ulti kar di ho.",
        "Madarchod, teri bhen ko kothe pe bitha dungi agar dubara yahan dikha toh, nikal yahan se!",
        "Saale randi ke pille, tere khandan mein sabse bada chutiya tu hi hai, jaake doob mar.",
        "Teri gaand mein itna danda daalungi ki muh se bahar niklega, bhosadike aukaat mein reh.",
        "Sun be lodu, teri maa mere paas aayi thi, keh rahi thi galti ho gayi tujhe paida karke.",
        "Abe suar ki aulad, tu wahi virus hai jise condom bhi rok nahi paaya tha.",
        "Teri bhen ki chut mein cactus daal ke ghumungi, saale tatti khor insaan."
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

# 4️⃣ GIVE VIP (Database Update)
@bot.tree.command(name="give_vip", description="Dosto ko VIP Access do 👑")
async def give_vip(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ **Sirf Owner hi naye VIP add kar sakta hai!**", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    try:
        check = supabase.table("voice_vip").select("user_id").eq("user_id", str(user.id)).execute()
        if check.data:
            await interaction.followup.send(f"⚠️ **{user.name}** pehle se VIP hai!")
        else:
            data = { "user_id": str(user.id), "added_by": str(interaction.user.name) }
            supabase.table("voice_vip").insert(data).execute()
            
            embed = create_premium_embed("✅ New VIP Added", f"{user.mention} ab `/bol` aur `/vcroast` use kar sakta hai!", 0x00FF00)
            await interaction.followup.send(embed=embed)
            
    except Exception as e:
        await interaction.followup.send(f"❌ **Error:** {e}")

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

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author_id: return await i.response.send_message("❌ You cannot use this button.", ephemeral=True)

        embed = discord.Embed(title="🛡️ Operation Cancelled", description="Access list safe hai.", color=0x2ecc71)
        await i.response.edit_message(embed=embed, view=None)
        self.stop()

# ================== PERMANENT GIVEAWAY SYSTEM (SUPABASE) ==================

class GiveawayView(discord.ui.View):
    def __init__(self, message_id):
        super().__init__(timeout=None)
        self.message_id = str(message_id)

    @discord.ui.button(label="🎉 Join Giveaway", style=discord.ButtonStyle.blurple, custom_id="join_giveaway_btn")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        msg_id = str(interaction.message.id)
        user_id = interaction.user.id

        # 1. DATABASE FETCH (Live Data)
        try:
            res = supabase.table("giveaways").select("*").eq("message_id", msg_id).execute()
            if not res.data:
                return await interaction.response.send_message("❌ Yeh giveaway database me nahi mila (Shayad delete ho gaya).", ephemeral=True)
            
            data = res.data[0]
            participants = data['participants'] # JSON List
            
        except Exception as e:
            return await interaction.response.send_message(f"⚠️ Database Error: {e}", ephemeral=True)

        # 2. 🛑 CHECKS (Already Joined?)
        if user_id in participants:
            # Leave Logic
            participants.remove(user_id)
            msg = "💔 Aapne giveaway leave kar diya."
        else:
            # Join Logic
            participants.append(user_id)
            msg = "✅ **Success:** Entry Confirmed! Good Luck! 🍀"

        # 3. DATABASE UPDATE (Save immediately)
        supabase.table("giveaways").update({"participants": participants}).eq("message_id", msg_id).execute()

        # 4. EMBED UPDATE (Show new count)
        embed = interaction.message.embeds[0]
        embed.set_field_at(1, name="👥 Entries", value=f"**{len(participants)}** Users", inline=True)
        
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message(msg, ephemeral=True)

# ================== PREMIUM GSTART (UPDATED BIG GIF) ==================

@bot.tree.command(name="gstart", description="💎 Start a Permanent Giveaway (Database)")
@app_commands.describe(prize="Prize name", duration="Time (10m, 1h, 1d)", winners="Winner count", image_url="Custom image link (Optional)")
async def gstart(i: discord.Interaction, prize: str, duration: str, winners: int, image_url: str = None):
    
    # Permission Check (Managers Only)
    # Agar sirf owner ke liye karna hai to yahan 'if not owner(i):' laga dena
    if not i.user.guild_permissions.manage_guild:
        return await i.response.send_message("❌ Sirf Managers giveaway start kar sakte hain!", ephemeral=True)

    # Time Logic
    unit = duration[-1].lower()
    time_val = int(duration[:-1])
    seconds = 0
    if unit == 'm': seconds = time_val * 60
    elif unit == 'h': seconds = time_val * 3600
    elif unit == 'd': seconds = time_val * 86400
    else: return await i.response.send_message("❌ Invalid Time! Use 10m, 1h, 1d (e.g., 10m)", ephemeral=True)

    end_time_dt = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    timestamp = int(end_time_dt.timestamp())

    # --- PREMIUM EMBED CREATION ---
    embed = discord.Embed(title="🎉 **ULTRA PREMIUM GIVEAWAY** 🎉", description=f"### 🎁 Prize: {prize}\n\n👇 **Click the button below to Join!**", color=0xFFD700)
    embed.add_field(name="⏰ Ends In", value=f"<t:{timestamp}:R>", inline=True)
    embed.add_field(name="👥 Entries", value="**0** Users", inline=True)
    embed.add_field(name="🏆 Winners", value=f"{winners}", inline=True)
    
    # Host info footer me
    embed.set_footer(text=f"Hosted by: {i.user.display_name} • Starting...", icon_url=i.user.display_avatar.url)
    
    # 🔥 NEW DEFAULT PREMIUM GIF (Big Banner Style) 🔥
    # Agar user ne apni image nahi di, to ye wali chalegi.
    default_img = "https://media1.tenor.com/m/XZThisaqECAAAAAC/giveaway-giveaway-alert.gif" 
    
    # `set_image` use karne se embed automatically BADA (Long) banta hai.
    embed.set_image(url=image_url if image_url else default_img)
    
    # Thumbnail option (Agar server ka icon lagana ho side me chota sa)
    if i.guild.icon:
        embed.set_thumbnail(url=i.guild.icon.url)

    await i.response.send_message("✅ Setting up giveaway...", ephemeral=True)
    msg = await i.channel.send(embed=embed)

    # Update View & Footer with ID
    view = GiveawayView(msg.id)
    embed.set_footer(text=f"Hosted by: {i.user.display_name} • ID: {msg.id}", icon_url=i.user.display_avatar.url)
    await msg.edit(embed=embed, view=view)

    # 🔥 SAVE TO SUPABASE (Permanent Storage) 🔥
    try:
        db_data = {
            "message_id": str(msg.id),
            "channel_id": str(i.channel.id),
            "prize": prize,
            "winners_count": winners,
            "end_time": str(end_time_dt),
            "host_id": str(i.user.id),
            "participants": [], # Empty list start me
            "ended": False
        }
        supabase.table("giveaways").insert(db_data).execute()
    except Exception as e:
        await i.channel.send(f"⚠️ **Database Error:** Giveaway start ho gaya, par database me save nahi hua! Reroll nahi chalega. Error: `{e}`")

    # Wait for end
    await asyncio.sleep(seconds)

    # --- ENDING LOGIC (Fetch fresh data from DB) ---
    res = supabase.table("giveaways").select("*").eq("message_id", str(msg.id)).execute()
    if res.data:
        data = res.data[0]
        users = data['participants']
        
        if len(users) < data['winners_count']:
            winner_text = "No one joined! 😢"
        else:
            winners_list = random.sample(users, data['winners_count'])
            winner_mentions = [f"<@{uid}>" for uid in winners_list]
            winner_text = ", ".join(winner_mentions)
            await i.channel.send(f"🎉 **CONGRATULATIONS!** {winner_text} won **{prize}**! 🎁")

        # Update Embed & Mark Ended in DB
        embed.color = 0x2B2D31
        embed.title = "🎊 GIVEAWAY ENDED 🎊"
        embed.description = f"### 🎁 Prize: {prize}\n\n👑 **Winner(s):** {winner_text}"
        embed.set_field_at(0, name="⏰ Status", value="Ended", inline=True)
        embed.set_image(url=None)
        
        await msg.edit(embed=embed, view=None)
        
        # Mark as ended in DB
        supabase.table("giveaways").update({"ended": True}).eq("message_id", str(msg.id)).execute()


@bot.tree.command(name="greroll", description="🔄 Reroll winner from Database (Restart Proof)")
async def greroll(i: discord.Interaction, giveaway_id: str, winners: int = 1):
    
    if not i.user.guild_permissions.manage_guild:
        return await i.response.send_message("❌ Managers only!", ephemeral=True)

    # 🔥 FETCH FROM DB (Restart hone ke baad bhi chalega)
    res = supabase.table("giveaways").select("*").eq("message_id", giveaway_id).execute()
    
    if not res.data:
        return await i.response.send_message("❌ Database me ye ID nahi mili!", ephemeral=True)

    data = res.data[0]
    participants = data['participants']

    if len(participants) < winners:
        return await i.response.send_message("❌ Not enough participants to reroll.", ephemeral=True)

    new_winners = random.sample(participants, winners)
    winner_text = ", ".join([f"<@{uid}>" for uid in new_winners])

    # Announce
    embed = discord.Embed(title="🔄 **REROLL RESULT**", description=f"### 🎁 Prize: {data['prize']}\n\n👑 **New Winner:** {winner_text}", color=0xFF0055)
    embed.set_footer(text=f"Rerolled by {i.user.display_name}")
    
    await i.response.send_message(f"🎉 **NEW WINNER:** {winner_text}", embed=embed)


@bot.tree.command(name="gcheck", description="🕵️ Check participants list from Database")
async def gcheck(i: discord.Interaction, giveaway_id: str):
    
    # 🔥 FETCH FROM DB
    res = supabase.table("giveaways").select("*").eq("message_id", giveaway_id).execute()
    
    if not res.data:
        return await i.response.send_message("❌ Invalid ID or Data deleted.", ephemeral=True)

    participants = res.data[0]['participants']
    
    if not participants:
        return await i.response.send_message("❌ Koi participants nahi hain.", ephemeral=True)

    # List banana
    names = []
    for uid in participants:
        names.append(f"<@{uid}> (`{uid}`)")

    desc = "\n".join(names)
    if len(desc) > 4000: # Agar list bahut lambi hai
        with open("list.txt", "w") as f: f.write("\n".join(names))
        await i.response.send_message(file=discord.File("list.txt"), ephemeral=True)
        os.remove("list.txt")
    else:
        embed = discord.Embed(title=f"👥 Participants ({len(names)})", description=desc, color=0x00ffea)
        await i.response.send_message(embed=embed, ephemeral=True)



# ================== 3. ULTIMATE ACCESS COMMAND (FIXED: Non-Blocking) ==================
@bot.tree.command(name="access", description="⚙️ Manage Access, Maintenance, Whitelist & Blacklist (Fixed)")
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
            val = "true" if mode.value == "on" else "false"
            # ✅ FIX
            await db_call(lambda: supabase.table("bot_settings").update({"value": val}).eq("key", "access_enabled").execute())
            
            status_emoji = "🟢" if mode.value == "on" else "🔴"
            color = 0x2ecc71 if mode.value == "on" else 0xe74c3c
            embed = discord.Embed(title=f"{status_emoji} System Updated", description=f"Verification Access is now **{mode.value.upper()}**", color=color)
            
            try: log_action(f"access_{mode.value}", "-", "-", "-", i.user.id)
            except: pass
            await i.followup.send(embed=embed)

        # ================== 2. MAINTENANCE ON/OFF ==================
        elif mode.value in ["maint_on", "maint_off"]:
            val = "true" if mode.value == "maint_on" else "false"
            # ✅ FIX
            await db_call(lambda: supabase.table("bot_settings").update({"value": val}).eq("key", "maintenance").execute())

            if mode.value == "maint_on":
                embed = discord.Embed(title="🛡️ Maintenance Enabled", description="⚠️ **System is now in Maintenance Mode.**", color=0xe67e22)
            else:
                embed = discord.Embed(title="🚀 Maintenance Disabled", description="✅ **System is now LIVE.**", color=0x2ecc71)
            
            try: log_action(f"maintenance_{val}", "-", "-", "-", i.user.id)
            except: pass
            await i.followup.send(embed=embed)

        # ================== 3. WHITELIST ADD ==================
        elif mode.value == "add":
            if not user_id: return await i.followup.send("❌ **ID required!**")
            u, d = await roblox_info(user_id)
            
            # ✅ FIX
            await db_call(lambda: supabase.table("access_users").upsert({"user_id": user_id, "username": u, "display_name": d, "discord_id": str(i.user.id)}).execute())
            
            try: log_action("access_add", user_id, u, d, i.user.id)
            except: pass
            
            embed = discord.Embed(title="✅ Access Granted", color=0x2ecc71)
            embed.add_field(name="User", value=f"{d} (@{u})", inline=True)
            await i.followup.send(embed=embed)

        # ================== 4. WHITELIST REMOVE ==================
        elif mode.value == "remove":
            if not user_id: return await i.followup.send("❌ **ID required!**")
            u, d = await roblox_info(user_id)
            
            # ✅ FIX
            await db_call(lambda: supabase.table("access_users").delete().eq("user_id", user_id).execute())
            
            try: log_action("access_remove", user_id, u, d, i.user.id)
            except: pass
            
            embed = discord.Embed(title="🗑️ Access Removed", color=0xff0000)
            embed.add_field(name="User", value=f"{d} (@{u})", inline=True)
            await i.followup.send(embed=embed)

        # ================== 5. WHITELIST LIST ==================
        elif mode.value == "list":
            # ✅ FIX
            data_req = await db_call(lambda: supabase.table("access_users").select("*").execute())
            data = data_req.data if data_req else []
            
            if not data: return await i.followup.send("❌ List is empty.")
            
            view = AccessPaginator(data, i.user)
            if view.total_pages <= 1: view.children[0].disabled = True; view.children[1].disabled = True
            else: view.update_buttons()
            await i.followup.send(embed=view.get_embed(), view=view)

        # ================== 6. BLACKLIST ADD ==================
        elif mode.value == "blk_add":
            if not user_id: return await i.followup.send("❌ **ID required!**")
            u, d = await roblox_info(user_id)

            # ✅ FIX: Dono call async wrapper me
            await db_call(lambda: supabase.table("blacklist_users").upsert({"user_id": user_id}).execute())
            try: await db_call(lambda: supabase.table("access_users").delete().eq("user_id", user_id).execute())
            except: pass

            try: log_action("blacklist_add", user_id, u, d, i.user.id)
            except: pass

            embed = discord.Embed(title="🚫 User Blacklisted", color=0x000000)
            embed.add_field(name="User", value=f"{d} (@{u})", inline=True)
            await i.followup.send(embed=embed)

        # ================== 7. BLACKLIST REMOVE ==================
        elif mode.value == "blk_remove":
            if not user_id: return await i.followup.send("❌ **ID required!**")
            u, d = await roblox_info(user_id)

            # ✅ FIX
            await db_call(lambda: supabase.table("blacklist_users").delete().eq("user_id", user_id).execute())

            try: log_action("blacklist_remove", user_id, u, d, i.user.id)
            except: pass

            embed = discord.Embed(title="✅ Blacklist Removed", color=0x3498db)
            embed.add_field(name="User", value=f"{d} (@{u})", inline=True)
            await i.followup.send(embed=embed)

        # ================== 8. BLACKLIST LIST ==================
        elif mode.value == "blk_list":
            # ✅ FIX
            data_req = await db_call(lambda: supabase.table("blacklist_users").select("user_id").execute())
            data = data_req.data if data_req else []
            
            if not data: return await i.followup.send("✅ No users blacklisted.")

            view = BlacklistPaginator(data, i.user)
            if view.total_pages <= 1: view.children[0].disabled = True; view.children[1].disabled = True
            else: view.update_buttons()
            
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
