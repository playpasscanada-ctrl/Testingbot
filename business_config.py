# business_config.py

# ==========================================
# 🏢 ALL BUSINESSES (Standard + Ultra Premium)
# ==========================================
# New Logic: "supply_duration" (Hours) added.
# Cheap Business = Low Duration (Needs active play)
# Expensive Business = High Duration (Passive play)

BUSINESSES = {
    # --- TIER 1: STREET LEVEL (High Maintenance: 1-2 Hours) ---
    "weed_farm": {
        "name": "Weed Farm 🌿", "price": 100000000, 
        "income_per_hr": 500000, "max_stock": 5000000, "supply_cost": 50000,
        "supply_duration": 1 # 1 Hour only
    },
    "meth_lab": {
        "name": "Meth Lab 🧪", "price": 110000000, 
        "income_per_hr": 600000, "max_stock": 6000000, "supply_cost": 60000,
        "supply_duration": 1.5 
    },
    "counterfeit_cash": {
        "name": "Counterfeit Cash 💵", "price": 120000000, 
        "income_per_hr": 700000, "max_stock": 7000000, "supply_cost": 70000,
        "supply_duration": 2
    },
    "cocaine_lockup": {
        "name": "Cocaine Lockup 🍚", "price": 130000000, 
        "income_per_hr": 800000, "max_stock": 8000000, "supply_cost": 80000,
        "supply_duration": 2.5
    },
    
    # --- TIER 2: CORPORATE CRIME (Moderate: 3-6 Hours) ---
    "bunker": {
        "name": "Gunrunning Bunker 🔫", "price": 140000000, 
        "income_per_hr": 900000, "max_stock": 9000000, "supply_cost": 90000,
        "supply_duration": 3
    },
    "luxury_cars": {
        "name": "Luxury Car Dealership 🏎️", "price": 145000000, 
        "income_per_hr": 950000, "max_stock": 9500000, "supply_cost": 95000,
        "supply_duration": 3.5
    },
    "nightclub": {
        "name": "Nightclub Empire 🕺", "price": 150000000, 
        "income_per_hr": 1000000, "max_stock": 10000000, "supply_cost": 100000,
        "supply_duration": 4
    },
    "hacking": {
        "name": "Hacking Facility 💻", "price": 160000000, 
        "income_per_hr": 1100000, "max_stock": 11000000, "supply_cost": 110000,
        "supply_duration": 4.5
    },
    "drone_factory": {
        "name": "Drone Manufacturing 🛸", "price": 170000000, 
        "income_per_hr": 1200000, "max_stock": 12000000, "supply_cost": 120000,
        "supply_duration": 5
    },
    "casino": {
        "name": "Underground Casino 🎲", "price": 180000000, 
        "income_per_hr": 1300000, "max_stock": 13000000, "supply_cost": 130000,
        "supply_duration": 6
    },
    
    # --- TIER 3: HIGH TECH (Long Lasting: 7-12 Hours) ---
    "gold": {
        "name": "Gold Smuggling 🟡", "price": 190000000, 
        "income_per_hr": 1400000, "max_stock": 14000000, "supply_cost": 140000,
        "supply_duration": 7
    },
    "oil": {
        "name": "Oil Company 🛢️", "price": 200000000, 
        "income_per_hr": 1500000, "max_stock": 15000000, "supply_cost": 150000,
        "supply_duration": 8
    },
    "crypto_farm": {
        "name": "Crypto Server Farm ₿", "price": 210000000, 
        "income_per_hr": 1600000, "max_stock": 16000000, "supply_cost": 160000,
        "supply_duration": 9
    },
    "cyber_clinic": {
        "name": "Cybernetics Clinic 🦾", "price": 220000000, 
        "income_per_hr": 1700000, "max_stock": 17000000, "supply_cost": 170000,
        "supply_duration": 10
    },
    "ai_lab": {
        "name": "AI Research Lab 🤖", "price": 230000000, 
        "income_per_hr": 1800000, "max_stock": 18000000, "supply_cost": 180000,
        "supply_duration": 11
    },
    "pmc": {
        "name": "Private Military Army 🎖️", "price": 250000000, 
        "income_per_hr": 2000000, "max_stock": 20000000, "supply_cost": 200000,
        "supply_duration": 12
    },
    "space_station": {
        "name": "Space Station Resort 🚀", "price": 300000000, 
        "income_per_hr": 2500000, "max_stock": 25000000, "supply_cost": 250000,
        "supply_duration": 14
    },
    "clone_factory": {
        "name": "Cloning Facility 🧬", "price": 350000000, 
        "income_per_hr": 3000000, "max_stock": 30000000, "supply_cost": 300000,
        "supply_duration": 16
    },
    "fusion_reactor": {
        "name": "Fusion Energy Plant ⚛️", "price": 400000000, 
        "income_per_hr": 3500000, "max_stock": 35000000, "supply_cost": 350000,
        "supply_duration": 18
    },
    "time_machine": {
        "name": "Time Travel Agency ⏳", "price": 1000000000, 
        "income_per_hr": 10000000, "max_stock": 100000000, "supply_cost": 1000000,
        "supply_duration": 20
    },

    # --- TIER 4: GOD TIER (Ultra Premium: 24 Hours / 1 Day) ---
    "weather_control": {
        "name": "Weather Control Station ⛈️", "price": 1500000000, 
        "income_per_hr": 15000000, "max_stock": 150000000, "supply_cost": 1500000,
        "supply_duration": 24
    },
    "asteroid_mining": {
        "name": "Asteroid Mining Corp 🌑", "price": 2000000000, 
        "income_per_hr": 20000000, "max_stock": 200000000, "supply_cost": 2000000,
        "supply_duration": 24
    },
    "ocean_city": {
        "name": "Underwater Metropolis 🧜‍♂️", "price": 2800000000, 
        "income_per_hr": 28000000, "max_stock": 280000000, "supply_cost": 2800000,
        "supply_duration": 24
    },
    "mars_colony": {
        "name": "Mars Colony Prime 🔴", "price": 3500000000, 
        "income_per_hr": 35000000, "max_stock": 350000000, "supply_cost": 3500000,
        "supply_duration": 24
    },
    "quantum_comp": {
        "name": "Quantum Supercomputer 🖥️", "price": 500000000000, 
        "income_per_hr": 50000000, "max_stock": 500000000, "supply_cost": 5000000,
        "supply_duration": 24
    },
    "immortality_lab": {
        "name": "Immortality Research 💉", "price": 7500000000000, 
        "income_per_hr": 75000000, "max_stock": 750000000, "supply_cost": 7500000,
        "supply_duration": 24
    },
    "nanotech_swarm": {
        "name": "Nanotech Grey Goo 🦠", "price": 10000000000000, 
        "income_per_hr": 100000000, "max_stock": 1000000000, "supply_cost": 10000000,
        "supply_duration": 24
    },
    "orbital_laser": {
        "name": "Orbital Death Laser 🛰️", "price": 15000000000000, 
        "income_per_hr": 150000000, "max_stock": 1500000000, "supply_cost": 15000000,
        "supply_duration": 24
    },
    "moon_base": {
        "name": "Lunar Helium-3 Mine 🌕", "price": 20000000000000, 
        "income_per_hr": 200000000, "max_stock": 2000000000, "supply_cost": 20000000,
        "supply_duration": 24
    },
    "dyson_prototype": {
        "name": "Mini Dyson Sphere ☀️", "price": 30000000000000, 
        "income_per_hr": 300000000, "max_stock": 3000000000, "supply_cost": 30000000,
        "supply_duration": 24
    },
    "portal_network": {
        "name": "Interstellar Portals 🌀", "price": 5000000000000, 
        "income_per_hr": 500000000, "max_stock": 5000000000, "supply_cost": 50000000,
        "supply_duration": 24
    },
    "antimatter_plant": {
        "name": "Antimatter Refinery 💥", "price": 75000000000000, 
        "income_per_hr": 750000000, "max_stock": 7500000000, "supply_cost": 75000000,
        "supply_duration": 24
    },
    "planet_terraform": {
        "name": "Planet Terraformer 🌍", "price": 100000000000000, 
        "income_per_hr": 1000000000, "max_stock": 10000000000, "supply_cost": 100000000,
        "supply_duration": 24
    },
    "galactic_senate": {
        "name": "Galactic Senate Seat 👑", "price": 250000000000000, 
        "income_per_hr": 2500000000, "max_stock": 25000000000, "supply_cost": 250000000,
        "supply_duration": 24
    },
    "black_hole_gen": {
        "name": "Black Hole Generator 🕳️", "price": 500000000000000, 
        "income_per_hr": 5000000000, "max_stock": 50000000000, "supply_cost": 500000000,
        "supply_duration": 24
    },
    "matrix_sim": {
        "name": "Reality Simulation (Matrix) 💾", "price": 750000000000000, 
        "income_per_hr": 7500000000, "max_stock": 75000000000, "supply_cost": 750000000,
        "supply_duration": 24
    },
    "star_forge": {
        "name": "Star Forge Foundry 🔥", "price": 1000000000000000, 
        "income_per_hr": 10000000000, "max_stock": 100000000000, "supply_cost": 1000000000,
        "supply_duration": 24
    },
    "multiverse_trade": {
        "name": "Multiverse Trade Route 🌌", "price": 250000000000000000, 
        "income_per_hr": 25000000000, "max_stock": 250000000000, "supply_cost": 2500000000,
        "supply_duration": 24
    },
    "timeline_editor": {
        "name": "Timeline Editor Authority ⏱️", "price": 500000000000000000, 
        "income_per_hr": 50000000000, "max_stock": 500000000000, "supply_cost": 5000000000,
        "supply_duration": 24
    },
    "void_bank": {
        "name": "The Void Central Bank ♾️", "price": 10000000000000000000, 
        "income_per_hr": 100000000000, "max_stock": 1000000000000, "supply_cost": 10000000000,
        "supply_duration": 24
    }
}

# ==========================================
# 🚨 ILLEGAL BUSINESSES (Subject to Police Raids)
# ==========================================
ILLEGAL_BIZ = [
    # Drugs & Crime
    "weed_farm", "meth_lab", "counterfeit_cash", "cocaine_lockup", "bunker", 
    "hacking", "casino", "gold", "pmc",
    
    # Sci-Fi Crimes (Unethical/Dangerous)
    "clone_factory", "nanotech_swarm", "orbital_laser", "antimatter_plant",
    "black_hole_gen", "matrix_sim", "timeline_editor", "void_bank"
]

# ==========================================
# 🤖 MANAGER PRICES (10% of Business Cost)
# ==========================================
MANAGER_PRICES = {
    # Tier 1
    "weed_farm": 10000000,
    "meth_lab": 11000000,
    "counterfeit_cash": 12000000,
    "cocaine_lockup": 13000000,
    
    # Tier 2
    "bunker": 14000000,
    "luxury_cars": 14500000,
    "nightclub": 15000000,
    "hacking": 16000000,
    "drone_factory": 17000000,
    "casino": 18000000,
    
    # Tier 3
    "gold": 19000000,
    "oil": 20000000,
    "crypto_farm": 21000000,
    "cyber_clinic": 22000000,
    "ai_lab": 23000000,
    "pmc": 25000000,
    "space_station": 30000000,
    "clone_factory": 35000000,
    "fusion_reactor": 40000000,
    "time_machine": 100000000,

    # Tier 4 (Ultra Premium)
    "weather_control": 150000000,
    "asteroid_mining": 200000000,
    "ocean_city": 280000000,
    "mars_colony": 350000000,
    "quantum_comp": 500000000,
    "immortality_lab": 750000000,
    "nanotech_swarm": 1000000000,
    "orbital_laser": 1500000000,
    "moon_base": 2000000000,
    "dyson_prototype": 3000000000,
    "portal_network": 5000000000,
    "antimatter_plant": 7500000000,
    "planet_terraform": 10000000000,
    "galactic_senate": 25000000000,
    "black_hole_gen": 50000000000000,
    "matrix_sim": 75000000000000,
    "star_forge": 100000000000000,
    "multiverse_trade": 250000000000000,
    "timeline_editor": 500000000000000,
    "void_bank": 1000000000000000,
    
    "default": 100000000 # Fallback
}

# ==========================================
# 📊 MARKET EVENTS (20+ Events)
# ==========================================
MARKET_EVENTS = [
    # --- GOOD EVENTS (Boom) ---
    {"name": "Bull Market 🐂", "multiplier": 1.5, "msg": "Global Economy Booming! All Income +50%"},
    {"name": "Tech Revolution 🤖", "multiplier": 1.8, "msg": "AI Breakout! Tech Business Income +80%"},
    {"name": "Crypto Surge 🚀", "multiplier": 2.0, "msg": "Bitcoin to the Moon! Crypto/Hacking Income +100%"},
    {"name": "Space Age 🌌", "multiplier": 2.5, "msg": "Mars Landing Successful! Space Biz Income +150%"},
    {"name": "The Purge 💀", "multiplier": 3.0, "msg": "Laws Suspended! Illegal Income +200%"},
    {"name": "Hyperinflation 💸", "multiplier": 1.4, "msg": "Money Printing Error! All Cash Flow +40%"},
    {"name": "Festival Season 🎉", "multiplier": 1.6, "msg": "Party Time! Nightclub & Casino Income +60%"},
    {"name": "War Declared ⚔️", "multiplier": 2.2, "msg": "Global Conflict! Weapons/PMC Income +120%"},
    {"name": "Aliens Arrive 👽", "multiplier": 4.0, "msg": "First Contact! Galactic Biz Income +300%"},
    {"name": "Gold Rush 🟡", "multiplier": 1.7, "msg": "New Mines Found! Resource Biz Income +70%"},

    # --- BAD EVENTS (Crash) ---
    {"name": "Market Crash 📉", "multiplier": 0.5, "msg": "Stock Market Collapse! All Income -50%"},
    {"name": "FBI Crackdown 🚨", "multiplier": 0.3, "msg": "Massive Police Raids! Illegal Income -70%"},
    {"name": "Solar Flare ☀️", "multiplier": 0.4, "msg": "Electronics Fried! Tech/Crypto Income -60%"},
    {"name": "Pandemic 😷", "multiplier": 0.6, "msg": "Global Lockdown! Public Biz Income -40%"},
    {"name": "Peace Treaty 🕊️", "multiplier": 0.5, "msg": "World Peace Achieved! Weapons/PMC Income -50%"},
    {"name": "Energy Crisis ⚡", "multiplier": 0.7, "msg": "Power Grid Failure! Factory Income -30%"},
    {"name": "Tax Audit 📝", "multiplier": 0.8, "msg": "IRS Investigation! All Income -20%"},
    {"name": "Cyber Attack 👾", "multiplier": 0.5, "msg": "Global Ransomware! Hacking/Tech Income -50%"},
    {"name": "Time Paradox ⏳", "multiplier": 0.1, "msg": "Timeline Unstable! Future Biz Income -90%"},
    {"name": "Meteor Shower ☄️", "multiplier": 0.6, "msg": "Infrastructure Damage! Space Biz Income -40%"}
]
