import os
import random
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import db
import time  # <--- Ye add karo
from business_config import BUSINESSES  # <--- Ye bhi add karo (File honi chahiye)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "cyberpunk_secret")

# Discord Config
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
API_ENDPOINT = 'https://discord.com/api/v10'

# --- AUTHENTICATION ---
@app.route('/')
def home():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return redirect(f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify")

@app.route('/callback')
def callback():
    code = request.args.get('code')
    data = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'grant_type': 'authorization_code', 'code': code, 'redirect_uri': REDIRECT_URI}
    r = requests.post(f'{API_ENDPOINT}/oauth2/token', data=data, headers={'Content-Type': 'application_x-www-form-urlencoded'})
    token = r.json().get('access_token')
    user = requests.get(f'{API_ENDPOINT}/users/@me', headers={'Authorization': f'Bearer {token}'}).json()
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['avatar'] = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png"
    return redirect(url_for('dashboard'))

# --- DASHBOARD & ROUTES ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('home'))
    return render_template('dashboard.html', 
                         username=session['username'], 
                         avatar=session['avatar'], 
                         balance=db.get_user_balance(session['user_id']))

@app.route('/shop')
def shop():
    if 'user_id' not in session: return redirect(url_for('home'))
    # Aapka purana index.html load karega
    return render_template('index.html', username=session['username']) 

@app.route('/games')
def gamelist():
    if 'user_id' not in session: return redirect(url_for('home'))
    return render_template('gamelist.html', balance=db.get_user_balance(session['user_id']))

@app.route('/games/casino')
def casino():
    if 'user_id' not in session: return redirect(url_for('home'))
    return render_template('casino.html', 
                         username=session['username'], 
                         balance=db.get_user_balance(session['user_id']))

# --- API: SLOTS LOGIC ---
@app.route('/api/spin', methods=['POST'])
def spin():
    user_id = session.get('user_id')
    if not user_id: return jsonify({"error": "Login required"})
    
    cost = 50000
    if db.get_user_balance(user_id) < cost:
        return jsonify({"status": "error", "msg": "Insufficient Funds!"})
    
    db.update_balance(user_id, -cost)
    
    # Logic: Diamond(1%), Gold(3%), Devil(2%), Apple(12%), Mango(12%), Loss(70%)
    items = ["💎", "🏆", "😈", "🍎", "🥭", "💩"]
    weights = [1, 3, 2, 12, 12, 70]
    result = random.choices(items, weights=weights, k=1)[0]
    
    win = 0
    is_jackpot = False
    slots = [result, result, result]
    msg = ""

    if result == "💩":
        slots = random.sample(["🍎", "🥭", "🍇", "🍋"], 3)
        msg = "You Lost!"
    elif result == "💎":
        win = 10000000; is_jackpot = True; msg = "JACKPOT! 10 MILLION!"
    elif result == "🏆":
        win = 500000; msg = "BIG WIN! 500k!"
    elif result == "😈":
        msg = "DEVIL ROLE UNLOCKED!" # Role API call here if needed
    elif result == "🍎" or result == "🥭":
        win = 100000; msg = f"Win! +100k"

    if win > 0: db.update_balance(user_id, win)
    
    return jsonify({
        "status": "success", "slots": slots, 
        "balance": db.get_user_balance(user_id), 
        "win": win, "jackpot": is_jackpot, "msg": msg
    })

# --- API: SATTA (MULTIPLIER) LOGIC ---
@app.route('/api/satta', methods=['POST'])
def satta():
    user_id = session.get('user_id')
    data = request.json
    bet_amount = int(data.get('amount'))
    multiplier = int(data.get('multiplier')) # 2, 3, 5, 10
    
    if db.get_user_balance(user_id) < bet_amount:
        return jsonify({"status": "error", "msg": "Garib! Balance nahi hai."})
    
    # Paisa kaat lo pehle
    db.update_balance(user_id, -bet_amount)
    
    # Your requested chances:
    # 2x = 10%, 3x = 7%, 5x = 5%, 10x = 1%
    chance_map = {2: 10, 3: 7, 5: 5, 10: 1}
    win_chance = chance_map.get(multiplier, 0)
    
    roll = random.randint(1, 100)
    won = roll <= win_chance
    
    win_amount = 0
    if won:
        win_amount = bet_amount * multiplier
        db.update_balance(user_id, win_amount)
        msg = f"WON! +{win_amount}"
    else:
        msg = f"LOST -{bet_amount}"
        
    return jsonify({
        "status": "success", "won": won, 
        "balance": db.get_user_balance(user_id), 
        "msg": msg
    })

# app.py me upar import add karein
import time
from business_config import BUSINESSES

# --- BUSINESS ROUTES ---

@app.route('/business')
def business_dashboard():
    if 'user_info' not in session: return redirect('/')
    
    user_id = session['user_info']['id']
    
    # DB se Data lo
    data = db.supabase.table("economy").select("balance, businesses").eq("user_id", user_id).execute().data
    if not data: return "Error loading data"
    
    balance = data[0]['balance']
    owned_businesses = data[0]['businesses'] or {}

    # --- PASSIVE INCOME CALCULATION (On Load) ---
    current_time = int(time.time())
    total_generated = 0
    
    for biz_id, biz_data in owned_businesses.items():
        last_check = biz_data.get('last_check', current_time)
        hours_passed = (current_time - last_check) / 3600
        
        if hours_passed > 0:
            # Stats update logic
            rate = BUSINESSES[biz_id]['income_per_hr']
            supplies = biz_data.get('supplies', 0)
            popularity = biz_data.get('popularity', 100)
            
            # Agar supplies hain tabhi production hoga
            if supplies > 0:
                production_efficiency = (popularity / 100)
                produced_stock = int(rate * hours_passed * production_efficiency)
                
                # Update Stock (Max cap check)
                max_st = BUSINESSES[biz_id]['max_stock']
                new_stock = min(biz_data.get('stock', 0) + produced_stock, max_st)
                
                # Supplies Kam karo
                supplies_used = int(hours_passed * 10) # 10 supplies per hour
                new_supplies = max(0, supplies - supplies_used)
                
                # Popularity thodi girao
                new_popularity = max(0, int(popularity - (hours_passed * 2)))
                
                # Save changes locally
                owned_businesses[biz_id]['stock'] = new_stock
                owned_businesses[biz_id]['supplies'] = new_supplies
                owned_businesses[biz_id]['popularity'] = new_popularity
                owned_businesses[biz_id]['last_check'] = current_time

    # DB Update karo naye stats ke saath
    db.supabase.table("economy").update({"businesses": owned_businesses}).eq("user_id", user_id).execute()

    return render_template('business.html', 
                         user=session['user_info'], 
                         balance=balance, 
                         owned=owned_businesses, 
                         all_biz=BUSINESSES)

# --- API: BUY BUSINESS ---
@app.route('/api/business/buy', methods=['POST'])
def buy_business():
    user_id = session['user_info']['id']
    biz_id = request.json.get('biz_id')
    
    data = db.supabase.table("economy").select("balance, businesses").eq("user_id", user_id).execute().data
    balance = data[0]['balance']
    owned = data[0]['businesses'] or {}
    
    if biz_id in owned:
        return jsonify({"status": "error", "msg": "You already own this!"})
    
    cost = BUSINESSES[biz_id]['price']
    if balance < cost:
        return jsonify({"status": "error", "msg": "Too expensive!"})
    
    # Buy Logic
    owned[biz_id] = {
        "stock": 0, "supplies": 100, "popularity": 100, 
        "level": 1, "last_check": int(time.time())
    }
    
    db.supabase.table("economy").update({
        "balance": balance - cost,
        "businesses": owned
    }).eq("user_id", user_id).execute()
    
    return jsonify({"status": "success", "msg": f"Purchased {BUSINESSES[biz_id]['name']}!"})

# --- API: RESUPPLY / PROMOTE / SELL ---
@app.route('/api/business/action', methods=['POST'])
def biz_action():
    user_id = session['user_info']['id']
    req = request.json
    action = req.get('action') # 'resupply', 'promote', 'sell_stock'
    biz_id = req.get('biz_id')
    
    data = db.supabase.table("economy").select("balance, businesses").eq("user_id", user_id).execute().data
    balance = data[0]['balance']
    owned = data[0]['businesses']
    
    if biz_id not in owned: return jsonify({"status": "error", "msg": "Not owned"})
    
    biz = owned[biz_id]
    msg = ""
    
    if action == 'resupply':
        cost = 75000
        if balance < cost: return jsonify({"status":"error", "msg":"Need $75k"})
        if biz['supplies'] >= 100: return jsonify({"status":"error", "msg":"Supplies Full"})
        
        balance -= cost
        biz['supplies'] = 100
        msg = "Supplies Restocked!"
        
    elif action == 'promote':
        cost = 10000
        if balance < cost: return jsonify({"status":"error", "msg":"Need $10k"})
        if biz['popularity'] >= 100: return jsonify({"status":"error", "msg":"Popularity Max"})
        
        balance -= cost
        biz['popularity'] = 100
        msg = "Popularity Boosted!"
        
    elif action == 'sell_stock':
        stock_val = biz['stock']
        if stock_val <= 0: return jsonify({"status":"error", "msg":"No Stock to sell"})
        
        balance += stock_val
        biz['stock'] = 0
        msg = f"Sold Stock for ${stock_val:,}!"

    # Save
    db.supabase.table("economy").update({
        "balance": balance, "businesses": owned
    }).eq("user_id", user_id).execute()
    
    return jsonify({"status": "success", "msg": msg, "new_bal": balance})

# --- API: RAID (ATTACK OTHERS) ---
@app.route('/api/business/raid', methods=['POST'])
def raid_business():
    attacker_id = session['user_info']['id']
    bet = int(request.json.get('bet', 100000))
    
    # Fetch Attacker Balance
    data = db.supabase.table("economy").select("balance").eq("user_id", attacker_id).execute().data
    if data[0]['balance'] < bet:
        return jsonify({"status": "error", "msg": "Not enough cash to fund this raid!"})
    
    # RNG Logic (50-50 Chance)
    import random
    success = random.random() < 0.5
    
    if success:
        # Win: Get 2x Bet
        winnings = bet * 2
        db.update_balance(attacker_id, winnings - bet) # Profit add
        return jsonify({"status": "win", "msg": f"Raid Successful! You stole ${winnings:,}!", "amount": winnings})
    else:
        # Lose: Money Deducted (Technically 'transferred' to system owner/void)
        # User said: "loss hua toh wo saare loss ke ammount tumhara pass" 
        # Here we just deduct from attacker. To implement transfer to specific user, we need Target ID.
        # For now, simpler: Risk vs System.
        db.update_balance(attacker_id, -bet)
        return jsonify({"status": "lose", "msg": f"Raid Failed! You lost ${bet:,} to security.", "amount": -bet})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
