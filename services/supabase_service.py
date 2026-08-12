import os

from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# Load environment
# ============================================================

load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")

# Prefer the new name.
# Keep SUPABASE_SECRET_KEY as fallback so your current setup
# continues working.
SUPABASE_SERVICE_ROLE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_SECRET_KEY")
)


# ============================================================
# Validate configuration
# ============================================================

if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL is missing."
    )


if not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError(
        "SUPABASE_SERVICE_ROLE_KEY is missing."
    )


# ============================================================
# Supabase client
# ============================================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)