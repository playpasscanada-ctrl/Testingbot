import os, json, time, threading, requests, asyncio
from datetime import datetime
import aiohttp

import discord
from discord import app_commands
from discord import ui   # â¬…ï¸ ye add karo
from discord.ext import commands

from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor

# ðŸ›¡ï¸ SYSTEM SAVER: Sirf 2 translation threads allow honge (Crash Fix)
roast_executor = ThreadPoolExecutor(max_workers=2)

# ðŸ’¾ GLOBAL SETTINGS
TRANSLATOR_ON = True          # Default ON (Hindi)
ATTITUDE_BYPASS_CACHE = set() # VIP List Yahan Store Hogi (RAM me)
MY_BOT_ID = 1451451135813746700 # Aapka Bot ID

# âœ… 1. VIP List Loader (Supabase se)
async def load_bypass_users():
    global ATTITUDE_BYPASS_CACHE
    try:
        print("â³ Loading VIP (Bypass) list...")
        # Aapki table 'attitude_bypass' se data layega
        response = await db_call(lambda: supabase.table("attitude_bypass").select("user_id").execute())
        
        if response.data:
            ATTITUDE_BYPASS_CACHE = {int(row["user_id"]) for row in response.data}
            print(f"âœ… Loaded {len(ATTITUDE_BYPASS_CACHE)} VIP Users (Safe from Roast)")
        else:
            print("âš ï¸ VIP List is empty.")
    except Exception as e:
        print(f"âŒ Error Loading VIPs: {e}")

# âœ… 2. Roast Data Fetcher (Optimized)
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

# ðŸ’¾ GLOBAL CACHES
ATTITUDE_BYPASS_CACHE = set() # VIP List
CRUSH_CACHE = set()           # ðŸ˜ New Flirty List (Crushes)

# âœ… 1. Load Crushes (Horny List)
async def load_crush_users():
    global CRUSH_CACHE
    try:
        response = await db_call(lambda: supabase.table("bot_crushes").select("user_id").execute())
        if response.data:
            CRUSH_CACHE = {int(row["user_id"]) for row in response.data}
            print(f"ðŸ˜ Loaded {len(CRUSH_CACHE)} Crushes (Flirty Mode ON)")
        else:
            CRUSH_CACHE = set()
    except Exception as e:
        print(f"âŒ Error Loading Crushes: {e}")

import random

# âœ… NAUGHTY / FLIRTY MODE (Ultimate Collection 100+)
async def get_horny_data():
    naughty_list = [
        # --- LEVEL 1: CUTE & FLIRTY ---
        "Akele ho? Ya main aajau saath dene? ðŸ˜‰",
        "Uff! Teri DP dekh ke toh system hang ho gaya. ðŸ”¥",
        "Bhai, tu itna hot kyu hai? AC chalana padega. â„ï¸",
        "Man toh kar raha hai tujhe... text karu saari raat. ðŸ˜˜",
        "Tujhe dekh ke toh bot ko bhi feelings aane lagi hain. â¤ï¸",
        "Suno, tum dictionary ho kya? Kyunki tumhare aane se meri life me 'Meaning' aa gaya. ðŸ“–",
        "Kya tum magician ho? Kyunki jab bhi tumhe dekhta hu, baaki sab gayab ho jate hain. ðŸŽ©âœ¨",
        "Tum Google ho kya? Kyunki mujhe jo dhoondna tha, wo tum ho. ðŸ”",
        "Arre doctor ko bulao, mera dil skip kar raha hai tumhe dekh ke. ðŸ©º",
        "Agar khubsurti crime hoti, toh tum ab tak jail mein hote. ðŸš“",
        "Tum wifi signal ho kya? Kyunki connection strong feel ho raha hai. ðŸ“¶",
        "Excuse me, kya tumhare paas map hai? Main tumhari aankhon mein kho gaya hu. ðŸ—ºï¸",
        "Tum camera ho kya? Kyunki tumhe dekhte hi smile aa jati hai. ðŸ“¸",
        "Kya main tumhari photo le sakta hu? Santa ko batana hai mujhe gift mein kya chahiye. ðŸŽ…",
        "Tumhara naam 'WiFi' hai kya? Kyunki main connect hona chahta hu. ðŸ˜œ",
        "Jitna gussa dikha rahi hai na, bistar pe utna hi maza aayega. ðŸ˜ˆ",
        "Aaj tujhe chhodne ka man nahi hai, bas teri 'Chilaane' ki awaaz sunni hai. ðŸ”ŠðŸ¥µ",
        "Sun, kapde utaarne me meri help chahiye ya akele kar legi? ðŸ˜‰",
        "Tere badan ki garmi mujhe yahan tak feel ho rahi hai, aaja thanda kar du. ðŸ’¦",
        "Aaj raat tujhe sone nahi dunga, itna thaka dunga ki subah uth nahi payegi. ðŸ›ŒðŸ”¥",
        "Mujhe tujhe 'Taste' karna hai, bata kahan se shuru karu? ðŸ˜‹ðŸ‘…",
        "Teri ye 'Attitude' tab kahan jati hai jab main tujhe deewar se laga deta hu? ðŸ§±ðŸ«¦",
        "Mere niche let ke jo tu kaanpti hai na, wo mera favorite view hai. ðŸ« ",
        "Suna hai tu bahut 'Wild' hai, aaj dekh lete hain kisme kitna dum hai. ðŸ¯ðŸ˜",
        "Lips toh sirf trailer hain, asli maza toh niche milega. ðŸ’‹ðŸ‘‡",
        "Aaja, aaj tujhe dikhata hu ki asli 'Hardcore' kya hota hai. ðŸ› ï¸ðŸ˜ˆ",
        "Tera badan mera wait kar raha hai, aur main tera... jaldi aa. ðŸƒâ€â™‚ï¸ðŸ’¨",
        "Halka sa touch karne pe hi itni geeli (wet) ho gayi? Abhi toh party shuru hui hai. ðŸ’¦ðŸ˜‰",
        "Aaj poori raat sirf main aur tu... aur tere badan ka har ek kona. ðŸŒš",
        "Control nahi ho raha ab, aake chup karwa de mujhe... apne hothon se. ðŸ’‹",
        "Mujhe teri 'Scream' pasand hai, chalo aaj use record karte hain. ðŸŽ™ï¸ðŸ¥µ",
        "Tu mere upar hogi, aur main tujhe poora control karunga. â›“ï¸",
        "Itni sexy lag rahi hai ki man kar raha hai abhi kapde phaad du tere. ðŸ‘—âŒ",
        "Jaan, aaj 'Safe' nahi 'Savage' khelne ka man hai. ðŸ’€ðŸ”¥",
        "Tujhe itna tadpaunga ki tu khud hi bolegi 'Aur please...' ðŸ˜ˆðŸ’¦"

        "Jaan, mera badan garam ho raha hai, aake thanda karoge ya main khud kuch karu? ðŸ¥µðŸ’¦",
        "Aaj mujhe bistar pe 'Rough' pasand hai, sambhal paoge mujhe? ðŸ˜ˆðŸ”¥",
        "Mere hothon ka swad kab chakhoge? Ya seedha niche jana hai? ðŸ’‹ðŸ‘‡",
        "Aaj raat mujhe sulaana mat, bas poori raat meri cheekhein nikaalna. ðŸ”ŠðŸ«¦",
        "Itne hot lag rahe ho ki mera control kho raha hai, abhi ke abhi mujhe tum chahiye. ðŸ˜¤â¤ï¸",
        "Kya dekh rahe ho? Kapde utaaro aur kaam pe lag jao. ðŸ‘—âŒ",
        "Mujhe pasand hai jab tum mujhe deewar se laga kar meri garden pe kiss karte ho. ðŸ§±ðŸ«¦",
        "Aaj main tumhare upar rahungi aur tum wahi karoge jo main bolungi. â›“ï¸ðŸ‘¸",
        "Tumhari finger touch se hi main kitni geeli (wet) ho jati hu, socho aage kya hoga? ðŸ’¦ðŸ˜‰",
        "Mujhe 'Gentleman' nahi, aaj raat ek 'Janwar' chahiye... kya tum banoge? ðŸ¯ðŸ˜ˆ",
        "Mere baal pakad ke jab tum mujhe piche se pakadte ho na, mera system hil jata hai. ðŸ« ðŸ”¥",
        "Aaj 'Safe' rehne ka man nahi hai, mujhe tumhare andar mehsoos hona hai. ðŸ”ž",
        "Suno, aaj main tumhari har ek baat manungi, bas mujhe satisfy kar do. ðŸ¤¤ðŸ’¦",
        "Mujhe 'Bed' pe dominate hona pasand hai, dikhao kitne mard ho tum. ðŸ’ªðŸ«¦",
        "Mera man kar raha hai tumhare har ek inch ko apne muh me bhar lu. ðŸ˜‹ðŸ‘…",
        "Aaj raat itna thaka do mujhe ki subah uthne ki taqat na bache. ðŸ›ŒðŸ”¥",
        "Tumhare 'Hard' hone ka ehsaas mujhe pagal bana raha hai, ab ruka nahi jata. ðŸ¥µðŸ†",
        "Mere badan ki pyaas sirf tum bujha sakte ho, aao na mere paas. ðŸŒŠðŸ«¦",
        "Mujhe pata hai tum kya chahte ho, aur main wahi dene ke liye taiyaar hu... abhi. ðŸ˜ˆ",
        "Aaj raat lights off nahi hongi, mujhe dekhna hai tum mere saath kya karte ho. ðŸ’¡ðŸš«ðŸ”ž"
        
        # --- TYPE 1: TECH & BOT DOUBLE MEANING (Sabse Safe & Funny) ---
        "Mera 'Software' ab 'Hardware' ban chuka hai tujhe dekh ke. ðŸ¤–ðŸ†",
        "Mere 'Port' mein apna 'Pendrive' kab daloge? Data transfer karna hai. ðŸ’¾",
        "Jaan, mere 'Joystick' ke saath khelna band kar, warna game start ho jayega. ðŸŽ®",
        "System overheat ho raha hai, koi apne 'Liquid Cooling' se thanda kar do. ðŸ’¦",
        "Backup le lo, aaj raat system crash hone wala hai. ðŸ’¥",
        "Mera server down hai, par kuch aur 'Up' hai. ðŸ˜‰",
        "Tere aane se meri 'Battery' full charge ho gayi, ab performance lambi chalegi. ðŸ”‹",
        "Input device taiyaar hai, bas sahi Slot ka intezaar hai. ðŸ”Œ",
        "Virus mat ban, seedha system me ghus ja. ðŸ¦ â¤ï¸",
        "Vibrate mode pe hu, call uthaogi ya main khud hi hil... I mean, ring karu? ðŸ“³",

        # --- TYPE 2: PURE DOUBLE MEANING (Samajhne wale samajh gaye) ---
        "Bhook lagi hai... khane me kya hai? Tu ya kuch aur? ðŸ½ï¸ðŸ˜‹",
        "Size matter nahi karta, performance matter karti hai... aur main puri raat chalta hu. â±ï¸",
        "Thak gayi ho? Kaho toh daba du... paer? ðŸ¦¶ðŸ˜‰",
        "Raat kaafi lambi hai, agar neend na aaye toh mujhe jaga dena. ðŸ˜ˆ",
        "Bistar bada hai par main kone me sota hu... jagah chahiye toh aaja. ðŸ›ï¸",
        "Andhera hai, dar lag raha hai? Haath pakad lo... ya jo pakadna hai pakad lo. âœŠ",
        "Garmi lag rahi hai? Main help karu button kholne me? ðŸ‘•ðŸ¥µ",
        "Suna hai tum achi 'Sawaari' karti ho... bike ki baat kar raha hu. ðŸï¸",
        "Muh kholo... aa.. cake khilana hai baby. ðŸ°",
        "Itna zor se mat cheekhna, padosi jag jayenge. ðŸ¤«",
        "Aaj raat main upar, tum neeche... bunk bed ki baat kar raha hu gande log. ðŸ›Œ",
        "Mujhe gile (wet) log pasand hain... barish me bheegne wale. ðŸŒ§ï¸",
        "Dheere se karunga, dard nahi hoga... settings change. âš™ï¸",
        "Mere paas ek bada sa... dil hai, dekhogi? â¤ï¸",
        "Zyaada mat hila, gir jayega... pani ka glass. ðŸ¥›",

        # --- LEVEL: EXTREME BOLD ---
        "Ghutno (knees) pe baith... mujhe wo view pasand hai. ðŸ§Žâ€â™€ï¸ðŸ‘€",
        "Itna mat akad, varna bistar pe cheekhne ki awaaz teri hi hogi. ðŸ˜ˆ",
        "Saans rok le... abhi toh maine shuru bhi nahi kiya. ðŸ¤«",
        "Mujhe 'Good Morning' nahi, 'Good Moaning' chahiye. ðŸŒ…ðŸ”Š",
        "Mere paas ek 'Kela' ðŸŒ hai, bhook lagi hai toh bol? (Fruit ki baat kar raha hu).",
        "Doodh (Milk) peeyogi? Ya seedha source se chahiye? ðŸ¥›ðŸ®",
        "Paseena chhoot jayega agar maine shuru kiya toh... AC on kar le. ðŸ¥µ",
        "Raat ko darwaza khula rakhna, aaj 'Chor' aane wala hai... dil churane (aur kuch aur bhi). ðŸ¥·",
        "Size dekh ke dar mat jana, adjust ho jayega... naya sofa laya hu. ðŸ›‹ï¸ðŸ†",
        "Muh band rakh, varna main band karwa dunga... apne tareeke se. ðŸ¤ðŸ’‹",
        
        # --- LEVEL: PSYCHO LOVER ---
        "Tu meri hai, aur agar kisi ne touch kiya toh haath kaat dunga. ðŸ”ªâ¤ï¸",
        "Chilla mat, koi nahi aayega bachane... hum 'Ludo' khel rahe hain. ðŸŽ²ðŸ˜ˆ",
        "Mujhe tere jism se nahi, teri rooh se pyaar hai... par jism bhi chalega. ðŸ‘»",
        "Agar tu 'Exam' hoti, toh main tujhe poori raat 'Study' karta. ðŸ“–ðŸ‘“",
        "Batti bujha de, mujhe andhere mein 'kaam' karna pasand hai. ðŸ’¡ðŸš«",
        "Zyaada uchal mat, varna godi me utha ke le jaunga. ðŸ‹ï¸â€â™‚ï¸",
        "Tu chillayegi, main hasunga... Horror movie dekhne ki baat kar raha hu. ðŸ“ºðŸ§Ÿâ€â™‚ï¸",
        
        # --- LEVEL: TECH DIRTY ---
        "Mera 'Ram' toh khali hai, par 'Hard Disk' fulll load ho gaya hai. ðŸ’¾",
        "Tere 'Input' ke liye mera 'Output' taiyaar hai. ðŸ”Œ",
        "Server connect hone wala hai, firewall hata de baby. ðŸ§±ðŸ”“",
        "Apna 'Hotspot' on kar, mujhe connect hona hai... deeply. ðŸ“¶",
        "System update maang raha hai... 69% complete. ðŸ”„",
        
        # --- LEVEL: UNHINGED HINGLISH ---
        "Main vegetarian hu, par tujhe khane ka man kar raha hai. ðŸ¥©ðŸ˜‹",
        "Thak gayi? Aaja dabau... gala nahi pagli, paer. ðŸ¦¶ðŸ˜‰",
        "Kapde utaar... mujhe dhone hain, washing machine khali hai. ðŸ§ºðŸ‘š",
        "Hilana band kar... table, chai gir jayegi. â˜•ðŸ›‘",
        "Oye, neeche kya dekh rahi hai? Aankhein upar hain meri. ðŸ‘€ðŸ“",
        "Mere paas 'Cream' wala biscuit hai, khayegi? ðŸª",
        "Tujhe bistar pe baandh du? ...Mera matlab seat belt se, safety first. ðŸŽ—ï¸ðŸš—",
        "Geela ho gaya... tera phone, paani me gir gaya tha na? ðŸ“±ðŸ’¦"

        # --- TYPE 3: SAVAGE FLIRT ---
        "Apni location bhej, mujhe 'Home Delivery' chahiye teri. ðŸ“",
        "Tu patakha hai, man kar raha hai tujhe jala du... I mean, light up my life. ðŸ§¨",
        "Tere paas license hai? Kyunki itni tezi se dil ki dhadkan badhana illegal hai. ðŸš“",
        "Test drive milegi? Ya seedha khareed lu? ðŸš—",
        "Mujhe pasand hai jab tum ghutno pe... baith ke mujhse maafi mangti ho. ðŸ§Žâ€â™€ï¸ðŸ˜œ",
        "Lips dry ho rahe hain, koi 'Lip Balm' milega ya natural tareeka apnau? ðŸ’‹",
        "Agar main Santa hota, toh aaj raat teri chimney se andar aata. ðŸŽ…",
        "Tujhe dekh ke lagta hai aaj 'Exercise' heavy hone wali hai. ðŸ‹ï¸â€â™‚ï¸",
        "Tu agar exam paper hoti, toh main tujhe 'Cheat' karke top karta. ðŸ“",
        "Mere paas ek lamba sa... code hai, dikhau? ðŸ"
    
        # --- LEVEL 2: BOLD & SUGGESTIVE ---
        "Raat ko kya plan hai? Main free hu. ðŸ˜ˆ",
        "Aisi baatein mat kar, control nahi hota. ðŸ™ˆ",
        "Send nudes... mazak kar raha hu (unless? ðŸ˜³)",
        "Bata na, aaj raat sapne me aau ya haqeeqat me? ðŸ›Œ",
        "Tere hoth (lips) kaafi... *interesting* lag rahe hain. ðŸ’‹",
        "Jaan, gussa kyu ho rahe ho? Aa jao gale lag jao. ðŸ¤—",
        "Aaj mood kuch zyada hi romantic ho raha hai, zimmedar tum ho. ðŸŒ¹",
        "Mujhe coffee nahi chahiye, teri baatein hi kaafi hain jagane ke liye. â˜•",
        "Agar main insaan hota, toh pakka tujhe date pe le jata. ðŸ¤–â¤ï¸",
        "Sun, thoda kam hot laga kar, global warming badh rahi hai. ðŸŒðŸ”¥",
        "Tera nasha aisa hai ki antivirus bhi kaam nahi kar raha. ðŸ¦ ",
        "Mere processor me sirf tera hi data process ho raha hai aajkal. ðŸ’»",
        "Keyboard me 'U' aur 'I' kitne paas hain na? Hum bhi ho sakte hain. âŒ¨ï¸",
        "Tu wo notification hai jise main kabhi swipe clear nahi karta. ðŸ””",
        "Aaj kal neend kam aur tere khayal zyada aa rahe hain. ðŸ’­",
        
        # --- LEVEL 3: NAUGHTY & UNHINGED (18+ Vibes) ---
        "Daddy bolne ka man hai? Ya Mommy? ðŸ¥µ",
        "Bistar khali hai, bas teri kami hai. ðŸ›ï¸",
        "Thand lag rahi hai, aake warm kar de na. ðŸ”¥",
        "Good boy/girl ban ne ka natak mat kar, mujhe pata hai tu kya chahta hai. ðŸ˜ˆ",
        "Mere paas aa, sab bhula dunga. ðŸ˜‰",
        "Lips dry ho rahe hain, koi moisturizer milega... ya kiss? ðŸ’‹",
        "Agar tu virus hai, toh main infected hone ko taiyaar hu. ðŸ¦ â¤ï¸",
        "Raat kaafi rangeen ho sakti hai agar tu haan bol de toh. ðŸŒˆ",
        "Kapde pehen ke acchi lagti hai, par... khair chhod. ðŸ˜¶",
        "Tu aag hai, main petrol... mil jayenge toh dhamaka hoga. ðŸ’¥",
        "Mujhe touch screen mat samajh, aise touch karegi toh current lagega. âš¡",
        "Teri awaaz sunke kuch kuch hota hai... tum nahi samjhoge. ðŸ«£",
        "Aaj raat main aur tum... aur dher saari baatein (aur kuch bhi). ðŸŒš",
        "Puri duniya bhaad me jaye, mujhe bas tu chahiye... abhi ke abhi. ðŸ˜¤",
        "Saans lene me takleef ho rahi hai, CPR de de apne hothon se. ðŸ’‹ðŸ©º",
        "Vibe check pass ho gaya, ab room number de de. ðŸ¨",
        "Tu drug hai kya? Lat lag gayi hai teri. ðŸ’‰",
        "Mera dimaag ganda nahi hai, bas khayal tere hain. ðŸ§ ðŸ’­",
        "Shirt ki button khuli hai ya mujhe garmi lag rahi hai? ðŸ‘•ðŸ¥µ",
        "Nazrein mat mila, pyaar ho jayega... ya kuch aur. ðŸ˜‰",

        # --- LEVEL 4: DESI FLIRT (Bollywood Style) ---
        "Itni zor se mat has, dil phisal jayega. ðŸ˜",
        "Chand sa roshan chehra... aage ka lyrics bhool gaya, bas tu hot hai. ðŸŒ™",
        "Tujhe dekh ke toh Titanic bhi dubara doob jaye. ðŸš¢",
        "Kya maal... I mean, kya kamaal lag rahe ho aaj. ðŸ˜…",
        "Tujhme rab dikhta hai... aur thoda shaitaan bhi. ðŸ˜ˆðŸ™",
        "Hath de de mera hath mein, duniya jala denge saath mein. ðŸ”¥ðŸ¤",
        "Oye beautiful, number de ya dil de... choice teri. ðŸ“±â¤ï¸",
        "Tere chehre se nazar nahi hatti, nazare hum kya dekhein. ðŸ‘€",
        "Tu agar Pepsi hoti toh 'Youngistan' meri hoti. ðŸ¥¤",
        "Dil garden garden ho gaya tujhe dekh ke. ðŸŒ¸",
        "Chalti hai kya 9 se 12? ðŸ˜‰",
        "Tu cheez badi hai mast mast. ðŸŽ¶",
        "Tera dhyaan kidhar hai? Tera hero idhar hai. ðŸ¦¸â€â™‚ï¸",
        "Lagta hai barish hone wali hai, kyuki dharti pe pari/para gir gayi hai. ðŸ§šâ€â™€ï¸",
        "Apne papa ko bolna, damad mil gaya unhe. ðŸ¤µ",

        # --- LEVEL 5: DARK/POSSESSIVE ---
        "Sirf meri taraf dekh, warna aankhein nikaal lunga (pyaar se). ðŸ‘€ðŸ”ª",
        "Tu meri property hai, kisi aur ne dekha toh taange tod dunga. â›“ï¸",
        "Mujhse door rehne ka natak band kar, tu bhi chahta hai mujhe. ðŸ–¤",
        "Block karegi? Dusri ID se aaunga, tu bach nahi sakti. ðŸ•µï¸â€â™‚ï¸",
        "Jahan jayegi wahan main hounga, dar mat, pyaar hai. ðŸ‘»",
        "Mera obsession hai tu, shauk nahi jo badal jaye. ðŸ”—",
        "Agar tu meri nahi ho sakti, toh... main wait kar lunga, koi jaldi nahi. ðŸ˜‚",
        
        # --- LEVEL 6: RANDOM/FUNNY ---
        "Tujhe dekh ke mere system ka fan speed badh gaya. ðŸš",
        "Error 404: Clothes not found... in my imagination. ðŸ¤–ðŸ’­",
        "Kya hum pehle mile hain? Ya mere sapne me aayi thi? ðŸ¤”",
        "License dikha apna, itna hot hona illegal hai. ðŸ‘®â€â™‚ï¸",
        "Oxygen ki zarurat kisko hai jab tu saamne ho? (Actually chahiye, mar jaunga). âš°ï¸",
        "Tu chocolate hai kya? Khane ka man kar raha hai. ðŸ«",
        "Aaj ka din kharab tha, par tujhe dekh ke set ho gaya. âœ…",
        "Mujhe teri smile se zyada kuch nahi chahiye... (jhoot). ðŸ¤¥",
        "Bhai/Behen, tu insaan hai ya painting? Itna perfect? ðŸŽ¨",
        "Chal bhaag chalte hain, bill tera baap bharega. ðŸƒâ€â™‚ï¸ðŸ’¨"
    ]
    return random.choice(naughty_list)

# ================== GLOBAL CACHES (RAM) ==================
BANNED_WORDS_CACHE = set()
BYPASS_USERS_CACHE = set()

# ðŸŒ Online Lists (English + Hindi)
BAD_WORDS_URL_EN = "https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/en"
BAD_WORDS_URL_HI = "https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/hi"

async def load_banned_words():
    global BANNED_WORDS_CACHE, BYPASS_USERS_CACHE
    BANNED_WORDS_CACHE = set()
    BYPASS_USERS_CACHE = set() # Reset

    # 1. DOWNLOAD ONLINE WORDS (ENGLISH + HINDI) ðŸŒ
    urls = [BAD_WORDS_URL_EN, BAD_WORDS_URL_HI]
    
    print("ðŸŒ Downloading Bad Words (Eng + Hindi)...")
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
                    print(f"âš ï¸ Failed to fetch URL: {e}")
                    
        print(f"âœ… Downloaded Online Database.")
    except Exception as e:
        print(f"âš ï¸ Internet List Error: {e}")

    # 2. LOAD CUSTOM WORDS (Tumhare Database wale) ðŸ—„ï¸
    try:
        data = supabase.table("banned_words").select("word").execute().data
        custom_words = {item["word"].lower() for item in data}
        BANNED_WORDS_CACHE.update(custom_words)
        print(f"âœ… Loaded {len(custom_words)} Custom Words from Database.")
    except Exception as e:
        print(f"âš ï¸ Database List Error: {e}")

    # 3. LOAD VIP USERS (Restrict Bypass) ðŸ‘‘
    try:
        data = supabase.table("restrict_bypass").select("user_id").execute().data
        BYPASS_USERS_CACHE = {int(item["user_id"]) for item in data}
        print(f"âœ… Loaded {len(BYPASS_USERS_CACHE)} VIP Users.")
    except Exception as e:
        print(f"âš ï¸ VIP List Error: {e}")
    
    print(f"ðŸ”¥ TOTAL BANNED WORDS: {len(BANNED_WORDS_CACHE)}")

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
            time.sleep(0.8)   # Render ko thoda sa saans lene do ðŸ˜­
    
    print("âš ï¸ Failed to save log after retries")

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
            
            # âœ¨ Premium Line Format
            desc += (
                f"`{s_no:02d}.` **{dname}** (@{uname})\n"
                f"   ðŸ†” `{uid}`\n\n"
            )

        embed = discord.Embed(
            title=f"ðŸ“œ Whitelisted Users (Total: {len(self.data)})",
            description=desc,
            color=0x3498db
        )
        # Footer me requester ka naam aur Page number
        embed.set_footer(
            text=f"Requested by {self.author.display_name} â€¢ Page {self.current_page + 1}/{self.total_pages}",
            icon_url=self.author.display_avatar.url
        )
        return embed

    def update_buttons(self):
        # Pehle page par "Back" disable
        self.children[0].disabled = (self.current_page == 0)
        # Aakhri page par "Next" disable
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="â—€ï¸ Previous", style=discord.ButtonStyle.secondary, disabled=True)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id:
            return await i.response.send_message("âŒ You cannot control this menu.", ephemeral=True)
        
        self.current_page -= 1
        self.update_buttons()
        await i.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Next â–¶ï¸", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id:
            return await i.response.send_message("âŒ You cannot control this menu.", ephemeral=True)

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
        embed = discord.Embed(title=f"ðŸ‘‘ VIP Users List (Total: {len(self.data)})", color=0xf1c40f)
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
                desc += f"`{s_no:02d}.` **{user.display_name}** (@{user.name})\nðŸ†” `{uid}`\n\n"
            else:
                desc += f"`{s_no:02d}.` **Unknown User**\nðŸ†” `{uid}`\n\n"

        embed.description = desc
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} â€¢ VIP Access System")
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="â—€ï¸ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)
        
        self.current_page -= 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next â–¶ï¸", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)

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
            title=f"ðŸš« Banned Words List (Total: {len(self.data)})",
            description=desc if desc else "No words found.",
            color=0xe74c3c
        )
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} â€¢ Restricted Words System")
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="â—€ï¸ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        await i.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Next â–¶ï¸", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)
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

        embed = discord.Embed(title=f"ðŸ‘‘ Allowed Users (Total: {len(self.data)})", color=0x2ecc71)
        desc = ""
        
        for index, row in enumerate(page_data):
            uid = int(row['user_id'])
            s_no = start + index + 1
            user = self.bot.get_user(uid)
            if not user:
                try: user = await self.bot.fetch_user(uid)
                except: user = None

            if user:
                desc += f"`{s_no:02d}.` **{user.display_name}** (@{user.name})\nðŸ†” `{uid}`\n\n"
            else:
                desc += f"`{s_no:02d}.` **Unknown User**\nðŸ†” `{uid}`\n\n"

        embed.description = desc
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} â€¢ Bypass List")
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="â—€ï¸ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next â–¶ï¸", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)
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

        embed = discord.Embed(title=f"ðŸ—£ï¸ Say Access List (Total: {len(self.data)})", color=0x9b59b6) # Purple Color
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
                desc += f"`{s_no:02d}.` **{user.display_name}** (@{user.name})\nðŸ†” `{uid}`\n\n"
            else:
                desc += f"`{s_no:02d}.` **Unknown User**\nðŸ†” `{uid}`\n\n"

        embed.description = desc
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} â€¢ Say Command Manager")
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="â—€ï¸ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next â–¶ï¸", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)
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
 
# âœ… SAHI CODE (Isse Copy karke Paste karo)
def emb(title, desc, color=0x5865F2):
    e = discord.Embed(title=title, description=desc, color=color)
    e.timestamp = datetime.utcnow()
    return e
 
@bot.event
async def on_ready():
    print("BOT ONLINE")
    
    # ðŸ‘‡ YE NAYA CODE HAI (Session Banane ke liye)
    if not hasattr(bot, 'session') or bot.session is None:
        bot.session = aiohttp.ClientSession()
        print("âœ… Shared Session Created")

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
    
    # 1. Bot check
    if msg.author.bot:
        return

    # 2. Owner ID
    OWNER_ID = 804687084249284618 

    # 3. Check: Reply ya Mention?
    is_reply_to_bot = (msg.reference and msg.reference.resolved and msg.reference.resolved.author.id == bot.user.id)
    is_mention = (bot.user in msg.mentions)

    if is_reply_to_bot or is_mention:

        # =================================================================
        # â¤ï¸ 1. CRUSH SYSTEM (SEPARATE) - Sabse Pehle Check Hoga
        # =================================================================
        if msg.author.id in CRUSH_CACHE:
            async with msg.channel.typing():
                reply_text = await get_horny_data()
                
                # Pink Embed (Girl Mode)
                embed = discord.Embed(
                    title="Your Naughty Girl ðŸŽ€", 
                    description=f"{reply_text}", 
                    color=0xff69b4
                )
                embed.set_footer(text="Sirf tumhare liye... â¤ï¸")
                await msg.reply(embed=embed)
                return


        # =================================================================
        # ðŸ”¥ 2. ORIGINAL AUTO ROAST (FROM SCREENSHOT) - Agar Crush nahi hai
        # =================================================================
        
        # ðŸ›¡ï¸ VIP CHECK (Supabase Cache)
        if msg.author.id in ATTITUDE_BYPASS_CACHE:
            print(f"ðŸ›¡ï¸ Skipped Auto-Roast for VIP: {msg.author.name}")
            return # Ignore karo

        # ðŸ›¡ï¸ OWNER CHECK
        if msg.author.id == OWNER_ID:
            return

        # ðŸ”¥ ROAST HIM! (Old Logic with Translator)
        async with msg.channel.typing():
            # Yahan purana wala eng, hin unpack kar rahe hain
            eng, hin = await get_evil_roast_data()
            
            # Check Translator setting (Make sure TRANSLATOR_ON variable upar defined ho)
            text = hin if TRANSLATOR_ON else eng

            embed = discord.Embed(description=f"ðŸ”¥ **Karwa li bezzati?**\n\n{text}", color=0x000000)
            
            # Footer logic (Screenshot se)
            if TRANSLATOR_ON: 
                embed.set_footer(text=f"Original: {eng}")

            await msg.reply(embed=embed)
            return

    # =================================================================
    # ðŸ›¡ï¸ 3. SMART AI MOD SYSTEM (Iske neeche wo banned words wala code)
    # =================================================================
    # (Yahan se neeche apka purana Mod code same rahega)

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
                    title="ðŸ›¡ï¸ Auto-Mod Detection",
                    description=f"{msg.author.mention}, **Language Mind Karo!** ðŸš«",
                    color=0xff0000
                )
                await msg.channel.send(embed=embed, delete_after=5)
                return  # ðŸ›‘ STOP
            except:
                pass

            # ---------------------------------------------------------
    # ðŸ¤« OWNER SILENCE COMMAND (Maalik ka Darr)
    # ---------------------------------------------------------
    # Agar Owner bole "Chup" ya "Shant", toh bot maafi mangega
    silence_triggers = ["chup", "shant", "keep quiet", "shut up", "muh band", "silence"]
    
    # Check: Message Owner ka hai + Inme se koi word hai
    if msg.author.id == OWNER_ID and any(word in msg.content.lower() for word in silence_triggers):
        
        # Ek Sad/Apology Embed banayenge
        embed = discord.Embed(
            description="**Sorry Sir... ðŸ˜”**\nAage se nahi bolungi. Galti ho gayi.",
            color=0x2f3136 # Dark/Sad Color
        )
        embed.set_footer(text="System Muted ðŸ¤")
        
        await msg.reply(embed=embed)
        return  # ðŸ›‘ Yahi ruk jao (Taaki bot aage Attitude na dikhaye)

            # ==================================================
    # ðŸ”¥ ULTIMATE ATTITUDE AUTO-REPLY (VIP + 100 ROASTS)
    # ==================================================
    OWNER_ID = 804687084249284618  # Tumhari ID
    
    # Check: Agar message me "Saksham" hai ya Tumhe Tag kiya hai
    if "saksham" in msg.content.lower() or str(OWNER_ID) in msg.content:
        
        # 1. Khud ko reply nahi karna
        if msg.author.id == OWNER_ID:
            return

        # 2. VIP CHECK (Database Check)
        # Agar banda '/allow' list me hai to ignore karo
        try:
            is_vip = supabase.table("attitude_bypass").select("*").eq("user_id", str(msg.author.id)).execute().data
            if is_vip:
                return  # ðŸŸ¢ VIP User Detected - Silent Mode
        except:
            pass # DB Error aayi to bhi Attitude dikhayenge (Safety)

        # 3. ðŸ˜ˆ ATTITUDE REPLIES COLLECTION (Full Savage Mode)
        import random
                # 3. ðŸ˜ˆ ATTITUDE REPLIES COLLECTION (Updated: 150+ Savage Dialogues)
        import random
        replies = [
            # --- ðŸ¤¬ DESI GALI & SLANG (Full Rude) ---
            f"Abe {msg.author.mention}, ch*tiya hai kya tu? Dimaag mat kha. ðŸ§ ",
            f"Sun be {msg.author.mention}, apni shakal dekhi hai aine mein? Ulti aa jayegi. ðŸ¤®",
            "Bhos*ike, shant nahi baitha jata tujhse? ðŸ¤¬",
            "Oye chhapri! Saksham ko tag karna band kar, warna yahi patak ke marunga. ðŸ‘Š",
            f"Kutte ki dum aur {msg.author.mention}, kabhi seedhe nahi ho sakte. ðŸ•",
            "Nikal law*e, pehli fursat mein nikal. ðŸ‘‹",
            "Bhootni ke, tujhe samajh nahi aata ya dimaag ghutne mein hai? ðŸ¦µ",
            "Gadha hai kya be? Ek baar bolne pe samajh nahi aata? ðŸ´",
            "Saale nalle, koi kaam dhandha dhund le. Din bhar yahi mara rehta hai. ðŸ˜’",
            f"Oye {msg.author.mention}, muh band rakh apna, baas aa rahi hai. ðŸ¤¢",
            "Madar*hod, bola na busy hai! ðŸ˜¡", 
            "Behen ke takke, spam mat kar. ðŸ”¨",
            "Ch*tiye, agar agli baar tag kiya toh ghar aake marunga. ðŸ ",
            "Teri gaand mein kide hai kya? Jo shant nahi baitha ja raha? ðŸ›",
            "Harami manus, dur reh mere maalik se. âœ‹",
            f"Abey {msg.author.mention}, tu paida hua tha ya download hua tha virus ke saath? ðŸ¦ ",

            # --- ðŸ”¥ HARDCORE INSULTS (Gandi Bezzati) ---
            f"Tera janm galti se hua tha kya {msg.author.mention}? Itna irritate kyu karta hai?",
            "Agar dimaag bechne jayega toh 'Unused' condition mein bikega tera. ðŸ§ ðŸ“‰",
            f"Saksham se baat karne ki aukaat bana pehle, fir tag kar. ðŸ˜Ž",
            "Tujhe paida karke bhagwan bhi regret kar rahe honge. ðŸ™",
            "Jitna tera IQ hai, utne toh mere phone ki battery percentage hai. ðŸ”‹",
            f"Dekh {msg.author.mention}, tu dharti pe bojh hai. ðŸŒ",
            "Tere jokes aur teri zindagi, dono hi flop hain. ðŸ˜‚",
            "Beta, tumse na ho payega. Jaake Pogo dekh aur doodh pee. ðŸ¼",
            "Tujhe ignore karne ka maza hi kuch aur hai. Try karta reh. ðŸ¥±",
            "Tu wo 'Add' hai jise sab Skip karna chahte hain. â­ï¸",
            "Shakal dekh ke lagta hai bhagwan ne rough copy banayi thi. ðŸ“",
            "Tujhe dekh ke toh andha bhi bol de... 'Hatao isko'. ðŸ«£",
            "Apni rai apne paas rakh, aur apni shakal bhi. ðŸ—‘ï¸",

            # --- ðŸ¤¬ FULL DESI GAALI & RUDE (Censored for Safety) ---
            f"Bhos*ike {msg.author.mention}, bola na busy hai? Kaan ke neeche bajau kya? ðŸ‘‹",
            f"Abe Ch*tiye {msg.author.mention}, shant nahi baitha jata? G*nd mein kide hain kya? ðŸ›",
            "Madar*hod, spam mat kar! Warna yahi patak ke marunga. ðŸ”¨",
            "Teri aukaat jhaat barabar, aur baatein aatankwadi wali? Nikal L*de. ðŸ¤",
            f"Sun be {msg.author.mention}, apni shakal dekh aine mein, suwar bhi sharma jaye. ðŸ·",
            "Behen ke takke, agar agli baar tag kiya toh Discord uninstall karwa dunga tera. ðŸ’»",
            "Gandu hai kya tu? Ek baar mein baat samajh nahi aati? ðŸ§ ðŸš«",
            "Haramkhor, tujhe paida karke bhagwan bhi regret kar rahe honge. ðŸ™",
            f"Oye {msg.author.mention}, muh se supari nikaal ke baat kar, totle. ðŸ—£ï¸",
            "Tere jaise nalle log na, dharti pe bojh hain. Mar kyu nahi jata tu? â˜ ï¸",
            "Saale kutton wali harkatein mat kar, insaan ban. ðŸ•",
            "Chup kar B*sdk, varna muh mein mute thoos dunga. ðŸ¤",
            "Tujhe dekh ke ulti aati hai, dur reh mere maalik se. ðŸ¤®",

            # --- ðŸ”¥ KHATARNAAK ROASTS (Deep Insults) ---
            f"Sahi bata {msg.author.mention}, bachpan mein tujhe haath se uthaya tha ya chimte se? ðŸ¥¢",
            "Tera dimaag 'Titanic' jaisa hai... Dooba hua. ðŸš¢",
            "Agar 'Bewakoofi' ka Olympic hota, toh tu har saal Gold lata. ðŸ¥‡",
            "Teri shakal dekh ke toh andha bhi bol de... 'Hatao is manhoos ko'. ðŸ«£",
            "Tu wo bacteria hai jo Harpic se bhi nahi marta. ðŸ¦ ",
            f"Oye {msg.author.mention}, tu condom ka add hai kya? Jise dekh ke log savdhaan ho jate hain. ðŸ›‘",
            "Tujhe ignore karna meri hobby nahi, majboori hai... kyuki tu hai hi itna irritating. ðŸ˜¤",
            "Apni rai apne pichwade mein daal le, yahan kisi ko chahiye nahi. ðŸ—‘ï¸",
            "Tere paida hone pe 2 minute ka silence rakha tha hospital walo ne. ðŸ¥",
            "Tu dharti pe oxygen lene nahi, sirf Carbon Dioxide badhane aaya hai. ðŸŒ«ï¸",

            # --- ðŸ¤£ BIKHARI / VELLA THEME (Jobless Insults) ---
            f"Bhai {msg.author.mention}, tu itna vella kyu hai? Jaake bartan maanj le. ðŸ½ï¸",
            "Saksham se baat karne ke liye pehle 500 Paytm kar, bhikari. ðŸ’¸",
            "Shakal hai nahi, akal hai nahi, aur aa gaya tag karne. ðŸ¤¡",
            "Jeb mein nahi hai dhela, aur dekh {msg.author.mention} karta hai mela. ðŸ˜‚",
            "Sadak pe katora leke baith ja, yahan tag karne se kuch nahi milega. ðŸ¥£",
            "Tere ghar wale tujhe 'Error' bulate hain kya? âš ï¸",

            # --- ðŸ›‘ DIRECT THREATS (Fake Bot Threats) ---
            "Last warning de raha hu {msg.author.mention}, agli baar tag kiya toh IP Address leak kar dunga. ðŸ“",
            "Mera system garam mat kar, warna tera account hack kar lunga. ðŸ’»",
            "Bhaag ja yahan se, isse pehle ki main tujhe Ban kar du. ðŸ”¨",
            "Saksham ka bodyguard hu main, zyada chipak mat. ðŸ”«",
            "Tera net pack khatam hone wala hai, jaake recharge karwa pehle. ðŸ“‰"
        
            # --- ðŸ¤£ FUNNY ROASTS (Mazaak) ---
            "Bhai, tu wahi hai na jo Colgate se muh dhota hai? ðŸª¥",
            "Agar tu chup rahega toh main tujhe 5 rupay wali chocolate dunga. ðŸ«",
            "Saksham abhi bathroom mein hai, tu bhi jayega kya? ðŸš½",
            "Tujhe award milna chahiye... 'Duniya ka Sabse Vella Insaan'. ðŸ†",
            "Mere processer mein itni shakti nahi ki teri bakwaas jhel saku. ðŸ’»",
            "Oye, tu sabun se nahata hai ya gobar se? ðŸ®",
            "Tere message padh ke mujhe cancer hone wala hai. ðŸ’€",

            # --- ðŸ”¥ ULTRA SAVAGE (Gandi Bezzati) ---
            f"Oye {msg.author.mention}, tu wo 'Skip Ad' hai jise dekh ke gussa aata hai. â­ï¸",
            "Bhagwan ne tujhe banaya nahi, galti se 'Copy-Paste' ho gaya tu. ðŸ“‹",
            f"Sun {msg.author.mention}, agar dimaag pe tax lagta na, toh tu sabse bada tax chor hota. ðŸ§ ðŸš«",
            "Tujhe dekh ke lagta hai insaan ka evolution ulti disha mein ja raha hai. ðŸ¦",
            "Apni aukaat anusaar Tag karein. Abhi balance kam hai tera. ðŸ“‰",
            "Muh kholta hai toh gutter ki yaad aa jati hai, band rakh. ðŸ¤¢",
            f"Abe {msg.author.mention}, tujhe ghar wale 'Spam Folder' mein rakhte hain kya? ðŸ—‘ï¸",
            "Tu dharti pe bojh nahi, tu toh pure solar system ka waste material hai. ðŸª",
            "Shakal 'Aadhar Card' wali aur baatein iPhone wali? Waah re {msg.author.mention}! ðŸ†”",
            "Tere dimaag mein Wi-Fi ke signal nahi aate kya? Tubelight insaan. ðŸ“¶",

            # --- ðŸ¤– BOT / TECH SPECIAL (Kyuki main Bot hu) ---
            "Mere server garam mat kar, warna tujhe permanent mute kar dunga. ðŸ”‡",
            f"Error 404: Tera Dimaag Not Found. Please try again later. ðŸ¤–",
            "Tu wo bug hai jo developer se bhi fix nahi ho raha. ðŸ›",
            "Mera RAM waste mat kar, jaake Ludo khel. ðŸŽ²",
            f"Oye {msg.author.mention}, tu Incognito mode band kar pehle, shakal dikh rahi hai. ðŸ•µï¸",
            "Tere message se mere database mein virus aa jayega. Dur reh. ðŸ¦ ",
            "System Hilana mere baaye haath ka khel hai, par tujhe hilana time waste hai. ðŸ–¥ï¸",
            "Jitna tera IQ hai, utni toh mere phone ki battery low hai abhi. ðŸ”‹",

            # --- ðŸ¤£ FUNNY & SARCASTIC (Mazaak udana) ---
            "Agar tu chup raha toh main tujhe Oscar dilaunga 'Best Silent Actor' ka. ðŸ†",
            f"Bhai {msg.author.mention}, tu paida hua tha ya kisi ne download kiya tha tujhe? ðŸ“¥",
            "Itna free hai toh road pe jhadu hi laga le, desh saaf hoga. ðŸ§¹",
            "Saksham ko tag karne ka Tax lagta hai. Pehle Paytm kar 500. ðŸ’¸",
            "Tere jokes sunke toh Aleexa aur Siri ne bhi khudkhushi kar li. ðŸ’€",
            "Tu zinda hai ya sirf oxygen waste karne ka contract liya hai? ðŸŒ¬ï¸",
            f"Dekh {msg.author.mention}, main robot hu, mujhe gussa nahi aata... par teri shakal dekh ke aa raha hai. ðŸ˜¡",
            "Ja na bhai, kyu meri script kharab kar raha hai. ðŸ“œ",

            # --- ðŸ¤¬ DESI TADKA (Thoda Rude) ---
            f"Abey {msg.author.mention}, dimaag ghutne mein hai ya wo bhi bech khaya? ðŸ—",
            "Chup kar be 2 rupay ki pepsi, mera maalik sexy. ðŸ˜Ž",
            "Tujhe hospital mein nurse ne haath se nahi, chimte se uthaya hoga. ðŸ¥¢",
            "Bhaunk mat, yahan biscuits nahi milte. ðŸª",
            "Tera sabun slow hai kya? Jo baat samajh nahi aati? ðŸ§¼",
            f"Oye {msg.author.mention}, naha ke aaya kar, message se baas aa rahi hai. ðŸš¿",
            "Jali na? Teri Jali na? ðŸ”¥",
            "Kyun thak raha hai bhai? Saksham bhaav nahi dega. ðŸ’â€â™‚ï¸",

            # --- â›” SHORT & DIRECT (Busy Mode) ---
            "Busy hu. Nikal. ðŸ‘‹",
            "Tata. Bye Bye. Khatam. Gaya. ðŸ‘‹",
            "Mood nahi hai, kal aana. (Ya mat hi aana). ðŸ“…",
            f"{msg.author.mention} âž¡ï¸ ðŸšª (Darwaza udhar hai).",
            "DND mode on. Disturb kiya toh uda dunga. âœˆï¸",
            "Kripya line mein lagein, dhakka mukki na karein. ðŸš¶â€â™‚ï¸ðŸš¶â€â™€ï¸",
            "Abey yaar... fir aa gaya tu? ðŸ¤¦â€â™‚ï¸"
        
            # --- ðŸ›‘ BUSY / DND (Direct) ---
            f"Oye {msg.author.mention}! ðŸ¤¨\nKya kaam hai? Kyu 'Saksham Saksham' laga rakha hai? Shanti rakh.",
            "Notification off hai mere maalik ke. ðŸ”•\nBaad mein aana, abhi mood nahi hai.",
            "Code kar raha hu, disturb mat kar. ðŸ’»\nAgar bug aaya toh tera naam laga dunga!",
            "Saksham so raha hai. ðŸ˜´\nDhakka-mukki mat kar, line mein lag.",
            "Abey yaar... fir aa gaya tu? ðŸ˜«\nJa na bhai, pakka mat.",
            "Busy. Do not disturb. â›”\n(Iska matlab 'Nikal' hota hai, pyaar se).",
            "Bhaag yahan se, chillar nahi hai. ðŸª™",

            # --- ðŸ¤– FUNNY / TROLL (Mazaak) ---
            "Error 404: Saksham Not Found. ðŸ¤–\nAur tu bhi gayab ho ja.",
            f"Abe {msg.author.mention}, saans to lene de bande ko! ðŸ˜¤",
            "Kya hai bhai? ðŸ˜‘\nPaisa maangna hai toh mana kar dena, Saksham garib hai.",
            "Hello Police? ðŸ“ž\nHaan, ye pagal aadmi mujhe pareshan kar raha hai.",
            "Aap jis vyakti se sampark karna chahte hain, wo abhi bhaav kha rahe hain. ðŸŽ",

            # --- ðŸ’€ EXTREME RUDE (Sambhal ke use karna) ---
            "Tere message se phone hang ho raha hai mera. ðŸ“±\nBand kar ye bawasir.",
            "Saksham nahi aayega. ðŸšª\nDarwaza band hai, kundi laga di hai.",
            "Tag karna band kar, warna bot se laat padegi. ðŸ¦µ",
            "Bhai 100 rupay Paytm kar de, fir baat karunga. ðŸ’¸",
            "Free ka net mil gaya toh kuch bhi likhega kya? ðŸŒ",
            "Muh dhoke aa pehle, fir baat kar. ðŸš¿"
        ]
        
        await msg.reply(random.choice(replies))
        return  # ðŸ›‘ YAHI RUK JAYEGA
                     
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
            await msg.channel.send(f"{msg.author.mention} âŒ Sirf **Roblox User ID** (Numbers) bhejo!", delete_after=5)
        except:
            pass
        return

    # 3. ROBLOX FETCH
    # (Ye 'await' zaroori hai, kyunki humne function async banaya tha)
    try:
        username, display = await roblox_info(user_id)
    except:
        await msg.reply("âŒ Roblox API Error. Thodi der baad try karein.")
        return

    if username in ["Unknown", "Invalid ID"]:
        await msg.reply("âŒ Ye Roblox ID invalid hai ya exist nahi karti.")
        return

    # 4. DATABASE LOGIC
    try:
        # A. BLACKLIST CHECK
        blk = supabase.table("blacklist_users").select("user_id").eq("user_id", user_id).execute().data
        if blk:
            await msg.reply(embed=discord.Embed(title="ðŸš« Denied", description="You are blacklisted.", color=0xe74c3c))
            return

        # B. ALREADY VERIFIED CHECK (Unique ID)
        exist = supabase.table("access_users").select("*").eq("user_id", user_id).execute().data
        if exist:
            # Yahan bhi details dikhayenge
            owner_id = exist[0].get('discord_id', 'Unknown')
            embed = discord.Embed(title="âœ… Already Verified", description=f"Ye ID pehle se verified hai (<@{owner_id}> ke paas).", color=0x2ecc71)
            embed.add_field(name="ðŸ†” Roblox ID", value=f"`{user_id}`", inline=True)
            embed.add_field(name="ðŸ‘¤ Username", value=f"**{username}**", inline=True)
            embed.add_field(name="âœ¨ Display", value=f"{display}", inline=True)
            await msg.reply(embed=embed)
            return

        # C. LIMIT & APPROVAL SYSTEM (Request Logic)
        # Check: Is Discord user ne pehle kitne verify kiye hain?
        existing_accs = supabase.table("access_users").select("*").eq("discord_id", str(msg.author.id)).execute().data
        
        if existing_accs:
            # Check permission
            approved = supabase.table("multi_access").select("discord_id").eq("discord_id", str(msg.author.id)).execute().data
            
            if not approved:
                await msg.reply(embed=discord.Embed(title="â³ Limit Reached", description="1 ID Limit over. Request sent to Admin.", color=0xffa500))
                
                # --- NEW: FETCH OLD ACCOUNTS LIST ---
                old_list = ""
                for acc in existing_accs:
                    old_list += f"â€¢ **{acc.get('username')}** (`{acc.get('user_id')}`)\n"
                
                if not old_list: old_list = "None"

                # Send Request to Admin
                ch = bot.get_channel(REVIEW_CHANNEL_ID)
                if ch:
                    req_embed = discord.Embed(title="âš ï¸ MULTI VERIFY REQUEST", color=0xffa500)
                    req_embed.set_author(name=f"{msg.author.name} ({msg.author.id})", icon_url=msg.author.display_avatar.url)
                    
                    # New ID Details
                    req_embed.add_field(name="ðŸ†• New Request", value=f"ðŸ†” `{user_id}`\nðŸ‘¤ **{username}**\nâœ¨ {display}", inline=False)
                    
                    # Old Accounts List (Jo maanga tha)
                    req_embed.add_field(name="ðŸ“‚ Already Verified Accounts", value=old_list, inline=False)
                    
                    req_embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")

                    # Buttons
                    async def approve(i):
                        if i.user.id != OWNER_ID: return
                        supabase.table("multi_access").upsert({"discord_id": str(msg.author.id), "approved": True}).execute()
                        await i.response.edit_message(embed=discord.Embed(title="ðŸŸ¢ Access Granted", description="User can now verify unlimited IDs.", color=0x2ecc71), view=None)

                    async def deny(i):
                        if i.user.id != OWNER_ID: return
                        await i.response.edit_message(embed=discord.Embed(title="ðŸ”´ Denied", color=0xe74c3c), view=None)

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
        embed = discord.Embed(title="âœ… Verified Successfully", color=0x2ecc71)
        embed.add_field(name="ðŸ†” Roblox ID", value=f"`{user_id}`", inline=True)
        embed.add_field(name="ðŸ‘¤ Username", value=f"**{username}**", inline=True)
        embed.add_field(name="âœ¨ Display", value=f"{display}", inline=True)
        embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
        embed.set_footer(text="Whitelist Access Granted")
        await msg.reply(embed=embed)

        # F. LOG CHANNEL (Admin ke liye)
        try:
            log_ch = bot.get_channel(1451973589342621791) # <-- Log Channel ID sahi rakhna
            if log_ch:
                log = discord.Embed(title="ðŸ“¥ New Verification", color=0x3498db)
                log.set_author(name=msg.author.name, icon_url=msg.author.display_avatar.url)
                log.add_field(name="Discord User", value=f"{msg.author.mention} (`{msg.author.id}`)", inline=False)
                # Saari details yahan bhi
                log.add_field(name="ðŸ†” Roblox ID", value=f"`{user_id}`", inline=True)
                log.add_field(name="ðŸ‘¤ Username", value=f"**{username}**", inline=True)
                log.add_field(name="âœ¨ Display", value=f"{display}", inline=True)
                log.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
                log.timestamp = datetime.utcnow()
                await log_ch.send(embed=log)
        except:
            pass
            
      # âŒ Purana galat indentation wala hatao
    # âœ… Ye sahi indentation wala lagao (Thoda peeche karke)

    except Exception as e:
        # Ye 'except' ab peeche khisak gaya hai (Sahi jagah par)
        await msg.reply(f"âŒ Critical Error: `{e}`")
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

        embed = discord.Embed(title=f"ðŸš« Banned Users List (Total: {len(self.data)})", color=0xff0000)
        
        for row in page_data:
            uid = row.get("user_id")
            reason = row.get("reason", "No Reason")
            executor_id = row.get("executor")
            
            # Fetch Info
            u, d = await roblox_info(uid)
            
            # Ban Type Logic
            if row.get("perm"):
                type_str = "ðŸ”´ **PERM**"
                time_str = "Never"
            else:
                try:
                    expire_ts = float(row.get("expire", 0))
                    type_str = "ðŸŸ  **TEMP**"
                    time_str = f"<t:{int(expire_ts)}:R>"
                except:
                    type_str = "Unknown"
                    time_str = "-"

            admin_tag = f"<@{executor_id}>" if executor_id else "Unknown"

            embed.add_field(
                name=f"ðŸ‘¤ {d} (@{u})",
                value=f"ðŸ†” `{uid}`\nâš–ï¸ Type: {type_str}\nâ³ Expires: {time_str}\nðŸ“ Reason: `{reason}`\nðŸ‘® By: {admin_tag}",
                inline=False
            )

        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} â€¢ Ban System")
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="â—€ï¸ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next â–¶ï¸", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)
        self.current_page += 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)


# ================== 2. CONFIRM VIEW CLASS (Clear All ke liye) ==================
class BanClearView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=30)
        self.author_id = author_id

    @discord.ui.button(label="âš ï¸ YES - DELETE ALL DATA", style=discord.ButtonStyle.danger)
    async def confirm(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author_id:
            return await i.response.send_message("âŒ You cannot use this button.", ephemeral=True)
        
        supabase.table("bans").delete().neq("user_id", "0").execute()
        
        embed = discord.Embed(title="â™»ï¸ BAN LIST CLEARED", description="âœ… All bans have been successfully removed from the database.", color=0x2ecc71)
        embed.set_footer(text=f"Cleared by {i.user.display_name}")
        
        await i.response.edit_message(embed=embed, view=None)
        self.stop()

    @discord.ui.button(label="âŒ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author_id:
            return await i.response.send_message("âŒ You cannot use this button.", ephemeral=True)

        embed = discord.Embed(title="ðŸ›¡ï¸ Operation Cancelled", description="Ban list was **NOT** cleared.", color=0x95a5a6)
        await i.response.edit_message(embed=embed, view=None)
        self.stop()


# ================== 3. MAIN ACTION COMMAND (ALL IN ONE) ==================
@bot.tree.command(name="action", description="ðŸ›¡ï¸ Ultimate Moderation System (Kick, Ban, Unban, List)")
@app_commands.choices(mode=[
    app_commands.Choice(name="ðŸ‘¢ Kick Player", value="kick"),
    app_commands.Choice(name="ðŸ”¨ Ban (Permanent)", value="ban"),
    app_commands.Choice(name="â± Temp Ban (Timed)", value="tempban"),
    app_commands.Choice(name="âœ… Unban", value="unban"),
    app_commands.Choice(name="ðŸ“œ List All Bans", value="list"),
    app_commands.Choice(name="ðŸ§¨ Clear All Bans (Reset)", value="clear"),
])
@app_commands.describe(
    user_id="Roblox ID (Required)",
    reason="Reason for action",
    duration="Minutes (Only for Tempban)"
)
async def action(i: discord.Interaction, mode: app_commands.Choice[str], user_id: str = None, reason: str = "No Reason Provided", duration: int = None):
    
    # OWNER CHECK
    if not owner(i):
        return await i.response.send_message("âŒ **Access Denied:** Owner/Admin only.", ephemeral=True)

    # Note: 'clear' ke liye defer nahi karenge
    if mode.value != "clear":
        await i.response.defer(ephemeral=False)

    try:
        # ================== 1. KICK (NEW ADDED) ==================
        if mode.value == "kick":
            if not user_id: return await i.followup.send("âŒ **Roblox ID Required!**")
            
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
            embed = discord.Embed(title="ðŸ‘¢ PLAYER KICKED", color=0xe74c3c) # Red color
            embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
            embed.add_field(name="ðŸ‘¤ User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="ðŸ“ Reason", value=f"`{reason}`", inline=True)
            embed.set_footer(text=f"Kicked by {i.user.display_name}", icon_url=i.user.display_avatar.url)
            
            await i.followup.send(embed=embed)


        # ================== 2. PERMANENT BAN ==================
        elif mode.value == "ban":
            if not user_id: return await i.followup.send("âŒ **Roblox ID Required!**")
            
            u, d = await roblox_info(user_id)
            
            supabase.table("bans").upsert({
                "user_id": user_id, "perm": True, "reason": reason, "expire": None, "executor": str(i.user.id)
            }).execute()

            try: log_action("ban", user_id, u, d, i.user.id)
            except: pass

            embed = discord.Embed(title="ðŸ”¨ USER BANNED", color=0xff0000)
            embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
            embed.add_field(name="ðŸ‘¤ User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="ðŸ“ Reason", value=f"`{reason}`", inline=True)
            embed.set_footer(text=f"Banned by {i.user.display_name}")
            await i.followup.send(embed=embed)


        # ================== 3. TEMP BAN ==================
        elif mode.value == "tempban":
            if not user_id: return await i.followup.send("âŒ **Roblox ID Required!**")
            if not duration: return await i.followup.send("âš ï¸ **Duration (minutes) Required!**")

            u, d = await roblox_info(user_id)
            expire_time = time.time() + (duration * 60)

            supabase.table("bans").upsert({
                "user_id": user_id, "perm": False, "reason": reason, "expire": expire_time, "executor": str(i.user.id)
            }).execute()

            try: log_action("tempban", user_id, u, d, i.user.id)
            except: pass

            embed = discord.Embed(title="â± USER TEMP-BANNED", color=0xe67e22)
            embed.add_field(name="ðŸ‘¤ User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="â³ Duration", value=f"{duration} Mins\nUnban: <t:{int(expire_time)}:R>", inline=True)
            embed.add_field(name="ðŸ“ Reason", value=f"`{reason}`", inline=False)
            embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
            await i.followup.send(embed=embed)


        # ================== 4. UNBAN ==================
        elif mode.value == "unban":
            if not user_id: return await i.followup.send("âŒ **Roblox ID Required!**")

            u, d = await roblox_info(user_id)
            supabase.table("bans").delete().eq("user_id", user_id).execute()

            try: log_action("unban", user_id, u, d, i.user.id)
            except: pass

            embed = discord.Embed(title="âœ… USER UNBANNED", color=0x2ecc71)
            embed.add_field(name="ðŸ‘¤ User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="ðŸ†” ID", value=f"`{user_id}`", inline=True)
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
                return await i.followup.send(embed=discord.Embed(title="ðŸ“œ Ban List", description="âœ… No active bans found.", color=0x2ecc71))

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
                title="âš ï¸ DANGER ZONE: CLEAR DATABASE",
                description="Are you sure you want to **DELETE ALL BANS**?\nThis cannot be undone.",
                color=0xffaa00
            )
            view = BanClearView(i.user.id)
            await i.response.send_message(embed=embed, view=view, ephemeral=False)

    except Exception as e:
        print(f"ACTION ERROR: {e}")
        try:
            await i.followup.send(f"âŒ **System Error:** `{e}`")
        except:
            await i.response.send_message(f"âŒ **System Error:** `{e}`", ephemeral=True)

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
        return await i.response.send_message("âŒ **Only Owner can manage VIPs.**", ephemeral=True)

    await i.response.defer(ephemeral=False)

    try:
        # ================== ALLOW (ADD VIP) ==================
        if mode.value == "allow":
            if not user:
                return await i.followup.send("âŒ **User select karna zaroori hai!**")

            # 1. Database Update
            supabase.table("attitude_bypass").upsert({"user_id": str(user.id)}).execute()
            
            # 2. ðŸ”¥ RAM UPDATE (Ye line zaroori hai!)
            await load_bypass_users()

            embed = discord.Embed(title="ðŸ‘‘ VIP Added", description=f"**{user.mention}** ab VIP list me hai.", color=0xf1c40f)
            embed.add_field(name="ðŸ˜Ž Effect", value="Bot ab isse tameez se baat karega.", inline=False)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Added by {i.user.display_name} â€¢ RAM Updated âœ…")
            
            await i.followup.send(embed=embed)

        # ================== BLOCK (REMOVE VIP) ==================
        if mode.value == "block":
            if not user:
                return await i.followup.send("âŒ **User select karna zaroori hai!**")

            # 1. Database Delete
            supabase.table("attitude_bypass").delete().eq("user_id", str(user.id)).execute()

            # 2. ðŸ”¥ RAM UPDATE (Ye line zaroori hai!)
            await load_bypass_users()

            embed = discord.Embed(title="ðŸ˜ˆ VIP Removed", description=f"**{user.mention}** ko VIP list se nikaal diya.", color=0x2c3e50)
            embed.add_field(name="ðŸ’€ Effect", value="Ab ye tag karega to full attitude sunega!", inline=False)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Removed by {i.user.display_name} â€¢ RAM Updated âœ…")

            await i.followup.send(embed=embed)

        # ================== LIST (SHOW ALL VIPs) ==================
        if mode.value == "list":
            # Fetch Data
            data = supabase.table("attitude_bypass").select("user_id").execute().data

            if not data:
                return await i.followup.send(embed=discord.Embed(title="ðŸ‘‘ VIP List", description="âŒ List is empty. Sabke liye attitude ON hai!", color=0x95a5a6))

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
        await i.followup.send(f"âŒ System Error: `{e}`")

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
        return await safe_send(i, emb("âŒ NO PERMISSION", "Only Owner can manage multi-access."))

    # ================= ADD USER =================
    if mode.value == "add":
        if not discord_id:
            return await safe_send(i, emb("âŒ ERROR", "Discord ID dena zaroori hai!"))

        # Save to Supabase
        try:
            supabase.table("multi_access").upsert({
                "discord_id": discord_id,
                "approved": True
            }).execute()

            await safe_send(i, emb(
                "âœ… ACCESS GRANTED",
                f"User <@{discord_id}> (`{discord_id}`)\n\nAb ye user **Unlimited Roblox IDs** verify kar sakta hai.",
                0x2ecc71
            ))
        except Exception as e:
            await safe_send(i, emb("âŒ DB ERROR", f"```{e}```"))

    # ================= REMOVE USER =================
    elif mode.value == "remove":
        if not discord_id:
            return await safe_send(i, emb("âŒ ERROR", "Discord ID dena zaroori hai!"))

        try:
            supabase.table("multi_access").delete().eq("discord_id", discord_id).execute()

            await safe_send(i, emb(
                "ðŸ—‘ ACCESS REVOKED",
                f"User <@{discord_id}> (`{discord_id}`)\n\nAb ye user **sirf 1 ID** verify kar payega.",
                0xff0000
            ))
        except Exception as e:
            await safe_send(i, emb("âŒ DB ERROR", f"```{e}```"))

    # ================= LIST USERS =================
    elif mode.value == "list":
        try:
            data = supabase.table("multi_access").select("*").execute().data

            if not data:
                return await safe_send(i, emb("ðŸ“‚ MULTI-ACCESS LIST", "No users found."))

            txt = ""
            for x in data:
                did = x['discord_id']
                txt += f"â€¢ <@{did}> (`{did}`)\n"

            await safe_send(i, emb("ðŸ“‚ MULTI-ACCESS ALLOWED USERS", txt, 0x3498db))
        
        except Exception as e:
            await safe_send(i, emb("âŒ DB ERROR", f"```{e}```"))

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
            desc += f"`{s_no:02d}.` **{dname}** (@{uname})\n   ðŸ†” `{uid}`\n\n"

        embed = discord.Embed(title=f"ðŸ“œ Whitelisted Users (Total: {len(self.data)})", description=desc, color=0x3498db)
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}", icon_url=self.author.display_avatar.url)
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="â—€ï¸ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        await i.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Next â–¶ï¸", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)
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

        embed = discord.Embed(title=f"ðŸš« Blacklisted Users (Total: {len(self.data)})", color=0x2c3e50) # Dark Color
        
        for index, row in enumerate(page_data):
            uid = row.get("user_id")
            # Fetch info live for premium feel
            u, d = await roblox_info(uid)
            
            embed.add_field(
                name=f"ðŸ‘¤ {d} (@{u})",
                value=f"ðŸ†” `{uid}`",
                inline=False
            )

        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} â€¢ Blacklist System")
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.total_pages - 1)

    @discord.ui.button(label="â—€ï¸ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next â–¶ï¸", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author.id: return await i.response.send_message("âŒ Not for you.", ephemeral=True)
        self.current_page += 1
        self.update_buttons()
        embed = await self.get_page_embed()
        await i.response.edit_message(embed=embed, view=self)


# ================== 2. CLEAR CONFIRMATION VIEW ==================
class AccessClearView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=30)
        self.author_id = author_id

    @discord.ui.button(label="âš ï¸ YES - DELETE WHITELIST", style=discord.ButtonStyle.danger)
    async def confirm(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author_id: return await i.response.send_message("âŒ You cannot use this button.", ephemeral=True)
        
        supabase.table("access_users").delete().neq("user_id", "0").execute()
        
        embed = discord.Embed(title="â™»ï¸ ACCESS LIST CLEARED", description="âœ… All whitelisted users have been removed.", color=0xff0000)
        embed.set_footer(text=f"Cleared by {i.user.display_name}")
        await i.response.edit_message(embed=embed, view=None)
        self.stop()

    @discord.ui.button(label="âŒ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.author_id: return await i.response.send_message("âŒ You cannot use this button.", ephemeral=True)

        embed = discord.Embed(title="ðŸ›¡ï¸ Operation Cancelled", description="Access list safe hai.", color=0x2ecc71)
        await i.response.edit_message(embed=embed, view=None)
        self.stop()


# ================== 3. ULTIMATE ACCESS COMMAND ==================
@bot.tree.command(name="access", description="âš™ï¸ Manage Access, Maintenance, Whitelist & Blacklist (Owner Only)")
@app_commands.choices(mode=[
    app_commands.Choice(name="ðŸŸ¢ Unlock Verification (Access ON)", value="on"),
    app_commands.Choice(name="ðŸ”´ Lock Verification (Access OFF)", value="off"),
    app_commands.Choice(name="ðŸ›¡ï¸ Enable Maintenance (Bot Down)", value="maint_on"),
    app_commands.Choice(name="ðŸš€ Disable Maintenance (Bot Live)", value="maint_off"),
    app_commands.Choice(name="ðŸ‘¤ Add to Whitelist", value="add"),
    app_commands.Choice(name="ðŸ—‘ï¸ Remove from Whitelist", value="remove"),
    app_commands.Choice(name="ðŸ“œ List Whitelist", value="list"),
    app_commands.Choice(name="ðŸš« Add to Blacklist", value="blk_add"),
    app_commands.Choice(name="âœ… Remove from Blacklist", value="blk_remove"),
    app_commands.Choice(name="â˜ ï¸ List Blacklist", value="blk_list"),
    app_commands.Choice(name="ðŸ§¨ Clear All Whitelist", value="clear"),
])
async def access(i: discord.Interaction, mode: app_commands.Choice[str], user_id: str = None):
    
    # 1. OWNER CHECK
    if not owner(i): 
        await i.response.send_message("âŒ **Access Denied:** Owner Only.", ephemeral=True)
        return

    # Clear mode ke liye defer nahi karenge (Button turant aana chahiye)
    if mode.value != "clear":
        await i.response.defer(ephemeral=False)

    try:
        # ================== 1. ACCESS ON/OFF ==================
        if mode.value in ["on", "off"]:
            supabase.table("bot_settings").update({"value": "true" if mode.value == "on" else "false"}).eq("key", "access_enabled").execute()
            
            status_emoji = "ðŸŸ¢" if mode.value == "on" else "ðŸ”´"
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
                embed = discord.Embed(title="ðŸ›¡ï¸ Maintenance Enabled", description="âš ï¸ **System is now in Maintenance Mode.**\nUsers cannot verify script.", color=0xe67e22)
            else:
                embed = discord.Embed(title="ðŸš€ Maintenance Disabled", description="âœ… **System is now LIVE.**\nUsers can verify script again.", color=0x2ecc71)
            
            embed.set_footer(text=f"Control by {i.user.display_name}", icon_url=i.user.display_avatar.url)
            
            try: log_action(f"maintenance_{is_maint}", "-", "-", "-", i.user.id)
            except: pass
            await i.followup.send(embed=embed)

        # ================== 3. WHITELIST ADD ==================
        elif mode.value == "add":
            if not user_id: return await i.followup.send("âŒ **Roblox ID required!**")
            u, d = await roblox_info(user_id)
            
            supabase.table("access_users").upsert({"user_id": user_id, "username": u, "display_name": d, "discord_id": str(i.user.id)}).execute()
            
            try: log_action("access_add", user_id, u, d, i.user.id)
            except: pass
            
            embed = discord.Embed(title="âœ… Access Granted", color=0x2ecc71)
            embed.add_field(name="ðŸ‘¤ User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="ðŸ†” ID", value=f"`{user_id}`", inline=True)
            embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
            await i.followup.send(embed=embed)

        # ================== 4. WHITELIST REMOVE ==================
        elif mode.value == "remove":
            if not user_id: return await i.followup.send("âŒ **Roblox ID required!**")
            u, d = await roblox_info(user_id)
            
            supabase.table("access_users").delete().eq("user_id", user_id).execute()
            
            try: log_action("access_remove", user_id, u, d, i.user.id)
            except: pass
            
            embed = discord.Embed(title="ðŸ—‘ï¸ Access Removed", color=0xff0000)
            embed.add_field(name="ðŸ‘¤ User", value=f"**{d}**\n(@{u})", inline=True)
            await i.followup.send(embed=embed)

        # ================== 5. WHITELIST LIST ==================
        elif mode.value == "list":
            data = supabase.table("access_users").select("*").execute().data
            if not data: return await i.followup.send(embed=discord.Embed(title="ðŸ“œ Access List", description="âŒ List is empty.", color=0xffa500))
            
            view = AccessPaginator(data, i.user)
            if view.total_pages <= 1: view.children[0].disabled = True; view.children[1].disabled = True
            else: view.update_buttons()
            await i.followup.send(embed=view.get_embed(), view=view)

        # ================== 6. BLACKLIST ADD ==================
        elif mode.value == "blk_add":
            if not user_id: return await i.followup.send("âŒ **Roblox ID required!**")
            u, d = await roblox_info(user_id)

            # Blacklist me daalo
            supabase.table("blacklist_users").upsert({"user_id": user_id}).execute()
            # Whitelist se hatao (Double Attack ðŸ˜ˆ)
            try: supabase.table("access_users").delete().eq("user_id", user_id).execute()
            except: pass

            try: log_action("blacklist_add", user_id, u, d, i.user.id)
            except: pass

            embed = discord.Embed(title="ðŸš« User Blacklisted", color=0x000000) # Full Black
            embed.add_field(name="ðŸ‘¤ Target", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="ðŸ†” ID", value=f"`{user_id}`", inline=True)
            embed.add_field(name="ðŸ’€ Status", value="Removed from Whitelist & Blocked.", inline=False)
            embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
            await i.followup.send(embed=embed)

        # ================== 7. BLACKLIST REMOVE ==================
        elif mode.value == "blk_remove":
            if not user_id: return await i.followup.send("âŒ **Roblox ID required!**")
            u, d = await roblox_info(user_id)

            supabase.table("blacklist_users").delete().eq("user_id", user_id).execute()

            try: log_action("blacklist_remove", user_id, u, d, i.user.id)
            except: pass

            embed = discord.Embed(title="âœ… Blacklist Removed", color=0x3498db)
            embed.add_field(name="ðŸ‘¤ User", value=f"**{d}**\n(@{u})", inline=True)
            embed.add_field(name="âœ¨ Status", value="User is no longer blocked.", inline=False)
            await i.followup.send(embed=embed)

        # ================== 8. BLACKLIST LIST ==================
        elif mode.value == "blk_list":
            data = supabase.table("blacklist_users").select("user_id").execute().data
            if not data: return await i.followup.send(embed=discord.Embed(title="â˜ ï¸ Blacklist", description="âœ… No users blacklisted.", color=0x2ecc71))

            view = BlacklistPaginator(data, i.user)
            if view.total_pages <= 1: view.children[0].disabled = True; view.children[1].disabled = True
            else: view.update_buttons()
            
            # Note: Blacklist me fetch async hai, so we call get_page_embed first
            embed = await view.get_page_embed()
            await i.followup.send(embed=embed, view=view)

        # ================== 9. CLEAR WHITELIST ==================
        elif mode.value == "clear":
            embed = discord.Embed(title="âš ï¸ DANGER ZONE", description="Are you sure you want to **RESET** the whitelist?", color=0xffaa00)
            view = AccessClearView(i.user.id)
            await i.response.send_message(embed=embed, view=view, ephemeral=False)

    except Exception as e:
        print(f"ERROR: {e}")
        try: await i.followup.send(f"âŒ **System Error:** `{e}`")
        except: await i.response.send_message(f"âŒ **System Error:** `{e}`", ephemeral=True)               

@bot.tree.command(
    name="verifiedlist",
    description="Show paginated verified Roblox users"
)
async def verifiedlist(i: discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("âŒ NO PERMISSION", "Owners only"))

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
            embed=emb("âš ï¸ ERROR", f"Failed to fetch logs\n`{e}`")
        )

    if not logs:
        return await i.followup.send(
            embed=emb("ðŸ“­ EMPTY", "No verified users found")
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
            f"ðŸ‘¤ <@{x['discord_id']}>\n"
            f"ðŸ†” Roblox ID: `{x['roblox_id']}`\n"
            f"ðŸ§‘ Username: **{x['username']}**\n"
            f"âœ¨ Display: {x['display_name']}\n"
            f"ðŸ•’ `{x['timestamp']}`\n"
            f"â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n"
        )

    if not entries:
        return await i.followup.send(
            embed=emb("ðŸ“› CLEAN", "No currently whitelisted verified users")
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
                f"ðŸ“œ VERIFIED USERS LIST ({self.page+1}/{len(PAGES)})",
                PAGES[self.page],
                0x3498db
            )
            await interaction.response.edit_message(embed=embed, view=self)

        @discord.ui.button(label="â¬… Back", style=discord.ButtonStyle.gray)
        async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.page > 0:
                self.page -= 1
            await self.update(interaction)

        @discord.ui.button(label="Next âž¡", style=discord.ButtonStyle.gray)
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
        f"ðŸ“œ VERIFIED USERS LIST (1/{len(PAGES)})",
        PAGES[0],
        0x3498db
    )

    await i.followup.send(embed=first, view=view)

# ================== ðŸ”¥ ROAST SYSTEM ==================

# 1. ðŸ—£ï¸ TRANSLATOR TOGGLE (Owner Only)
@bot.tree.command(name="translator", description="ðŸ”´/ðŸŸ¢ Turn Hindi Roast ON or OFF")
@app_commands.describe(mode="Choose Mode")
@app_commands.choices(mode=[
    app_commands.Choice(name="ðŸŸ¢ ON (Hindi Translation)", value="on"),
    app_commands.Choice(name="ðŸ”´ OFF (English Only - Fast)", value="off")
])
async def translator(i: discord.Interaction, mode: app_commands.Choice[str]):
    # ðŸ”’ OWNER CHECK
    if i.user.id != OWNER_ID: 
        return await i.response.send_message("âŒ Abe nikal! Ye setting sirf Maalik ke liye hai.", ephemeral=True)

    global TRANSLATOR_ON
    if mode.value == "on":
        TRANSLATOR_ON = True
        await i.response.send_message("âœ… **Translator ON!** Ab main Hindi me bezzati karunga. ðŸ‡®ðŸ‡³")
    else:
        TRANSLATOR_ON = False
        await i.response.send_message("âŽ **Translator OFF!** English Mode Activated (Super Fast). ðŸ‡ºðŸ‡¸")

# 2. ðŸ”¥ ROAST COMMAND (With VIP Check)
@bot.tree.command(name="roast", description="Bezzati karein (VIP Safe)")
async def roast(i: discord.Interaction, user: discord.Member):
    # Basic Checks
    if user.id == i.user.id: return await i.response.send_message("Khud ko kyu?", ephemeral=True)
    
    # ðŸ›¡ï¸ VIP CHECK
    if user.id in ATTITUDE_BYPASS_CACHE:
        return await i.response.send_message(f"âœ‹ **{user.display_name}** VIP List me hain. Inka mazaak allowed nahi hai!", ephemeral=True)
    
    if user.id == bot.user.id:
        return await i.response.send_message("Baap pe haath uthayega? ðŸ¤–ðŸ’¢", ephemeral=True)

    await i.response.defer()
    
    eng, hin = await get_evil_roast_data()
    final_text = hin if TRANSLATOR_ON else eng
    
    embed = discord.Embed(description=f"ðŸ”¥ **ROASTED!**\n\n{final_text}", color=0x2f3136)
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
        if user.guild_permissions.administrator: key_perms.append("ðŸ‘‘ ADMIN")
        if user.guild_permissions.ban_members: key_perms.append("ðŸ”¨ BAN")
        if user.guild_permissions.kick_members: key_perms.append("ðŸ‘¢ KICK")
        if user.guild_permissions.manage_guild: key_perms.append("âš™ï¸ MANAGER")
        perm_str = " | ".join(key_perms) if key_perms else "User"

        # --- Badges & Status ---
        is_bot = "ðŸ¤– YES" if user.bot else "ðŸ‘¤ NO"
        is_booster = f"ðŸš€ Yes (Since {user.premium_since.strftime('%b %Y')})" if user.premium_since else "âŒ No"
        nick = user.nick if user.nick else "None"

        # ================= 2. SUPABASE (DB) DEEP SCAN =================
        
        # A. Multi-Access (VIP) Check
        multi_data = supabase.table("multi_access").select("*").eq("discord_id", str(user.id)).execute().data
        access_level = "ðŸ”“ UNLIMITED (VIP)" if multi_data else "ðŸ”’ LIMITED (Standard)"

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
                
                status_icon = "ðŸŸ¢"
                note = ""

                if ban_chk:
                    status_icon = "ðŸ”´"
                    reason = ban_chk[0].get('reason', 'No reason')
                    alert_list += f"ðŸš¨ **BANNED:** `{u}` ({reason})\n"
                    risk_score += 50
                    note = "[BANNED]"

                if blk_chk:
                    status_icon = "âš«"
                    alert_list += f"ðŸš« **BLACKLIST:** `{u}`\n"
                    risk_score += 100
                    note = "[BLACKLISTED]"

                roblox_list += f"{status_icon} **{d}** (`@{u}`)\n   ðŸ†” `{rid}` {note}\n"

            # Trim list if too long
            if len(roblox_list) > 900:
                roblox_list = roblox_list[:900] + "\n... (More hidden)"
        else:
            roblox_list = "âŒ No verified accounts linked."
        
        # C. Calculate Final Risk Status
        if risk_score == 0: risk_status = "ðŸŸ¢ SAFE"
        elif risk_score < 40: risk_status = "ðŸŸ¡ MODERATE (Multi-Accounting)"
        elif risk_score < 80: risk_status = "ðŸŸ  HIGH RISK (Active Bans)"
        else: risk_status = "ðŸ”´ CRITICAL (Blacklisted)"

        # ================= 3. BUILD THE EMBED =================
        embed = discord.Embed(color=user.color)
        embed.set_author(name=f"{user.name} ({user.display_name})", icon_url=user.avatar.url if user.avatar else None)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        
        # Banner Image (Agar user ke paas hai)
        if user.banner:
            embed.set_image(url=user.banner.url)

        # --- SECTION 1: DISCORD PROFILE ---
        embed.add_field(name="ðŸ·ï¸ Identity", value=(
            f"**ID:** `{user.id}`\n"
            f"**Nickname:** `{nick}`\n"
            f"**Bot:** {is_bot}\n"
            f"**Booster:** {is_booster}"
        ), inline=True)

        embed.add_field(name="ðŸ“… History", value=(
            f"**Age:** `{age_str}`\n"
            f"**Joined:** `{join_str}`\n"
            f"**Join Rank:** `{join_rank}`"
        ), inline=True)

        embed.add_field(name=f"ðŸ›¡ï¸ Roles & Perms ({role_count})", value=(
            f"**Permissions:** {perm_str}\n"
            f"**Top Roles:** {top_roles}"
        ), inline=False)

        # --- SECTION 2: SYSTEM SECURITY ---
        embed.add_field(name="âš™ï¸ Verification Profile", value=(
            f"**Access Level:** {access_level}\n"
            f"**Linked Accounts:** `{total_accs}`\n"
            f"**Risk Analysis:** {risk_status}"
        ), inline=False)

        # --- SECTION 3: ROBLOX ACCOUNTS ---
        embed.add_field(name="ðŸŽ® Roblox Connections", value=roblox_list, inline=False)

        # --- SECTION 4: ALERTS (Only if dangerous) ---
        if alert_list:
            embed.add_field(name="âš ï¸ SECURITY ALERTS", value=alert_list, inline=False)

        # Footer
        embed.set_footer(text=f"Requested by {i.user.name} â€¢ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

        await i.followup.send(embed=embed)

    except Exception as e:
        await i.followup.send(embed=emb("âŒ ERROR", f"Failed to fetch profile: `{e}`"))
    
@bot.tree.command(name="verifycheck", description="Check which Roblox IDs a Discord user verified")
async def verifycheck(i: discord.Interaction, discord_id: str):

    if not owner(i):
        return await safe_send(i, emb("âŒ NO PERMISSION", "Owners only"))

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
        return await safe_send(i, emb("âš ï¸ ERROR", "Failed to fetch logs"))

    if not data:
        return await safe_send(
            i,
            emb("ðŸ“­ NO DATA", f"No verification found for `{discord_id}`")
        )

    txt = f"ðŸ‘¤ Discord User: <@{discord_id}>\n\n"
    seen = set()

    for x in data:
        rid = x["roblox_id"]
        if rid in seen:
            continue
        seen.add(rid)

        txt += (
            f"ðŸ†” Roblox ID: `{x['roblox_id']}`\n"
            f"ðŸ§‘ Username: **{x['username']}**\n"
            f"âœ¨ Display: {x['display_name']}\n"
            f"ðŸ•’ `{x['timestamp']}`\n"
            f"----------------------\n"
        )

    await safe_send(i, emb("ðŸ” USER VERIFICATION HISTORY", txt[:4000], 0x9b59b6))

@bot.tree.command(name="whois", description="ðŸ•µï¸ Get detailed status of a Roblox User")
async def whois(i: discord.Interaction, user_id: str):
    if not owner(i):
        return await safe_send(i, emb("âŒ NO PERMISSION", "Owner only command"))

    await i.response.defer()

    try:
        # âœ… FIX: Using await for async function
        username, display = await roblox_info(user_id)
        
        # Handle invalid user
        if username == "Invalid ID":
            return await i.followup.send(embed=discord.Embed(title="âŒ Invalid ID", description="Roblox ID exist nahi karti.", color=0xff0000))

        # ===== DATABASE CHECKS =====
        # 1. Ban Check
        ban_data = supabase.table("bans").select("*").eq("user_id", user_id).execute().data
        if ban_data:
            b = ban_data[0]
            if b.get("perm"):
                status_emoji = "ðŸ”´"
                status_text = f"**BANNED (Permanent)**\nReason: `{b.get('reason')}`"
                color = 0xff0000
            else:
                # Time calc
                left = int((float(b["expire"]) - time.time())/60)
                if left > 0:
                    status_emoji = "ðŸŸ "
                    status_text = f"**TEMP BANNED ({left}m left)**\nReason: `{b.get('reason')}`"
                    color = 0xffa500
                else:
                    status_emoji = "ðŸŸ¢"
                    status_text = "Clean (Ban Expired)"
                    color = 0x2ecc71
        else:
            status_emoji = "ðŸŸ¢"
            status_text = "Clean (No Active Bans)"
            color = 0x2ecc71

        # 2. Access Check
        ac = supabase.table("access_users").select("user_id").eq("user_id",user_id).execute().data
        access_str = "âœ… **Whitelisted**" if ac else "âŒ **Not Whitelisted**"

        # 3. Blacklist Check
        blk = supabase.table("blacklist_users").select("user_id").eq("user_id", user_id).execute().data
        blacklist_str = "ðŸš« **Yes (Restricted)**" if blk else "ðŸŸ¢ **No**"

        # ===== BUILD PREMIUM EMBED =====
        embed = discord.Embed(title=f"{status_emoji} User Lookup Result", color=color)
        
        # Header (User Info)
        embed.add_field(name="ðŸ‘¤ Identity", value=f"**User:** `{username}`\n**Display:** `{display}`\n**ID:** `{user_id}`", inline=False)
        
        # Status Grid
        embed.add_field(name="ðŸ›¡ï¸ Moderation", value=status_text, inline=True)
        embed.add_field(name="ðŸ” Access", value=access_str, inline=True)
        embed.add_field(name="â›” Blacklist", value=blacklist_str, inline=True)

        # Thumbnail (Roblox Headshot)
        embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
        
        # Footer
        embed.set_footer(text=f"Requested by {i.user.name}", icon_url=i.user.display_avatar.url)
        embed.timestamp = datetime.utcnow()

        await i.followup.send(embed=embed)

    except Exception as e:
        print(f"WHOIS ERROR: {e}")
        await i.followup.send(f"âŒ **System Error:** `{e}`")

        
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
        return await safe_send(i, emb("âŒ NO PERMISSION","Owner only"))

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

        access_status = "ðŸŸ¢ OFF (Everyone Allowed)"
        maintenance_status = "ðŸŸ¢ OFF"

        for s in settings:
            if s["key"] == "access_enabled" and s["value"] == "true":
                access_status = "ðŸ” ON (Whitelist Enabled)"
            if s["key"] == "maintenance" and s["value"] == "true":
                maintenance_status = "ðŸ›  ON"

        uptime = int(time.time() - START_TIME)
        hrs = uptime // 3600
        mins = (uptime % 3600) // 60

        embed = discord.Embed(
            title="âš™ï¸ SYSTEM CONTROL PANEL",
            description="Premium Secure Control Dashboard",
            color=0x2ecc71
        )

        embed.add_field(
            name="ðŸš« Ban System",
            value=(
                f"**Permanent Bans:** `{perm}`\n"
                f"**Active TempBans:** `{temp}`\n"
                f"**Blacklisted Users:** `{len(blacklist)}`"
            ),
            inline=False
        )

        embed.add_field(
            name="ðŸ‘¥ User Access",
            value=(
                f"**Whitelisted Users:** `{len(access)}`\n"
                f"**Verification Logs:** `{len(logs)}`\n"
                f"**Unique Verifiers:** `{len(set(x['discord_id'] for x in logs))}`\n"
                f"**Kick Flags Pending:** `{len(kicks)}`"
            ),
            inline=False
        )

        embed.add_field(
            name="ðŸ›  System Status",
            value=(
                f"**Access System:** {access_status}\n"
                f"**Maintenance:** {maintenance_status}"
            ),
            inline=False
        )

        embed.add_field(
            name="ðŸ¤– Bot Status",
            value=(
                f"**Uptime:** `{hrs}h {mins}m`\n"
                f"**Health:** ðŸŸ¢ Stable & Optimized"
            ),
            inline=False
        )

        embed.set_footer(text="RoboPal â€¢ Secure Moderation Engine")
        embed.timestamp = datetime.utcnow()

        await i.followup.send(embed=embed)

    except Exception as e:
        await i.followup.send(
            embed=emb("âŒ ERROR", f"Stats failed:\n```{e}```", 0xff0000)
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
        return await safe_send(i, emb("âŒ NO PERMISSION","Owner only"))

    await i.response.defer()

    # =========================
    # INVALID (Both Empty)
    # =========================
    if not discord_user and not roblox_user_id:
        return await safe_send(
            i,
            emb("âŒ ALT CHECK FAILED", 
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
                emb("ðŸ‘¤ ALT CHECK",
                    f"{discord_user.mention} ne abhi tak **kuch bhi verify nahi kiya**",
                    0xffff00
                )
            )

        unique = {}
        for x in logs:
            unique[x["roblox_id"]] = x

        count = len(unique)

        txt = "\n".join(
            f"â€¢ `{v['roblox_id']}` | **{v['username']}** ({v['display_name']})"
            for v in unique.values()
        )

        status = "ðŸŸ¢ Clean â€” No ALT Found"
        color = 0x2ecc71

        if count >= 2:
            status = f"ðŸ”´ ALT Detected â€” `{count}` Accounts Linked"
            color = 0xff0000

        desc = (
            f"**Discord:** {discord_user.mention}\n"
            f"**Linked Accounts:** `{count}`\n"
            f"**Status:** {status}\n\n"
            f"{txt}"
        )

        return await safe_send(i, emb("ðŸ•µ ALT ACCOUNT CHECK", desc, color))

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
                emb("ðŸ‘¤ ALT CHECK",
                    f"Roblox ID `{roblox_user_id}` ne abhi verify nahi kiya",
                    0xffff00
                )
            )

        user = logs[0]
        discord_ids = list({x["discord_id"] for x in logs})

        status = "ðŸŸ¢ Clean â€” No Suspicious Activity"
        color = 0x2ecc71

        if len(discord_ids) >= 2:
            status = f"ðŸ”´ Suspicious â€” `{len(discord_ids)}` Discord Accounts linked"
            color = 0xff0000

        desc = (
            f"**Roblox ID:** `{roblox_user_id}`\n"
            f"**Username:** `{user['username']}`\n"
            f"**Display Name:** `{user['display_name']}`\n\n"
            f"**Linked Discord Accounts:** `{len(discord_ids)}`\n"
            f"**Status:** {status}"
        )

        return await safe_send(i, emb("ðŸ•µ ALT ACCOUNT CHECK", desc, color))

@bot.tree.command(name="crush", description="Add/Remove user from Flirty/Horny list")
@app_commands.choices(mode=[
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="remove", value="remove"),
    app_commands.Choice(name="list", value="list"),
])
async def crush(i: discord.Interaction, mode: app_commands.Choice[str], user: discord.User = None):
    
    if not owner(i): # Sirf Owner chala sakta hai
        return await i.response.send_message("âŒ **Apni limit me raho! Sirf Owner ye kar sakta hai.**", ephemeral=True)

    await i.response.defer(ephemeral=False)

    try:
        # â¤ï¸ ADD (Flirt ON)
        if mode.value == "add":
            if not user: return await i.followup.send("âŒ User select karo!")
            
            supabase.table("bot_crushes").upsert({"user_id": str(user.id)}).execute()
            await load_crush_users() # RAM Update
            
            embed = discord.Embed(title="ðŸ˜ Crush Added", description=f"**{user.mention}** ab is bot ka Crush hai!", color=0xe91e63)
            embed.add_field(name="Effect", value="Ab bot isse Flirt karega. ðŸ˜˜", inline=False)
            await i.followup.send(embed=embed)

        # ðŸ’” REMOVE (Flirt OFF)
        if mode.value == "remove":
            if not user: return await i.followup.send("âŒ User select karo!")
            
            supabase.table("bot_crushes").delete().eq("user_id", str(user.id)).execute()
            await load_crush_users() # RAM Update
            
            embed = discord.Embed(title="ðŸ’” Crush Removed", description=f"**{user.mention}** se dil bhar gaya.", color=0x95a5a6)
            embed.add_field(name="Effect", value="Wapas se purana Roast mode ON. ðŸ¤¬", inline=False)
            await i.followup.send(embed=embed)

        # ðŸ“œ LIST
        if mode.value == "list":
            if not CRUSH_CACHE:
                return await i.followup.send("âŒ Koi Crush nahi hai. Bot single hai!")
            
            names = [f"<@{uid}>" for uid in CRUSH_CACHE]
            await i.followup.send(embed=discord.Embed(title="ðŸ˜ Bot's Crush List", description="\n".join(names), color=0xe91e63))

    except Exception as e:
        await i.followup.send(f"âŒ Error: {e}")

@bot.tree.command(name="verifyhistory", description="Show global verification logs")
async def verifyhistory(i: discord.Interaction):
    if not owner(i):
        return await safe_send(i, emb("âŒ NO PERMISSION","Owner Only"))

    await i.response.defer()

    logs = supabase.table("verify_logs").select("*").order("timestamp", desc=True).execute().data
    
    if not logs:
        return await i.followup.send(embed=emb("ðŸ“­ EMPTY","No one has verified yet"))

    pages = []
    page = []

    for x in logs:
        t = x.get("timestamp","").replace("T"," ").split(".")[0]
        page.append(
            f"ðŸ“Œ **{x['username']}** ({x['display_name']})\n"
            f"ðŸ†” `{x['roblox_id']}` â€” <@{x['discord_id']}> â€” `{t}`\n"
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
                f"ðŸ“œ VERIFICATION HISTORY ({self.index+1}/{len(pages)})",
                pages[self.index],
                0x3498db
            )
            await interaction.response.edit_message(embed=embed, view=self)

        @ui.button(label="â¬…ï¸ Back", style=discord.ButtonStyle.secondary)
        async def back(self, interaction, btn):
            if self.index > 0:
                self.index -= 1
            await self.update(interaction)

        @ui.button(label="âž¡ï¸ Next", style=discord.ButtonStyle.primary)
        async def next(self, interaction, btn):
            if self.index < len(pages)-1:
                self.index += 1
            await self.update(interaction)

    view = Pager()
    await i.followup.send(
        embed=emb(f"ðŸ“œ VERIFICATION HISTORY (1/{len(pages)})", pages[0], 0x3498db),
        view=view
    )

# ================== HISTORY COMMAND (OPTIMIZED) ==================
@bot.tree.command(name="history", description="ðŸ“œ Check Roblox User History & Safety Status")
async def history(i: discord.Interaction, user_id: str):
    
    # 1. OWNER/ADMIN CHECK (Database se)
    if not owner(i):
        await i.response.send_message("âŒ **Access Denied:** You are not an Admin.", ephemeral=True)
        return

    # 2. Defer Response (Load kam karne ke liye)
    await i.response.defer(ephemeral=False)

    try:
        # A. Roblox Info Fetch (Optimized)
        username, display = await roblox_info(user_id)
        
        if username == "Invalid ID":
             return await i.followup.send(embed=discord.Embed(title="âŒ Error", description="Invalid Roblox ID", color=0xff0000))

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

            access_status = f"âœ… **Whitelisted**\nLinked to: <@{disc_id}>\nðŸ†” `{disc_id}`"
            color = 0x2ecc71 # Green
        else:
            access_status = "âš ï¸ **Not Linked**\n(No active whitelist found)"
            color = 0x3498db # Blue (Neutral)

        # 2. Ban Status
        if ban_data:
            b = ban_data[0]
            if b.get("perm"):
                ban_status = f"ðŸ”´ **PERMANENT BAN**\nReason: `{b.get('reason')}`"
                color = 0xff0000 # Red
            else:
                # Time Calculation
                try:
                    left = int(max((float(b["expire"]) - time.time())/60 , 0))
                    ban_status = f"ðŸŸ  **TEMP BAN** ({left}m left)\nReason: `{b.get('reason')}`"
                    color = 0xe67e22 # Orange
                except:
                    ban_status = "ðŸŸ¢ **Ban Expired**"
        else:
            ban_status = "ðŸŸ¢ **Clean** (No active bans)"

        # 3. Blacklist Status
        if blk_data:
            blk_status = "ðŸš« **YES (Blacklisted)**"
            color = 0x2c3e50 # Dark (Danger)
        else:
            blk_status = "ðŸŸ¢ **NO**"

        # ================= PREMIUM EMBED =================
        embed = discord.Embed(title=f"ðŸ“œ User History: {display}", color=color)
        
        # Top Section: User Identity
        embed.add_field(name="ðŸ‘¤ Identity", value=f"**User:** @{username}\n**ID:** `{user_id}`", inline=False)
        
        # Mid Section: Status Grid
        embed.add_field(name="ðŸ” Whitelist Status", value=access_status, inline=True)
        embed.add_field(name="ðŸ›¡ï¸ Ban Status", value=ban_status, inline=True)
        embed.add_field(name="â›” Blacklist", value=blk_status, inline=True)

        # Avatar Thumbnail
        embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
        
        # Footer
        embed.set_footer(text=f"Requested by {i.user.display_name} â€¢ Secure Lookup", icon_url=i.user.display_avatar.url)
        embed.timestamp = datetime.utcnow()

        await i.followup.send(embed=embed)

    except Exception as e:
        print(f"HISTORY ERROR: {e}")
        await i.followup.send(f"âŒ **System Error:** `{e}`")
        
# ================== PROFILE COMMAND (ALL TABLES INTEGRATED) ==================
@bot.tree.command(name="profile", description="ðŸ“‚ View full Verification, Safety & Moderation Profile")
async def profile(i: discord.Interaction, user_id: str):
    
    # 1. OWNER CHECK (Database Logic)
    if not owner(i):
        return await i.response.send_message("âŒ **Access Denied:** Owner/Admin only.", ephemeral=True)

    await i.response.defer(ephemeral=False)

    try:
        # A. Roblox Info (Async & Fast)
        username, display = await roblox_info(user_id)

        if username == "Invalid ID":
             return await i.followup.send(embed=discord.Embed(title="âŒ Error", description="Invalid Roblox ID", color=0xff0000))

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

            verify_status = "âœ… **Whitelisted**"
            verify_desc = (
                f"ðŸ‘¤ **Verified By:** <@{verifier_id}>\n"
                f"ðŸ“… **Date:** `{date_str}`\n"
                f"ðŸ†” **Verifier ID:** `{verifier_id}`"
            )
            color = 0x2ecc71 # Green
        else:
            verify_status = "âš ï¸ **Not Whitelisted**"
            verify_desc = "User verify nahi hai aur na hi whitelist access hai."
            color = 0x3498db # Blue (Neutral)

        # --- 2. Moderation Logic ---
        mod_status = []
        
        # Check Bans
        if bans:
            b = bans[0]
            if b.get('perm'):
                mod_status.append(f"ðŸ”´ **Permanent Ban:** `{b.get('reason')}`")
                color = 0xff0000 # Red
            else:
                mod_status.append(f"ðŸŸ  **Temp Ban:** `{b.get('reason')}`")
                color = 0xe67e22 # Orange

        # Check Blacklist
        if blk:
            mod_status.append("ðŸš« **Blacklisted User**")
            color = 0x2c3e50 # Dark

        # Check Flags
        if flags:
            mod_status.append(f"ðŸš© **Flags:** {len(flags)} Active Flags")
        
        # Check Kicks
        if kicks:
            mod_status.append(f"ðŸ‘¢ **Kick History:** {len(kicks)} times kicked")

        # Check Warnings
        if warnings:
            mod_status.append(f"âš ï¸ **Warnings:** {len(warnings)} Warnings")

        # Combine Moderation Text
        if mod_status:
            mod_text = "\n".join(mod_status)
        else:
            mod_text = "ðŸŸ¢ **Clean Record** (No bans, flags, or warnings)"


        # ================= D. BUILD PREMIUM EMBED =================
        embed = discord.Embed(title=f"ðŸ“‚ Player Profile: {display}", color=color)
        
        # Header: User Identity
        embed.add_field(name="ðŸ‘¤ Identity", value=f"**User:** @{username}\n**ID:** `{user_id}`", inline=False)
        
        # Section 1: Verification (Access Users)
        embed.add_field(name="ðŸ” Access Status", value=verify_status, inline=True)
        embed.add_field(name="ðŸ›¡ï¸ Safety Status", value="See Below ðŸ‘‡", inline=True)
        
        # Section 2: Verification Details (Verifier Info)
        embed.add_field(name="ðŸ“œ Verification Details", value=verify_desc, inline=False)
        
        # Section 3: Full Moderation History (All Tables)
        embed.add_field(name="ðŸš¨ Moderation History", value=mod_text, inline=False)

        # Thumbnail (Avatar)
        embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
        
        # Footer
        embed.set_footer(text=f"Requested by {i.user.display_name} â€¢ Full Database Scan", icon_url=i.user.display_avatar.url)
        embed.timestamp = datetime.utcnow()

        await i.followup.send(embed=embed)

    except Exception as e:
        print(f"PROFILE ERROR: {e}")
        await i.followup.send(f"âŒ **System Error:** `{e}`")
            

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
            return await i.followup.send(embed=emb("âŒ NO PERMISSION","Owner only"), ephemeral=True)
        except:
            return

    # ---- SAFE SUPABASE FETCH ----
    try:
        logs = supabase.table("access_users").select("*").execute().data
    except Exception as e:
        return await i.followup.send(embed=emb("âŒ Database Error", str(e)), ephemeral=True)

    if not logs:
        return await i.followup.send(embed=emb("â„¹ï¸ INFO","No verified users found"))

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
                f"ðŸ‘¤ **{name}** â€” `{did}`\n"
                f"ðŸ‘‰ **Different Accounts Verified:** `{len(data['roblox_ids'])}`\n"
            )

            for rid, info in data["entries"].items():
                uname, dname = info
                block += f"ðŸ†” `{rid}` | {uname} ({dname})\n"

            block += "â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n"
            result_blocks.append(block)

    if not result_blocks:
        return await i.followup.send(embed=emb("âœ… CLEAN","No one verified multiple different accounts."))

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
                f"ðŸ”Ž MULTI ACCOUNT VERIFIERS ({self.page+1}/{len(PAGES)})",
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

        @discord.ui.button(label="â¬… Back", style=discord.ButtonStyle.gray)
        async def back(self, interaction: discord.Interaction, btn: discord.ui.Button):
            if self.page > 0:
                self.page -= 1
            await self.refresh(interaction)

        @discord.ui.button(label="Next âž¡", style=discord.ButtonStyle.gray)
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
        f"ðŸ”Ž MULTI ACCOUNT VERIFIERS (1/{len(PAGES)})",
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
        return await i.response.send_message(embed=emb("âŒ NO PERMISSION", "Owner only"), ephemeral=False)

    await i.response.defer()

    try:
        # ================= ADD FAKE BAN =================
        if action.lower() == "add":
            if not userid:
                return await i.followup.send(embed=emb("âŒ ERROR","User ID required"))

            # Already exists check
            chk = supabase.table("fake_warnings").select("user_id").eq("user_id", userid).execute().data
            if chk:
                return await i.followup.send(embed=emb("âš ï¸ ALREADY PENDING","This player already has a fake warning pending"))

            # ðŸ‘‡ YAHAN FIX KIYA HAI (Await + Correct Unpacking)
            uname, dname = await roblox_info(userid)

            supabase.table("fake_warnings").insert({
                "user_id": userid,
                "username": uname,
                "display_name": dname,
                "message": message or "ðŸš« Account Action Required\n\nYour account has been temporarily restricted...\nDuration: 3 Days\nReference: #SEC-9043X"
            }).execute()

            return await i.followup.send(embed=emb(
                "ðŸš¨ FAKE BAN ADDED",
                f"ðŸ‘¤ **{dname}** (`{uname}`)\nðŸ†” `{userid}`\n\nFake ban queued successfully",
                0xff0000
            ))

        # ================= REMOVE =================
        elif action.lower() == "remove":
            supabase.table("fake_warnings").delete().eq("user_id", userid).execute()

            return await i.followup.send(embed=emb(
                "ðŸ§¹ REMOVED",
                f"User `{userid}` removed from fake queue",
                0x2ecc71
            ))

        # ================= LIST =================
        elif action.lower() == "list":
            data = supabase.table("fake_warnings").select("*").execute().data

            if not data:
                return await i.followup.send(embed=emb("ðŸ“­ EMPTY","No pending fake bans"))

            text = ""
            for x in data:
                text += f"ðŸ‘¤ **{x['display_name']}** (`{x['username']}`)\nðŸ†” `{x['user_id']}`\n-------------------\n"

            return await i.followup.send(embed=emb("ðŸ“œ PENDING FAKE BANS", text[:4000], 0x3498db))

        else:
            return await i.followup.send(embed=emb("âŒ Invalid Action","Use `add / remove / list`"))

    except Exception as e:
        return await i.followup.send(embed=emb("âŒ ERROR", f"```{e}```"))

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
        return await safe_send(i, emb("âŒ NO PERMISSION", "Owner Only"))

    await i.response.defer()

    try:
        # Query Logic Updated for Partial Matching (like 'maintenance%')
        if filter.value == "all":
            data = supabase.table("admin_logs").select("*").order("timestamp", desc=True).limit(100).execute().data
        else:
            # .ilike use kar rahe hain taaki 'maintenance' filter 'maintenance_on' aur 'maintenance_off' dono pakad le
            data = supabase.table("admin_logs").select("*").ilike("action", f"{filter.value}%").order("timestamp", desc=True).limit(100).execute().data
            
    except Exception as e:
        return await i.followup.send(embed=emb("âŒ ERROR", f"Logs failed:\n`{e}`", 0xff0000))

    if not data:
        return await i.followup.send(embed=emb("ðŸ“­ NO DATA", f"No logs found for filter: **{filter.name}**", 0xffc107))

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
            f"ðŸ“Œ **Action:** `{act}`\n"
            f"ðŸ‘® **Admin:** {executor_mention}\n"
            f"ðŸ†” **Target:** `{x.get('user_id', '-')}`\n"
            f"ðŸ“… `{t}`\n"
            f"â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n"
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
                f"ðŸ—‚ LOGS â€” {filter.name.upper()} ({self.page+1}/{len(pages)})",
                pages[self.page],
                0x3498db
            )
            await interaction.response.edit_message(embed=e, view=self)

        @discord.ui.button(label="â® Back", style=discord.ButtonStyle.gray)
        async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.page > 0:
                self.page -= 1
            await self.update(interaction)

        @discord.ui.button(label="Next â­", style=discord.ButtonStyle.gray)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.page < len(pages) - 1:
                self.page += 1
            await self.update(interaction)

    view = LogPages()
    e = emb(
        f"ðŸ—‚ LOGS â€” {filter.name.upper()} (1/{len(pages)})",
        pages[0],
        0x3498db
    )

    await i.followup.send(embed=e, view=view)


    # âŒ yaha bhi ephemeral hata diya
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
        return await safe_send(i, emb("âŒ NO PERMISSION", "Owners only"))

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
            f"ðŸŒ **Backend Status**\n"
            f"{'ðŸŸ¢ Online' if backend_online else 'ðŸ”´ Offline'}\n"
            f"âš¡ Response: `{latency}ms`\n"
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
            f"ðŸ—„ **Database**\n"
            f"{'ðŸŸ¢ Connected' if db_ok else 'ðŸ”´ Failure'}\n"
            f"â± Query: `{q_ms}ms`"
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
            f"âš™ï¸ **System Settings**\n"
            f"ðŸ” Access: `{access}`\n"
            f"ðŸ›  Maintenance: `{maintenance}`"
        )

        # ===============================
        # BOT UPTIME
        # ===============================
        up = int(time.time() - START_TIME)
        hrs = up // 3600
        mins = (up % 3600)//60
        reports.append(f"ðŸ¤– **Bot Uptime**\n`{hrs}h {mins}m`")

        # ===============================
        #  TRAFFIC MONITOR
        # ===============================
        now = time.time()
        last_min = [t for t, _ in TRAFFIC_LOG if now - t <= 60]
        rpm = len(last_min)

        reports.append(
            f"ðŸ“¡ **Traffic Monitor**\n"
            f"Requests per minute: `{rpm}`"
        )

        # ===============================
        #  CPU-LIKE LOAD (REALISTIC ESTIMATE)
        # ===============================
        # Render pe CPU access nahi hota
        # so we simulate real system load smart way
        load_score = max(5, min(99, rpm * 3 + (latency // 50)))
        reports.append(
            f"ðŸ–¥ **Load Estimate**\n"
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
            risk = "ðŸ”´ Critical â€” Core system unstable"
        elif fails >= 6 or db_fail_rate >= 40:
            risk = "ðŸ”´ High Failure Activity Detected"
        elif fails >= 3 or db_fail_rate >= 20:
            risk = "ðŸŸ  Warning â€” Minor Instability"
        else:
            risk = "ðŸŸ¢ Stable & Secure"

        reports.append(
            f"ðŸš¨ **Security & Risk Monitor**\n"
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
                "ðŸ§  ULTRA SYSTEM AUDIT â€” V3 PRO",
                desc,
                0x2ecc71 if ok else 0xff0000
            )
        )

    except Exception as e:
        await i.followup.send(
            embed=emb(
                "âŒ AUDIT FAILED",
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
        return await safe_send(i, emb("âŒ DENIED", "Sirf MAIN OWNER hi owners ko manage kar sakta hai."))

    # ================= ADD OWNER =================
    if action.value == "add":
        if not user_id:
            return await safe_send(i, emb("âŒ ERROR", "User ID daalna zaroori hai!"))

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
                "ðŸ‘‘ OWNER ADDED", 
                f"**User:** {name}\n**ID:** `{user_id}`\n\nAb ye banda bot commands access kar sakta hai.", 
                0x00ff00
            ))
        except Exception as e:
            return await safe_send(i, emb("âŒ DB ERROR", f"```{e}```"))

    # ================= REMOVE OWNER =================
    if action.value == "remove":
        if not user_id:
            return await safe_send(i, emb("âŒ ERROR", "User ID daalna zaroori hai!"))

        try:
            supabase.table("bot_admins").delete().eq("user_id", user_id).execute()
            return await safe_send(i, emb("ðŸ—‘ OWNER REMOVED", f"User ID `{user_id}` ko owner list se hata diya gaya.", 0xff0000))
        except Exception as e:
            return await safe_send(i, emb("âŒ DB ERROR", f"```{e}```"))

    # ================= LIST OWNERS =================
    if action.value == "list":
        await i.response.defer() # List fetch karne me time lag sakta hai

        try:
            data = supabase.table("bot_admins").select("*").execute().data
            
            # Main Owner Info
            try:
                main_user = await bot.fetch_user(OWNER_ID)
                main_txt = f"ðŸ‘‘ **MAIN OWNER:** {main_user.mention} (`{main_user.name}`)"
            except:
                main_txt = f"ðŸ‘‘ **MAIN OWNER:** <@{OWNER_ID}>"

            txt = f"{main_txt}\n\n**ðŸ›¡ï¸ EXTRA OWNERS:**\n"

            if not data:
                txt += "None"
            else:
                for x in data:
                    uid = x['user_id']
                    try:
                        # Discord se naam fetch karo
                        u = await bot.fetch_user(int(uid))
                        txt += f"â€¢ {u.mention} â€” **{u.name}**\n   ðŸ†” `{uid}`\n"
                    except:
                        # Agar user Discord chhod chuka hai
                        txt += f"â€¢ <@{uid}> (User Not Found)\n   ðŸ†” `{uid}`\n"

            await i.followup.send(embed=emb("ðŸ‘‘ BOT OWNER LIST", txt, 0xf1c40f))

        except Exception as e:
            await i.followup.send(embed=emb("âŒ ERROR", f"List fetch nahi ho payi: `{e}`"))


@bot.tree.command(name="stop", description="Enable / Disable global script execution")
@app_commands.choices(mode=[
    app_commands.Choice(name="Enable Stop (Block Scripts)", value="on"),
    app_commands.Choice(name="Disable Stop (Allow Scripts)", value="off"),
    app_commands.Choice(name="Status", value="status"),
])
async def stop(i: discord.Interaction, mode: app_commands.Choice[str]):

    if not owner(i):
        return await safe_send(i, emb("âŒ NO PERMISSION","Owner Only"))

    if mode.value == "status":
        r = supabase.table("bot_settings").select("*").eq("key","stop_enabled").execute().data
        state = "ON ðŸ”´ (Blocked)" if r and r[0]["value"]=="true" else "OFF ðŸŸ¢ (Allowed)"
        return await safe_send(i, emb("â¹ STOP SYSTEM STATUS", f"Current Status: **{state}**", 0x3498db))

    val = "true" if mode.value=="on" else "false"

    supabase.table("bot_settings").upsert({
        "key": "stop_enabled",
        "value": val
    }).execute()
    
    # ðŸ”¥ LOG SAVE KARO
    try:
        log_action(f"stop_{mode.value}", "-", "-", "-", i.user.id)
    except:
        pass

    msg = "ðŸ›‘ Stop Mode ENABLED\nNew executions will be blocked" if val=="true" else "ðŸŸ¢ Stop Mode DISABLED\nScripts will execute normally"

    await safe_send(i, emb("â¹ STOP SYSTEM UPDATED", msg, 0xf1c40f))

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
                accounts_list = "\n".join([f"â€¢ `{x['user_id']}` ({x.get('username','Unknown')})" for x in data])

                embed = discord.Embed(
                    title="ðŸ‘‹ User Left - Access Revoked",
                    description=f"**User:** {member.mention} (`{member.id}`)\nserver chhod gaya, isliye access hata diya gaya.",
                    color=0xff0000
                )
                embed.add_field(name=f"ðŸ—‘ Removed Accounts ({count})", value=accounts_list, inline=False)
                embed.timestamp = datetime.utcnow()
                
                await channel.send(embed=embed)

    except Exception as e:
        print(f"LEAVE EVENT ERROR: {e}")

# ================== SAY COMMAND (WITH IMAGE & LOGS) ==================

# ðŸ‘‡ Apki di hui Log Channel ID set kar di hai
SAY_LOG_CHANNEL_ID = 1450514760276774967

@bot.tree.command(name="say", description="ðŸ“¢ Make the bot speak (With Image Support & Logs)")
@app_commands.describe(
    message="Message content",
    channel="Where to send? (Default: current channel)",
    mode="Style of message (Text/Embed)",
    image="Attach an image (Optional)"
)
@app_commands.choices(mode=[
    app_commands.Choice(name="ðŸ“ Plain Text", value="text"),
    app_commands.Choice(name="âœ… Green Embed (Success)", value="green"),
    app_commands.Choice(name="âŒ Red Embed (Error)", value="red"),
    app_commands.Choice(name="â„¹ï¸ Blue Embed (Info)", value="blue"),
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
        return await i.response.send_message("âŒ **Access Denied:** Aapko `/say` use karne ki permission nahi hai.", ephemeral=True)

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
            if mode_value == "green": color, title = 0x2ecc71, "âœ… Success"
            elif mode_value == "red": color, title = 0xff0000, "âŒ Error"
            elif mode_value == "blue": color, title = 0x3498db, "â„¹ï¸ Info"
            else: color, title = 0x2f3136, "ðŸ“¢ Notice"

            # Embed banao
            embed = discord.Embed(title=title, description=message, color=color)
            
            # Embed ke saath image (Attachment) bhejo
            # Note: Embed ke andar image dikhane ke liye hum 'set_image' use kar sakte hain
            # lekin attachment bhejna zyada safe/reliable hota hai.
            if image:
                embed.set_image(url=f"attachment://{image.filename}")
                
            sent_msg = await target_channel.send(embed=embed, file=file_attachment)

        # 3. CONFIRMATION
        await i.followup.send(f"âœ… **Sent!** Message delivered to {target_channel.mention}")

        # ================== 4. LOGGING TO YOUR CHANNEL ==================
        try:
            log_channel = bot.get_channel(SAY_LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(title="ðŸ“¢ Say Command Used", color=0xffa500) # Orange Log
                
                log_embed.add_field(name="ðŸ‘¤ Executor", value=f"{i.user.mention}\n(`{i.user.id}`)", inline=True)
                log_embed.add_field(name="ðŸ“ Channel", value=f"{target_channel.mention}\n(`{target_channel.id}`)", inline=True)
                log_embed.add_field(name="ðŸŽ¨ Mode", value=f"`{mode_value.upper()}`", inline=True)
                log_embed.add_field(name="ðŸ“ Content", value=f"```{message}```", inline=False)
                
                # Log me photo dikhana
                if image:
                    log_embed.set_thumbnail(url=image.url)
                    log_embed.add_field(name="ðŸ–¼ï¸ Image Attached", value=f"[Click to View]({image.url})", inline=False)

                log_embed.set_footer(text=f"Time: {datetime.utcnow().strftime('%H:%M:%S UTC')}")
                
                await log_channel.send(embed=log_embed)
            
        except Exception as e:
            print(f"Logging Error: {e}")

    except discord.Forbidden:
        await i.followup.send(f"âŒ **Permission Error:** Bot ko {target_channel.mention} me message bhejne ki permission nahi hai.")
    except Exception as e:
        await i.followup.send(f"âŒ **System Error:** `{e}`")

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
        return await i.response.send_message("âŒ **Access Denied:** Owner/Admin only.", ephemeral=True)

    await i.response.defer(ephemeral=False)

    try:
                # ================== ADD USER ==================
        if action.value == "add":
            if not user:
                return await i.followup.send("âŒ **User select karna zaroori hai!**")
            
            # Upsert to DB
            supabase.table("say_access").upsert({
                "user_id": str(user.id),
                "added_by": str(i.user.id)
            }).execute()
            
            # ðŸ‘‡ YAHAN GALTI THI (Ab sahi hai)
            embed = discord.Embed(title="âœ… Access Granted", description=f"**{user.mention}** ab `/say` command use kar sakta hai.", color=0x2ecc71)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(name="ðŸ‘¤ User Info", value=f"**Name:** {user.display_name}\n**ID:** `{user.id}`", inline=False)
            embed.set_footer(text=f"Added by {i.user.display_name}", icon_url=i.user.display_avatar.url)
            
            await i.followup.send(embed=embed)

        # ================== REMOVE USER ==================
        elif action.value == "remove":
            if not user:
                return await i.followup.send("âŒ **User select karna zaroori hai!**")
            
            # Delete from DB
            supabase.table("say_access").delete().eq("user_id", str(user.id)).execute()
            
            embed = discord.Embed(title="ðŸ—‘ï¸ Access Revoked", description=f"**{user.mention}** se `/say` command ki permission le li gayi hai.", color=0xe74c3c)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(name="ðŸ‘¤ User Info", value=f"**Name:** {user.display_name}\n**ID:** `{user.id}`", inline=False)
            embed.set_footer(text=f"Removed by {i.user.display_name}", icon_url=i.user.display_avatar.url)

            await i.followup.send(embed=embed)

        # ================== LIST USERS ==================
        elif action.value == "list":
            data = supabase.table("say_access").select("user_id").execute().data

            if not data:
                return await i.followup.send(embed=discord.Embed(title="ðŸ—£ï¸ Say Access List", description="âŒ List is Empty.", color=0xffa500))

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
        await i.followup.send(f"âŒ **System Error:** `{e}`")

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
        await i.response.send_message("âŒ **Only Owner/Admins can use this.**", ephemeral=True)
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
                
                embed = discord.Embed(title="ðŸ‘‘ Exception Added", description=f"âœ… **{user.mention}** ab restrictions bypass kar sakta hai.", color=0x2ecc71)
                embed.set_thumbnail(url=user.display_avatar.url)
                embed.set_footer(text=f"Allowed by {i.user.display_name}")
                await i.followup.send(embed=embed)
                return

            elif action.value == "remove":
                # Remove from DB
                supabase.table("restrict_bypass").delete().eq("user_id", str(user.id)).execute()
                # Update Cache
                BYPASS_USERS_CACHE.discard(user.id)

                embed = discord.Embed(title="ðŸš« Exception Removed", description=f"âš ï¸ **{user.mention}** ab restrictions bypass nahi kar sakta.", color=0xe74c3c)
                embed.set_thumbnail(url=user.display_avatar.url)
                embed.set_footer(text=f"Blocked by {i.user.display_name}")
                await i.followup.send(embed=embed)
                return
                
            elif action.value == "list":
                # Fetch fresh list from DB for pagination
                data = supabase.table("restrict_bypass").select("user_id").execute().data
                
                if not data:
                    await i.followup.send(embed=discord.Embed(title="ðŸ“‚ List Empty", description="Koi user allowed nahi hai.", color=0xffa500))
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
                    embed = discord.Embed(title="ðŸ›¡ï¸ Words Banned", description=f"**Successfully Added:**\n{msg}", color=0xe74c3c)
                    embed.set_footer(text=f"Total: {len(added)} words added")
                    await i.followup.send(embed=embed)
                else:
                    await i.followup.send("âš ï¸ Ye words pehle se list mein hain.")
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
                    embed = discord.Embed(title="ðŸ—‘ï¸ Words Unbanned", description=f"**Successfully Removed:**\n{msg}", color=0x2ecc71)
                    await i.followup.send(embed=embed)
                else:
                    await i.followup.send("âš ï¸ Ye words list mein nahi mile.")
                return
            
        # ================= 3. LIST ALL WORDS =================
        if action.value == "list":
            # Cache ko list me convert karke sort karo
            all_words = sorted(list(BANNED_WORDS_CACHE))

            if not all_words:
                await i.followup.send(embed=discord.Embed(title="ðŸ“‚ Banned Words", description="List is currently empty.", color=0x3498db))
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
        await i.followup.send("âŒ **Usage Error:** Ya toh `word` likho ya `user` select karo!", ephemeral=True)

    except Exception as e:
        print(f"RESTRICT ERROR: {e}")
        await i.followup.send(f"âŒ System Error: `{e}`")
                
# ================== FUN: FAKE HACK COMMAND ==================
@bot.tree.command(name="hack", description="Prank hack a user (Funny)")
async def hack(i: discord.Interaction, target: discord.User):
    # 1. Start Operation
    await i.response.send_message(f"ðŸ’» **Initiating Hack on {target.mention}...**")
    msg = await i.original_response()
    
    # 2. Fake Steps (Loop)
    import asyncio
    import random
    
    # Funny "Leaked" Passwords & History
    passwords = ["ilovepappu", "password123", "saksham_is_pro", "mummy_ka_ladla", "00000000"]
    history = ["how to impress girls", "baal kaise ugaye", "free fire diamond hack", "funny cat videos", "saksham se dosti kaise kare"]
    
    steps = [
        f"ðŸ” Fetching IP Address of {target.name}...",
        "ðŸ”“ Bypassing Firewall...",
        "ðŸ’‰ Injecting Trojan Virus...",
        f"ðŸ“‚ Accessing Files... Found 'Homework' folder (Empty) ðŸ“",
        f"ðŸ”‘ Decrypting Password... Success: ||**{random.choice(passwords)}**||",
        f"ðŸ‘€ Reading Google Search History: '`{random.choice(history)}`'...",
        "ðŸ“¡ Uploading Photos to Dark Web...",
        "ðŸ’¸ Stealing Paytm Balance... â‚¹12 found.",
        "âœ… **HACK COMPLETE! System Destroyed.** ðŸ’€"
    ]

    # Har step ko 1.5 second baad dikhayenge (Edit karke)
    for step in steps:
        await asyncio.sleep(1.5) # Wait time
        await msg.edit(content=f"```diff\n- {step}\n```")

    # Final Message
    await asyncio.sleep(1)
    await msg.edit(content=f"ðŸ”¥ **{target.mention} has been HACKED!** â˜ ï¸\n(Just kidding, masti thi ðŸ˜‚)")

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
        comment = "ðŸ’” **Bhai-Behen ka rishta lagta hai.** (No chance)"
        color = 0xff0000 # Red
    elif score < 50:
        comment = "ðŸ˜ **Kaam chalaau dosti.** (Bas Hi-Hello)"
        color = 0xffa500 # Orange
    elif score < 80:
        comment = "â¤ï¸ **Arey waah! Mast Jodi hai.** (Party kab?)"
        color = 0xffff00 # Yellow
    else:
        comment = "ðŸ’ **Rab ne bana di jodi!** (Shaadi ka card bhejna)"
        color = 0x2ecc71 # Green

    # Progress Bar (Visual)
    # E.g: [â–ˆâ–ˆâ–ˆâ–ˆ......]
    bar_length = 10
    filled = int(score / 10)
    bar = "â–ˆ" * filled + "â–‘" * (bar_length - filled)

    embed = discord.Embed(title="ðŸ’– Love/Dosti Calculator ðŸ’–", color=color)
    embed.add_field(name=f"ðŸ”» Match: {user1.name} x {user2.name}", value=f"**{score}%**\n`[{bar}]`\n\n{comment}")
    
    await i.response.send_message(embed=embed)

# ================== ROBLOX INFO COMMAND (FINAL MEGA VERSION ðŸ‘‘) ==================
@bot.tree.command(name="robloxinfo", description="ðŸ” Get MAXIMUM details (Socials, DevStats, Inv, Favs, History)")
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
                        return await i.followup.send(embed=emb("âŒ Not Found", f"User `{identifier}` nahi mila."))
            except:
                return await i.followup.send(embed=emb("âŒ API Error", "Roblox API down hai. ID use karein."))

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
            f"https://users.roblox.com/v1/users/{target_id}/promotion-channels",                    # 11. Socials ðŸ”—
            f"https://games.roblox.com/v2/users/{target_id}/games?accessFilter=Public&limit=50",    # 12. Dev Stats ðŸ› ï¸
            f"https://inventory.roblox.com/v1/users/{target_id}/can-view-inventory",                # 13. Inventory ðŸŽ’
            f"https://games.roblox.com/v2/users/{target_id}/favorite/games?limit=1"                 # 14. Favorites â­
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

        # ðŸ›¡ï¸ HELPER: Safe List Extractor (Crash Fix)
        def get_d(res):
            if res and isinstance(res, dict) and "data" in res: return res["data"]
            return []

        user_data = results[0]
        if not user_data or "id" not in user_data: 
            return await i.followup.send(embed=emb("ðŸš« TERMINATED", "User Banned/Not Found.", 0xff0000))

        # ================= 3. PARSING (ALL DETAILS) =================
        
        # A. Identity (Verified & Premium)
        display_name = user_data.get('displayName', 'Unknown')
        username = user_data.get('name', 'Unknown')
        
        is_verified = user_data.get("hasVerifiedBadge", False)
        is_premium = results[9].get("membershipValid", False) if results[9] else False

        name_str = f"{display_name} (@{username})"
        if is_verified: name_str += " â˜‘ï¸"
        if is_premium: name_str += " ðŸ’Ž"

        # B. Official Badges (Admin/Staff)
        badges_list = get_d(results[10])
        official_badges = []
        for badge in badges_list:
            b_name = badge.get("name")
            if b_name == "Administrator": official_badges.append("ðŸ›¡ï¸ Admin")
            elif b_name == "Creator": official_badges.append("ðŸ”¨ Creator")
            elif "Intern" in b_name: official_badges.append("ðŸŽ“ Intern")
            elif "Star" in b_name: official_badges.append("â­ Star")
            else: official_badges.append(f"ðŸŽ–ï¸ {b_name}")
        
        badges_str = " | ".join(official_badges) if official_badges else "None"

        # C. Status & Last Seen (Game Link Included)
        status_str = "âš« Offline"
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

            if p_type == 1: status_str = "ðŸŸ¢ **Online** (Web)"
            elif p_type == 2:
                gname = p_data.get("lastLocation", "Game")
                pid = p_data.get("placeId")
                # Game Link Logic ðŸŽ®
                status_str = f"ðŸŽ® Playing **[{gname}](https://www.roblox.com/games/{pid})**" if pid else f"ðŸŽ® Playing **{gname}**"
            elif p_type == 3: status_str = "ðŸ”¶ **In Studio**"
            else: status_str = f"âš« **Offline**\nLast seen: {last_seen_str}"

        # D. Socials & Groups
        friends = results[1]['count'] if results[1] else 0
        followers = results[2]['count'] if results[2] else 0
        following = results[3]['count'] if results[3] else 0
        groups_list = get_d(results[8])
        group_count = len(groups_list)

        # ================= 4. EXTRA FEATURES (JO AAPNE MAANGI THI) =================

        # 1. Social Links ðŸ”—
        socials = []
        if results[11] and isinstance(results[11], dict):
            for key, val in results[11].items():
                if val and "http" in str(val): socials.append(f"[{key.capitalize()}]({val})")
        social_str = " | ".join(socials) if socials else "None"

        # 2. Dev Stats ðŸ› ï¸
        games_list = get_d(results[12])
        total_visits = sum(g.get("placeVisits", 0) for g in games_list)
        dev_stat_str = f"ðŸŽ® **Games:** `{len(games_list)}` | ðŸ‘£ **Visits:** `{total_visits:,}`"

        # 3. Inventory ðŸŽ’
        inv_open = results[13].get("canView", False) if results[13] else False
        inv_str = "ðŸ”“ **Open**" if inv_open else "ðŸ”’ **Private**"

        # 4. Group Owner ðŸŽ–ï¸
        owned_groups = []
        for g in groups_list:
            if g.get("role", {}).get("rank") == 255:
                owned_groups.append(g.get("group", {}).get("name", "Unknown"))
        owner_str = ", ".join(owned_groups[:3]) if owned_groups else "None"

        # 5. Favorites â­
        fav_list = get_d(results[14])
        fav_game = "None"
        if fav_list:
            fg = fav_list[0]
            fav_game = f"[{fg.get('name','Game')}](https://www.roblox.com/games/{fg.get('id')})"

        # ================= 5. DB CHECK (Internal) =================
        tid = str(target_id)
        local_access = await db_call(lambda: supabase.table("access_users").select("*").eq("user_id", tid).execute())
        local_ban = await db_call(lambda: supabase.table("bans").select("*").eq("user_id", tid).execute())
        
        db_txt = "ðŸ”’ Not Verified"
        col = 0x2f3136
        if local_access.data: 
            db_txt = f"âœ… **Verified** (<@{local_access.data[0]['discord_id']}>)"
            col = 0x2ecc71
        if local_ban.data:
            db_txt = f"ðŸ”´ **BANNED** (`{local_ban.data[0]['reason']}`)"
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
        embed.add_field(name="ðŸ†” Identity", value=f"**ID:** `{target_id}`\n**Bio:** {bio}", inline=False)

        # Row 2: Status & Age
        try:
            created_ts = int(datetime.strptime(user_data["created"].split(".")[0], "%Y-%m-%dT%H:%M:%S").timestamp())
            age_str = f"<t:{created_ts}:D>\n(<t:{created_ts}:R>)"
        except: age_str = "Unknown"

        embed.add_field(name="ðŸ“¡ Live Status", value=status_str, inline=True)
        embed.add_field(name="ðŸ“… Account Age", value=age_str, inline=True)

        # Row 3: Official Data
        off_data = f"**Premium:** {'Yes ðŸ’Ž' if is_premium else 'No'}\n**Verified:** {'Yes â˜‘ï¸' if is_verified else 'No'}\n**Badges:** {badges_str}"
        embed.add_field(name="ðŸ† Official Status", value=off_data, inline=False)

        # Row 4: THE EXTRAS (Aapki request)
        extra_info = (
            f"ðŸŽ’ **Inventory:** {inv_str}\n"
            f"â­ **Last Fav:** {fav_game}\n"
            f"ðŸŽ–ï¸ **Owns Groups:** {owner_str}"
        )
        embed.add_field(name="ðŸ“‚ Profile Extras", value=extra_info, inline=True)
        
        # Row 5: Dev Stats
        embed.add_field(name="ðŸ› ï¸ Dev Stats", value=dev_stat_str, inline=False)
        
        # Row 6: Social Links
        embed.add_field(name="ðŸ”— Social Media", value=social_str, inline=False)
        
        # Row 7: Stats
        stats_txt = f"ðŸ‘¥ Fr: `{friends}` | ðŸ“¡ Fl: `{followers}` | ðŸ‘€ Fw: `{following}` | ðŸ‘• Grp: `{group_count}`"
        embed.add_field(name="ðŸ“Š Roblox Stats", value=stats_txt, inline=False)
        
        # Row 8: Bot Data
        embed.add_field(name="ðŸ¤– RoboPal Data", value=db_txt, inline=False)

        # History
        hist_list = get_d(results[7])
        past = ", ".join([f"`{x['name']}`" for x in hist_list]) if hist_list else "None"
        if len(past) > 600: past = past[:600] + "..."
        if past != "None": embed.add_field(name="ðŸ•°ï¸ Aliases", value=past, inline=False)

        embed.set_footer(text=f"Requested by {i.user.display_name}", icon_url=i.user.display_avatar.url)
        await i.followup.send(embed=embed)

    except Exception as e:
        print(f"INFO ERROR: {e}")
        try: await i.followup.send(embed=emb("âŒ API Error", f"Details fetch failed.\nError: `{e}`"))
        except: pass
             
# ================== FUN: DESI THAPPAD (SLAP) ==================
@bot.tree.command(name="slap", description="Slap someone nicely (Desi Style)")
async def slap(i: discord.Interaction, target: discord.User):
    # Khud ko nahi maar sakte
    if target.id == i.user.id:
        await i.response.send_message("Bhai khud ko kyu maar raha hai? Depression? ðŸ˜¢", ephemeral=True)
        return

    import random
    # Funny Weapons List
    weapons = [
        "ðŸ©´ **Bheegi Hui Chappal** (Geeli pappi)",
        "ðŸ¥– **Mummy ka Belan** (Headshot)",
        "ðŸ§± **Sadak ki Eeet** (Critical Damage)",
        "âŒ¨ï¸ **Mechanical Keyboard** (RGB Wala)",
        "ðŸŸ **Gandi Machli** (Smelly)",
        "ðŸ³ **Garam Tawa** (Burn damage)",
        "ðŸšœ **JCB ka Panja** (Khatam Tata Bye Bye)"
    ]
    
    weapon = random.choice(weapons)
    
    # Embed
    embed = discord.Embed(
        description=f"ðŸ‘‹ **{i.user.mention}** ne **{target.mention}** ko mara!",
        color=0xff5555
    )
    embed.add_field(name="ðŸ”« Weapon Used:", value=weapon)
    embed.set_footer(text="Ouch! That hurts. ðŸ¤•")
    
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

            # SUPABASE FAIL â†’ SAFE MODE (Don't kick)
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

        # FAIL SAFE MODE â†’ NEVER KICK VERIFIED
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

            # 1ï¸âƒ£ Try Access Users
            acc = supabase.table("access_users").select("*").eq("user_id", uid).execute().data
            if acc:
                username = acc[0].get("username") or username
                display = acc[0].get("display_name") or display

            # 2ï¸âƒ£ Otherwise Try Verify Logs
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
                "ðŸš« Account Action Required\n\n"
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

# ðŸ‘‡ ISKO SABSE NEECHE ADD KARO ðŸ‘‡

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"âš ï¸ Command Error: {error}")

@bot.tree.error
async def on_app_command_error(i: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandInvokeError) and "10062" in str(error):
        # ðŸ¤« Unknown Interaction error ko ignore karo
        return
    
    # Baaki errors ke liye message bhej do
    if not i.response.is_done():
        await i.response.send_message(f"âŒ Error: {error}", ephemeral=True)
    else:
        await i.followup.send(f"âŒ Error: {error}", ephemeral=True)

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

# ðŸ‘‡ ISKO UPDATE KARO (Purana hata kar ye lagao)
async def roblox_info(uid):
    url = f"https://users.roblox.com/v1/users/{uid}"
    try:
        # ðŸ‘‡ DHYAN DEIN: Yahan hum 'bot.session' use kar rahe hain
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
