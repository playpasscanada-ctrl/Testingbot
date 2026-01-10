import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user_balance(user_id):
    try:
        res = supabase.table('economy').select("balance").eq('user_id', str(user_id)).execute()
        return res.data[0]['balance'] if res.data else 0
    except: return 0

def update_balance(user_id, amount):
    try:
        current = get_user_balance(user_id)
        new_bal = current + amount
        supabase.table('economy').update({"balance": new_bal}).eq('user_id', str(user_id)).execute()
        return new_bal
    except: return 0
