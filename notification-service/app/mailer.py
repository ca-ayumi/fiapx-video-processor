import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_email_notification(to_email: str, filename: str):
    print(f"[→] Tentando enviar e-mail para {to_email} sobre '{filename}'")

    msg = EmailMessage()
    msg["Subject"] = "Seu vídeo foi processado com sucesso!"
    msg["From"] = SMTP_USERNAME
    msg["To"] = to_email
    msg.set_content(f"O vídeo '{filename}' foi processado com sucesso e está pronto para download.")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(msg)
            print(f"[✓] E-mail enviado para {to_email}")
    except Exception as e:
        print(f"[X] Erro ao enviar e-mail para {to_email}: {e}")
