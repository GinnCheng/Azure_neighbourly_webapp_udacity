import os
import json
import uuid
import datetime
import requests
import traceback

def publish_ad_created_event(ad_data: dict):
    print("👉 Entered publish_ad_created_event")

    try:
        endpoint = os.environ.get("EVENT_GRID_TOPIC_ENDPOINT")
        key = os.environ.get("EVENT_GRID_TOPIC_KEY")

        print(f"👉 endpoint: {endpoint}")
        print(f"👉 key: {'yes' if key else 'no'}")

        if not endpoint or not key:
            print("⚠️ Missing config — skipping")
            return

        event = [{
            "id": str(uuid.uuid4()),
            "eventType": "Neighbourly.AdCreated",
            "subject": "advertisements",
            "eventTime": datetime.datetime.utcnow().isoformat() + "Z",
            "data": ad_data,
            "dataVersion": "1.0"
        }]

        headers = {
            "Content-Type": "application/json",
            "aeg-sas-key": key
        }

        print("🚀 Sending POST to Event Grid...")
        resp = requests.post(
            endpoint,
            headers=headers,
            data=json.dumps(event),
            timeout=3
        )

        print(f"✅ Event POST response: {resp.status_code} {resp.text}")

        if resp.status_code >= 300:
            print(f"❌ Event Grid publish failed: {resp.status_code} {resp.text}")

    except Exception as e:
        print("❌ Exception in publish_ad_created_event:")
        traceback.print_exc()
