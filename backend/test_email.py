from alert_engine import send_email_alert

result = send_email_alert(
    text        = "Test alert from SafeVoice",
    platform    = "test",
    severity    = 3,
    incident_id = 0
)

if result:
    print("Email sent successfully!")
else:
    print("Email failed — check your .env values")