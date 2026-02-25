import os
from supabase import create_client

with open("backend/.env", "r") as f:
    for line in f:
        if line.startswith("SUPABASE_URL="):
            os.environ["SUPABASE_URL"] = line.strip().split("=", 1)[1]
        elif line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
            os.environ["SUPABASE_SERVICE_ROLE_KEY"] = line.strip().split("=", 1)[1]

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
result = supabase.table("user_threads").select("*").limit(1).execute()
print(result.data)
