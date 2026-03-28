from supabase import create_client, Client
from app.config import settings

# Admin client — uses service_role key, bypasses RLS
# Only used server-side in FastAPI, never exposed to the browser
supabase_admin: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key,
)
