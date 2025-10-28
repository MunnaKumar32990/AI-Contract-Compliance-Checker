import smtplib
from email.mime.text import MIMEText
import requests
import json
import os
from dotenv import load_dotenv  # <-- import dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch Slack Webhook URL from environment variables
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_email_notification(subject, notification):
    """Sends an email notification."""
    try:
        sender = "munnakushw7@gmail.com"
        password = "fdbp vbtp xkjn uqeh"
        receiver = "kmunna2482@gmail.com"

        msg = MIMEText(f"{notification}")
        msg["Subject"] = subject
        msg["From"] = f"Munna<{sender}>"
        msg["To"] = receiver

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print("✅ Email notification sent successfully!")

    except Exception as e:
        print(f"❌ Failed to send email notification: {e}")


def send_slack_notification(message):
    """Sends a notification to a Slack channel using a webhook."""
    try:
        if not SLACK_WEBHOOK_URL:
            print("⚠️ Slack webhook URL is not set. Skipping Slack notification.")
            return

        payload = {"text": message}
        headers = {"Content-Type": "application/json"}

        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        print("✅ Slack notification sent successfully!")

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send Slack notification: {e}")


def send_notification(subject, notification, send_to_email=True, send_to_slack=True):
    """Sends a notification to one or both platforms."""
    full_message = f"Subject: {subject}\n\n{notification}"

    if send_to_email:
        send_email_notification(subject, notification)
    if send_to_slack:
        send_slack_notification(full_message)
