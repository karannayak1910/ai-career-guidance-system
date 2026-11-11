"""
Check live Render deployment status and build progress.
"""
import sys
import json
import time
import urllib.request

API_KEY = "rnd_6nDTCwx4FJ55EReNLXAKMINrZk9x"
SERVICE_NAME = "ai-career-guidance-system"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 1. Get Service ID
req = urllib.request.Request("https://api.render.com/v1/services?name=" + SERVICE_NAME, headers=headers)
with urllib.request.urlopen(req) as res:
    data = json.loads(res.read().decode())
    svc = data[0]["service"]
    service_id = svc["id"]
    service_url = svc["serviceDetails"]["url"]
    print(f"Service ID: {service_id}")
    print(f"Live URL:   {service_url}")

# 2. Get latest deploy
req_dep = urllib.request.Request(f"https://api.render.com/v1/services/{service_id}/deploys?limit=1", headers=headers)
with urllib.request.urlopen(req_dep) as res:
    deploys = json.loads(res.read().decode())
    if deploys:
        dep = deploys[0]["deploy"]
        print(f"Deploy ID:     {dep['id']}")
        print(f"Deploy Status: {dep['status']}")
        print(f"Created At:    {dep['createdAt']}")
        print(f"Updated At:    {dep['updatedAt']}")
