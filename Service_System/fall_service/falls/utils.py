import requests
from django.conf import settings


def send_fcm_notification(token, title, body):
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Authorization": f"key={settings.FCM_SERVER_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "to": token,
        "notification": {"title": title, "body": body},
    }
    requests.post(url, json=data, headers=headers, timeout=3)
