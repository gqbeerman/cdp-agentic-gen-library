import os
from supabase import create_client

with open("backend/.env", "r") as f:
    for line in f:
        if line.startswith("SUPABASE_URL="):
            os.environ["SUPABASE_URL"] = line.strip().split("=", 1)[1]
        elif line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
            os.environ["SUPABASE_SERVICE_ROLE_KEY"] = line.strip().split("=", 1)[1]

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
result = supabase.table("user_threads").insert({"user_id": "8a04745f-fcce-4a96-962b-4e394f5e286c", "title": "Test Insert"}).execute()
print(result.data)
