import httpx
import json

response = httpx.get("http://localhost:8000/openapi.json")
data = response.json()

# Find admin endpoints
admin_paths = {k: v for k, v in data.get("paths", {}).items() if "admin" in k}

if admin_paths:
    print("Admin endpoints found:")
    for path in admin_paths:
        print(f"  {path}")
        print(json.dumps(admin_paths[path], indent=2)[:500])
else:
    print("No admin endpoints found!")
    print("\nAll paths:")
    for path in data.get("paths", {}).keys():
        print(f"  {path}")
