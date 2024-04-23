from supabase_py import create_client
from config import Config

# Create Supabase client
supabase_client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
