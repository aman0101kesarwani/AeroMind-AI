import os

from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# Load Environment Variables
# ============================================================

load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")


# ============================================================
# Validate Configuration
# ============================================================

if not SUPABASE_URL:

    raise ValueError(
        "SUPABASE_URL is missing."
    )


if not SUPABASE_SECRET_KEY:

    raise ValueError(
        "SUPABASE_SECRET_KEY is missing."
    )


# ============================================================
# Supabase Client
# ============================================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)