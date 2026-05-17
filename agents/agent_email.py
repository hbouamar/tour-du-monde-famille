import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google import genai
from agents.config import load_config


def _generate_html(program: dict) -> str:
    load_config()
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    prompt = f"""Rédige un email récapitulatif familial pour le programme culturel de la semaine.

Programme :
{json.dumps(program, ensure_ascii=False, indent=2)}

L'email doit :
- S'adresser à Alice (7 ans), Liam (12 ans) et leurs parents avec enthousiasme
- Présenter le pays de la semaine de façon accrocheuse
- Résumer chaque jour avec son thème et ses activités
- Terminer par un message d'encouragement
- Être en HTML simple compatible Gmail (pas de CSS externe)
- Utiliser des emojis 🌍

Réponds UNIQUEMENT avec le HTML (commence par <html>)."""

    return client.models.generate_content(model="gemini-2.0-flash", contents=prompt).text.strip()


def send_email(program: dict):
    gmail_user = os.environ["GMAIL_USER"]
    # Strip spaces/non-breaking spaces that Google inserts in displayed app passwords
    gmail_password = "".join(c for c in os.environ["GMAIL_APP_PASSWORD"] if c.isalnum())
    recipient = os.environ["EMAIL_RECIPIENT"]

    country = program.get("country", "le monde")
    week_start = program.get("week_start", "")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🌍 Cette semaine on voyage en {country} ! ({week_start})"
    msg["From"] = gmail_user
    msg["To"] = recipient

    msg.attach(MIMEText(_generate_html(program), "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipient, msg.as_string())

    print(f"Email envoyé à {recipient}")


if __name__ == "__main__":
    with open("data/current_program.json", encoding="utf-8") as f:
        program = json.load(f)
    send_email(program)
