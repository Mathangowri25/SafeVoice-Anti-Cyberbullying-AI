import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

THRESHOLD    = int(os.getenv("ALERT_SEVERITY_THRESHOLD", 2))
ALERT_EMAIL  = os.getenv("ALERT_EMAIL", "")        # guardian email
SMTP_USER    = os.getenv("SMTP_USER", "")
SMTP_PASS    = os.getenv("SMTP_PASS", "")
SMTP_HOST    = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT    = int(os.getenv("SMTP_PORT", 587))

SEVERITY_LABELS = {
    0: "Safe",
    1: "Mild toxic",
    2: "Hate speech",
    3: "Severe — immediate action needed"
}

def send_email_alert(text: str, platform: str,
                     severity: int, incident_id: int) -> bool:
    if not ALERT_EMAIL or not SMTP_USER:
        print("Email alert skipped — SMTP not configured")
        return False
    try:
        subject = f"SafeVoice Alert — {SEVERITY_LABELS[severity]} detected"
        body = f"""
SafeVoice has detected toxic content.

Severity  : {severity}/3 — {SEVERITY_LABELS[severity]}
Platform  : {platform}
Incident  : #{incident_id}
Content   : {text[:200]}

Please review this immediately in the SafeVoice dashboard.
        """
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"]    = SMTP_USER
        msg["To"]      = ALERT_EMAIL

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, ALERT_EMAIL, msg.as_string())

        print(f"Email alert sent for incident #{incident_id}")
        return True
    except Exception as e:
        print(f"Email alert failed: {e}")
        return False

def send_alert_if_needed(severity: int, text: str,
                          platform: str, incident_id: int) -> bool:
    if severity >= THRESHOLD:
        return send_email_alert(text, platform, severity, incident_id)
    return False