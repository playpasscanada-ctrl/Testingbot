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

# --- 8. BUSINESS DASHBOARD & DELIVERY CHECK ---
@app.route('/business')
def business_dashboard():
    if 'user_info' not in session: return redirect('/')
    user_id = session['user_info']['id']
    
    data = db.supabase.table("economy").select("balance, businesses").eq("user_id", user_id).execute().data
    if not data: return "Error loading data."
    
    balance = data[0]['balance']
    owned_businesses = data[0]['businesses'] or {}
    current_time = int(time.time())

    # --- DELIVERY & PASSIVE INCOME LOGIC ---
    for biz_id, biz in owned_businesses.items():
        # 1. Check Pending Delivery (3 Hours System)
        if 'delivery_time' in biz and biz['delivery_time'] > 0:
            if current_time >= biz['delivery_time']:
                # Delivery Arrived!
                biz['supplies'] = 100
                biz['delivery_time'] = 0 # Reset
        
        # 2. Passive Income Calculation
        last_check = biz.get('last_check', current_time)
        hours_passed = (current_time - last_check) / 3600
        
        if hours_passed > 0:
            rate = BUSINESSES[biz_id]['income_per_hr']
            supplies = biz.get('supplies', 0)
            
            if supplies > 0:
                # Production based on Popularity
                production = int(rate * hours_passed * (biz.get('popularity', 100)/100))
                max_st = BUSINESSES[biz_id]['max_stock']
                biz['stock'] = min(biz.get('stock', 0) + production, max_st)
                
                # Consumption
                biz['supplies'] = max(0, supplies - int(hours_passed * 10))
                biz['popularity'] = max(0, int(biz.get('popularity', 100) - hours_passed))
                biz['last_check'] = current_time

    db.supabase.table("economy").update({"businesses": owned_businesses}).eq("user_id", user_id).execute()

    return render_template('business.html', user=session['user_info'], balance=balance, owned=owned_businesses, all_biz=BUSINESSES, now=current_time)


# --- 9. API: ORDER SUPPLIES (3 HOURS DELAY) ---
@app.route('/api/business/order', methods=['POST'])
def order_supplies():
    if 'user_info' not in session: return jsonify({"status":"error", "msg":"Login First"})
    user_id = session['user_info']['id']
    biz_id = request.json.get('biz_id')
    
    data = db.supabase.table("economy").select("balance, businesses").eq("user_id", user_id).execute().data
    bal = data[0]['balance']
    owned = data[0]['businesses']
    
    if biz_id not in owned: return jsonify({"status":"error", "msg":"Not Owned"})
    
    # Check if already delivering
    if owned[biz_id].get('delivery_time', 0) > time.time():
         return jsonify({"status":"error", "msg":"Supply truck already on the way!"})

    cost = 75000
    if bal < cost: return jsonify({"status":"error", "msg":"Need $75k"})
    
    # 3 HOURS DELAY (3 * 3600 seconds)
    arrival_time = int(time.time()) + (3 * 3600)
    
    owned[biz_id]['delivery_time'] = arrival_time
    
    db.supabase.table("economy").update({"balance": bal - cost, "businesses": owned}).eq("user_id", user_id).execute()
    return jsonify({"status":"success", "msg": "Supplies ordered! Arriving in 3 Hours."})


# --- 10. API: BUSINESS ACTIONS (SELL/PROMOTE + PROFIT SPLIT) ---
@app.route('/api/business/action', methods=['POST'])
def biz_action():
    if 'user_info' not in session: return jsonify({"status":"error", "msg":"Login First"})

    user_id = session['user_info']['id']
    req = request.json
    action = req.get('action') 
    biz_id = req.get('biz_id')
    
    data = db.supabase.table("economy").select("balance, businesses").eq("user_id", user_id).execute().data
    balance = data[0]['balance']
    owned = data[0]['businesses']
    
    if biz_id not in owned: return jsonify({"status": "error", "msg": "You don't own this!"})
    
    biz = owned[biz_id]
    msg = ""
    
    if action == 'promote':
        cost = 10000
        if balance < cost: return jsonify({"status":"error", "msg":"Need $10k"})
        if biz['popularity'] >= 100: return jsonify({"status":"error", "msg":"Popularity Maxed!"})
        balance -= cost
        biz['popularity'] = 100
        msg = "Popularity Boosted!"
        
    elif action == 'sell_stock':
        stock_val = biz['stock']
        if stock_val <= 0: return jsonify({"status":"error", "msg":"No Stock to sell"})
        
        # --- INVESTMENT PROFIT SPLIT LOGIC ---
        final_profit = stock_val
        
        # Agar Investor hai, to 20% usko bhejo
        if biz.get('has_investor') and biz.get('investor_id'):
            investor_share = int(stock_val * 0.20) # 20% Share
            investor_id = biz['investor_id']
            final_profit = stock_val - investor_share # Owner gets 80%
            
            # Investor ko paisa bhejo (Using helper function)
            db.update_balance(investor_id, investor_share)
            msg = f"Stock Sold! You kept ${final_profit:,} (Partner took ${investor_share:,})"
        else:
            msg = f"Stock Sold! Earned ${final_profit:,}"
            
        balance += final_profit
        biz['stock'] = 0

    # Save
    db.supabase.table("economy").update({
        "balance": balance, "businesses": owned
    }).eq("user_id", user_id).execute()
    
    return jsonify({"status": "success", "msg": msg, "new_bal": balance})


# --- 11. API: BUY SECURITY ---
@app.route('/api/business/security', methods=['POST'])
def buy_security():
    user_id = session['user_info']['id']
    biz_id = request.json.get('biz_id')
    
    data = db.supabase.table("economy").select("balance, businesses").eq("user_id", user_id).execute().data
    bal = data[0]['balance']
    owned = data[0]['businesses']
    
    current_sec = owned[biz_id].get('security', 1)
    if current_sec >= 5: return jsonify({"status":"error", "msg":"Max Security Reached!"})
    
    cost = 500000 * current_sec # Cost increases with level
    if bal < cost: return jsonify({"status":"error", "msg":f"Need ${cost:,} for upgrade"})
    
    owned[biz_id]['security'] = current_sec + 1
    db.supabase.table("economy").update({"balance": bal - cost, "businesses": owned}).eq("user_id", user_id).execute()
    
    return jsonify({"status":"success", "msg": "Security Upgraded! Hackers will struggle."})


# --- 12. API: GET HACKING TARGETS (ALSO USED FOR INVESTMENT LISTING) ---
@app.route('/api/business/targets', methods=['GET'])
def get_targets():
    all_users = db.supabase.table("economy").select("user_id, businesses").neq("businesses", "{}").limit(20).execute().data
    targets = []
    my_id = session['user_info']['id']
    
    for u in all_users:
        if u['user_id'] == my_id: continue 
        
        for b_id, b_data in u['businesses'].items():
            targets.append({
                "user_id": u['user_id'],
                "biz_name": BUSINESSES[b_id]['name'],
                "biz_id": b_id,
                "security": b_data.get('security', 1),
                "stock": b_data.get('stock', 0),
                "investment_open": b_data.get('investment_open', False),
                "has_investor": b_data.get('has_investor', False)
            })
            
    return jsonify(targets)


# --- 13. API: HEIST EXECUTION (THE 4 STEPS RESULT) ---
@app.route('/api/business/heist', methods=['POST'])
def execute_heist():
    hacker_id = session['user_info']['id']
    req = request.json
    target_id = req.get('target_id')
    biz_id = req.get('biz_id')
    step_success = req.get('success') 
    
    # 1. Check Hacker Balance (Entry Fee)
    hacker_data = db.supabase.table("economy").select("balance, businesses").eq("user_id", hacker_id).execute().data
    if hacker_data[0]['balance'] < 100000000: 
        return jsonify({"status":"error", "msg":"Insufficient Funds for Heist Kit ($100M required)"})

    # Deduct 100M Entry Fee
    new_hacker_bal = hacker_data[0]['balance'] - 100000000
    
    if not step_success:
        db.supabase.table("economy").update({"balance": new_hacker_bal}).eq("user_id", hacker_id).execute()
        return jsonify({"status":"fail", "msg":"HACK FAILED! You lost $100M."})

    # 2. Fetch Target
    target_data = db.supabase.table("economy").select("businesses").eq("user_id", target_id).execute().data
    target_biz = target_data[0]['businesses']
    
    # 3. Security Check (Final RNG Layer)
    security_lvl = target_biz[biz_id].get('security', 1)
    win_chance = 1.0 - (security_lvl * 0.15) 
    
    if random.random() > win_chance:
        db.supabase.table("economy").update({"balance": new_hacker_bal}).eq("user_id", hacker_id).execute()
        return jsonify({"status":"fail", "msg": f"Target Security Level {security_lvl} blocked your breach!"})
    
    # 4. SUCCESS: TRANSFER OWNERSHIP
    stolen_biz_data = target_biz.pop(biz_id)
    # Reset investment status on theft (Optional rule)
    stolen_biz_data['has_investor'] = False 
    stolen_biz_data['investment_open'] = False
    
    db.supabase.table("economy").update({"businesses": target_biz}).eq("user_id", target_id).execute()
    
    hacker_biz = hacker_data[0]['businesses'] or {}
    hacker_biz[biz_id] = stolen_biz_data 
    
    db.supabase.table("economy").update({
        "balance": new_hacker_bal, "businesses": hacker_biz
    }).eq("user_id", hacker_id).execute()
    
    return jsonify({"status":"success", "msg":"SYSTEM BREACHED! Ownership transferred to you."})


# --- 14. API: LIST FOR INVESTMENT (NEW) ---
@app.route('/api/business/open_investment', methods=['POST'])
def open_investment():
    if 'user_info' not in session: return jsonify({"status":"error", "msg":"Login First"})
    user_id = session['user_info']['id']
    biz_id = request.json.get('biz_id')
    
    data = db.supabase.table("economy").select("balance, businesses").eq("user_id", user_id).execute().data
    owned = data[0]['businesses']
    
    if owned[biz_id].get('has_investor', False):
         return jsonify({"status":"error", "msg":"Already has an investor!"})

    # Price = 50% of original business price
    invest_price = int(BUSINESSES[biz_id]['price'] * 0.5)
    owned[biz_id]['investment_open'] = True
    owned[biz_id]['invest_price'] = invest_price
    
    db.supabase.table("economy").update({"businesses": owned}).eq("user_id", user_id).execute()
    return jsonify({"status":"success", "msg": f"Listed for Investment! Price: ${invest_price:,}"})


# --- 15. API: INVEST NOW (NEW) ---
@app.route('/api/business/invest_now', methods=['POST'])
def invest_now():
    if 'user_info' not in session: return jsonify({"status":"error", "msg":"Login First"})
    investor_id = session['user_info']['id']
    req = request.json
    target_id = req.get('target_id')
    biz_id = req.get('biz_id')
    
    if investor_id == target_id: return jsonify({"status":"error", "msg":"Cannot invest in yourself!"})

    # Fetch Data
    investor_data = db.supabase.table("economy").select("balance").eq("user_id", investor_id).execute().data
    target_data = db.supabase.table("economy").select("balance, businesses").eq("user_id", target_id).execute().data
    
    target_biz = target_data[0]['businesses']
    biz = target_biz.get(biz_id)
    
    if not biz or not biz.get('investment_open'):
        return jsonify({"status":"error", "msg":"Investment closed."})
        
    cost = biz['invest_price']
    
    if investor_data[0]['balance'] < cost:
        return jsonify({"status":"error", "msg":"Insufficient Funds to Invest!"})

    # Transaction: Investor pays, Owner gets cash
    new_inv_bal = investor_data[0]['balance'] - cost
    new_owner_bal = target_data[0]['balance'] + cost
    
    biz['investment_open'] = False
    biz['has_investor'] = True
    biz['investor_id'] = investor_id
    biz['equity'] = 0.20
    
    db.supabase.table("economy").update({"balance": new_inv_bal}).eq("user_id", investor_id).execute()
    db.supabase.table("economy").update({"balance": new_owner_bal, "businesses": target_biz}).eq("user_id", target_id).execute()
    
    return jsonify({"status":"success", "msg": f"Investment Successful! You own 20% of this business."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
