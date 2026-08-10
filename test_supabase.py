from services.supabase_service import supabase


response = (
    supabase
    .table("documents")
    .select("*")
    .limit(1)
    .execute()
)


print("Supabase connection successful!")
print("Documents:", response.data)