# business_config.py

BUSINESSES = {
    # ==========================================
    # 🏛️ EXISTING BUSINESSES (DO NOT TOUCH)
    # ==========================================
    "weed_farm": {
        "name": "Weed Farm 🌿", "price": 100000000, 
        "income_per_hr": 500000, "max_stock": 5000000, "supply_cost": 50000
    },
    "meth_lab": {
        "name": "Meth Lab 🧪", "price": 110000000, 
        "income_per_hr": 600000, "max_stock": 6000000, "supply_cost": 60000
    },
    "counterfeit_cash": {
        "name": "Counterfeit Cash 💵", "price": 120000000, 
        "income_per_hr": 700000, "max_stock": 7000000, "supply_cost": 70000
    },
    "cocaine_lockup": {
        "name": "Cocaine Lockup 🍚", "price": 130000000, 
        "income_per_hr": 800000, "max_stock": 8000000, "supply_cost": 80000
    },
    "bunker": {
        "name": "Gunrunning Bunker 🔫", "price": 140000000, 
        "income_per_hr": 900000, "max_stock": 9000000, "supply_cost": 90000
    },
    "luxury_cars": {
        "name": "Luxury Car Dealership 🏎️", "price": 145000000, 
        "income_per_hr": 950000, "max_stock": 9500000, "supply_cost": 95000
    },
    "nightclub": {
        "name": "Nightclub Empire 🕺", "price": 150000000, 
        "income_per_hr": 1000000, "max_stock": 10000000, "supply_cost": 100000
    },
    "hacking": {
        "name": "Hacking Facility 💻", "price": 160000000, 
        "income_per_hr": 1100000, "max_stock": 11000000, "supply_cost": 110000
    },
    "drone_factory": {
        "name": "Drone Manufacturing 🛸", "price": 170000000, 
        "income_per_hr": 1200000, "max_stock": 12000000, "supply_cost": 120000
    },
    "casino": {
        "name": "Underground Casino 🎲", "price": 180000000, 
        "income_per_hr": 1300000, "max_stock": 13000000, "supply_cost": 130000
    },
    "gold": {
        "name": "Gold Smuggling 🟡", "price": 190000000, 
        "income_per_hr": 1400000, "max_stock": 14000000, "supply_cost": 140000
    },
    "oil": {
        "name": "Oil Company 🛢️", "price": 200000000, 
        "income_per_hr": 1500000, "max_stock": 15000000, "supply_cost": 150000
    },
    "crypto_farm": {
        "name": "Crypto Server Farm ₿", "price": 210000000, 
        "income_per_hr": 1600000, "max_stock": 16000000, "supply_cost": 160000
    },
    "cyber_clinic": {
        "name": "Cybernetics Clinic 🦾", "price": 220000000, 
        "income_per_hr": 1700000, "max_stock": 17000000, "supply_cost": 170000
    },
    "ai_lab": {
        "name": "AI Research Lab 🤖", "price": 230000000, 
        "income_per_hr": 1800000, "max_stock": 18000000, "supply_cost": 180000
    },
    "pmc": {
        "name": "Private Military Army 🎖️", "price": 250000000, 
        "income_per_hr": 2000000, "max_stock": 20000000, "supply_cost": 200000
    },
    "space_station": {
        "name": "Space Station Resort 🚀", "price": 300000000, 
        "income_per_hr": 2500000, "max_stock": 25000000, "supply_cost": 250000
    },
    "clone_factory": {
        "name": "Cloning Facility 🧬", "price": 350000000, 
        "income_per_hr": 3000000, "max_stock": 30000000, "supply_cost": 300000
    },
    "fusion_reactor": {
        "name": "Fusion Energy Plant ⚛️", "price": 400000000, 
        "income_per_hr": 3500000, "max_stock": 35000000, "supply_cost": 350000
    },
    "time_machine": {
        "name": "Time Travel Agency ⏳", "price": 1000000000, 
        "income_per_hr": 10000000, "max_stock": 100000000, "supply_cost": 1000000
    },

    "weather_control": {
        "name": "Weather Control Station ⛈️", "price": 1500000000, 
        "income_per_hr": 15000000, "max_stock": 150000000, "supply_cost": 1500000
    },
    "asteroid_mining": {
        "name": "Asteroid Mining Corp 🌑", "price": 2000000000, 
        "income_per_hr": 20000000, "max_stock": 200000000, "supply_cost": 2000000
    },
    "ocean_city": {
        "name": "Underwater Metropolis 🧜‍♂️", "price": 2800000000, 
        "income_per_hr": 28000000, "max_stock": 280000000, "supply_cost": 2800000
    },
    "mars_colony": {
        "name": "Mars Colony Prime 🔴", "price": 3500000000, 
        "income_per_hr": 35000000, "max_stock": 350000000, "supply_cost": 3500000
    },
    "quantum_comp": {
        "name": "Quantum Supercomputer 🖥️", "price": 5000000000, 
        "income_per_hr": 50000000, "max_stock": 500000000, "supply_cost": 5000000
    },
    "immortality_lab": {
        "name": "Immortality Research 💉", "price": 7500000000, 
        "income_per_hr": 75000000, "max_stock": 750000000, "supply_cost": 7500000
    },
    "nanotech_swarm": {
        "name": "Nanotech Grey Goo 🦠", "price": 10000000000, 
        "income_per_hr": 100000000, "max_stock": 1000000000, "supply_cost": 10000000
    },
    "orbital_laser": {
        "name": "Orbital Death Laser 🛰️", "price": 15000000000, 
        "income_per_hr": 150000000, "max_stock": 1500000000, "supply_cost": 15000000
    },
    "moon_base": {
        "name": "Lunar Helium-3 Mine 🌕", "price": 20000000000, 
        "income_per_hr": 200000000, "max_stock": 2000000000, "supply_cost": 20000000
    },
    "dyson_prototype": {
        "name": "Mini Dyson Sphere ☀️", "price": 30000000000, 
        "income_per_hr": 300000000, "max_stock": 3000000000, "supply_cost": 30000000
    },
    "portal_network": {
        "name": "Interstellar Portals 🌀", "price": 50000000000, 
        "income_per_hr": 500000000, "max_stock": 5000000000, "supply_cost": 50000000
    },
    "antimatter_plant": {
        "name": "Antimatter Refinery 💥", "price": 75000000000, 
        "income_per_hr": 750000000, "max_stock": 7500000000, "supply_cost": 75000000
    },
    "planet_terraform": {
        "name": "Planet Terraformer 🌍", "price": 100000000000, 
        "income_per_hr": 1000000000, "max_stock": 10000000000, "supply_cost": 100000000
    },
    "galactic_senate": {
        "name": "Galactic Senate Seat 👑", "price": 250000000000, 
        "income_per_hr": 2500000000, "max_stock": 25000000000, "supply_cost": 250000000
    },
    "black_hole_gen": {
        "name": "Black Hole Generator 🕳️", "price": 500000000000, 
        "income_per_hr": 5000000000, "max_stock": 50000000000, "supply_cost": 500000000
    },
    "matrix_sim": {
        "name": "Reality Simulation (Matrix) 💾", "price": 750000000000, 
        "income_per_hr": 7500000000, "max_stock": 75000000000, "supply_cost": 750000000
    },
    "star_forge": {
        "name": "Star Forge Foundry 🔥", "price": 1000000000000, 
        "income_per_hr": 10000000000, "max_stock": 100000000000, "supply_cost": 1000000000
    },
    "multiverse_trade": {
        "name": "Multiverse Trade Route 🌌", "price": 2500000000000, 
        "income_per_hr": 25000000000, "max_stock": 250000000000, "supply_cost": 2500000000
    },
    "timeline_editor": {
        "name": "Timeline Editor Authority ⏱️", "price": 5000000000000, 
        "income_per_hr": 50000000000, "max_stock": 500000000000, "supply_cost": 5000000000
    },
    "void_bank": {
        "name": "The Void Central Bank ♾️", "price": 10000000000000, 
        "income_per_hr": 100000000000, "max_stock": 1000000000000, "supply_cost": 10000000000
    }
}
