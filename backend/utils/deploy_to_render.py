"""
Render.com Automated API Deployment Utility.
Deploys the AI Career Guidance System to Render via the official Render REST API.
"""
import sys
import json
import urllib.request
import urllib.error

REPO_URL = "https://github.com/karannayak1910/ai-career-guidance-system"
SERVICE_NAME = "ai-career-guidance-system"

def deploy_service(api_key: str):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key.strip()}"
    }

    # 1. Fetch Owner ID
    print("[1/3] Fetching Render account owner ID...")
    try:
        req_owners = urllib.request.Request("https://api.render.com/v1/owners", headers=headers)
        with urllib.request.urlopen(req_owners) as res:
            owners_data = json.loads(res.read().decode())
            if not owners_data:
                print("[ERROR] No workspaces/owners found for this Render account.")
                return False
            owner_id = owners_data[0]["owner"]["id"]
            owner_name = owners_data[0]["owner"].get("name", "User")
            print(f"[SUCCESS] Authenticated as '{owner_name}' (ID: {owner_id})")
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Invalid API Key ({e.code}): {e.read().decode()}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to query Render owners: {e}")
        return False

    # 2. Check if service already exists
    print(f"[2/3] Checking if '{SERVICE_NAME}' exists on Render...")
    try:
        req_list = urllib.request.Request(f"https://api.render.com/v1/services?name={SERVICE_NAME}", headers=headers)
        with urllib.request.urlopen(req_list) as res:
            existing_services = json.loads(res.read().decode())
            for item in existing_services:
                svc = item.get("service", {})
                if svc.get("name") == SERVICE_NAME:
                    service_id = svc.get("id")
                    service_url = svc.get("serviceDetails", {}).get("url")
                    print(f"[INFO] Service already exists! (ID: {service_id})")
                    print(f"Triggering manual redeploy for {service_id}...")
                    req_deploy = urllib.request.Request(f"https://api.render.com/v1/services/{service_id}/deploys", data=b"{}", headers=headers)
                    with urllib.request.urlopen(req_deploy) as dep_res:
                        print("[SUCCESS] Redeploy triggered successfully!")
                    print(f"\n=======================================================")
                    print(f"🌟 LIVE RENDER URL: {service_url}")
                    print(f"=======================================================\n")
                    return True
    except Exception as e:
        print(f"[WARN] List check: {e}")

    # 3. Create Web Service
    print(f"[3/3] Creating new web service on Render...")
    payload = {
        "type": "web_service",
        "name": SERVICE_NAME,
        "ownerId": owner_id,
        "repo": REPO_URL,
        "branch": "main",
        "autoDeploy": "yes",
        "serviceDetails": {
            "env": "python",
            "region": "oregon",
            "plan": "free",
            "envSpecificDetails": {
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "gunicorn run:app --workers 2 --threads 4 --timeout 120"
            }
        }
    }

    try:
        req_create = urllib.request.Request("https://api.render.com/v1/services", data=json.dumps(payload).encode(), headers=headers)
        with urllib.request.urlopen(req_create) as res:
            svc_res = json.loads(res.read().decode())
            service = svc_res.get("service", svc_res)
            service_url = service.get("serviceDetails", {}).get("url") or f"https://{SERVICE_NAME}.onrender.com"
            print("\n" + "=" * 65)
            print("🎉 RENDER SERVICE CREATED SUCCESSFULLY!")
            print(f"🌟 LIVE URL: {service_url}")
            print("=" * 65 + "\n")
            return True
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Service creation failed ({e.code}): {e.read().decode()}")
        return False
    except Exception as e:
        print(f"[ERROR] Exception during service creation: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        deploy_service(sys.argv[1])
    else:
        print("Usage: python backend/utils/deploy_to_render.py <RENDER_API_KEY>")
