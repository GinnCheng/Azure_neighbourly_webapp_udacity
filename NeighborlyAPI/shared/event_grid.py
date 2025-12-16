import os
import json
import uuid
import datetime
import requests


def publish_ad_created_event(ad_data: dict):
    endpoint = os.environ.get("EVENT_GRID_TOPIC_ENDPOINT")
    key = os.environ.get("EVENT_GRID_TOPIC_KEY")

    if not endpoint or not key:
        # 没配置就静默跳过，避免影响主流程
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

    resp = requests.post(
        endpoint,
        headers=headers,
        data=json.dumps(event),
        timeout=10
    )

    # 可选：调试用
    if resp.status_code >= 300:
        raise Exception(f"Event Grid publish failed: {resp.text}")
