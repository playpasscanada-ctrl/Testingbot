import os
import random
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import db

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
