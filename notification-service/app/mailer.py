import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_email_notification(to_email: str, filename: str, error_message: str = None):
    msg = EmailMessage()
    msg["From"] = SMTP_USERNAME
    msg["To"] = to_email

    if error_message:
        msg["Subject"] = "Erro ao processar seu vídeo 😔"
        msg.set_content(
            f"Houve uma falha ao processar o vídeo '{filename}'.\n\nMotivo: {error_message}\n\nPor favor, verifique o arquivo e tente novamente."
        )
    else:
        msg["Subject"] = "✅ Seu vídeo foi processado com sucesso!"
        msg.set_content(
            f"O vídeo '{filename}' foi processado com sucesso e está pronto para download!"
        )

    print(f"[→] Tentando enviar e-mail para {to_email} sobre '{filename}'")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(msg)
        print(f"[✓] E-mail enviado para {to_email}")
    except Exception as e:
        print(f"[X] Erro ao enviar e-mail para {to_email}: {e}")
