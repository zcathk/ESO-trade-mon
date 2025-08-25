import smtplib,os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Convert Last seen text e.g. "9 hours ago" to minutes
# ==============================
def time_ago_to_minutes(text: str) -> int:
    text = text.lower().replace("ago", "").strip()
    parts = text.split()
    if len(parts) < 2:
        raise ValueError("Invalid time string format")
    value = int(parts[0])
    unit = parts[1]
    if unit.startswith("min"):
        return value
    elif unit.startswith("hour"):
        return value * 60
    elif unit.startswith("day"):
        return value * 24 * 60
    elif unit.startswith("sec"):
        return max(1, value // 60)  # round seconds to 1 minute
    else:
        raise ValueError(f"Unknown unit: {unit}")
# Send email notification.
# ==============================
def sendnoti(subject,content,from_email,from_emailcredential,to_email):
    msg = MIMEMultipart()
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(content, "plain"))    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_email, from_emailcredential)
        server.sendmail(from_email, msg["To"], msg.as_string())
    