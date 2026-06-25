from email.message import EmailMessage
import aiosmtplib


async def send_contact_notification(
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    notification_email: str,
    client_name: str,
    client_email: str,
    client_message: str,
):
    if not smtp_username or not smtp_password or not notification_email:
        return

    email = EmailMessage()
    email["From"] = smtp_username
    email["To"] = notification_email
    email["Subject"] = f"New Website Request from {client_name}"

    email.set_content(
        f"""
New client request received.

Name: {client_name}
Email: {client_email}

Message:
{client_message}
"""
    )

    await aiosmtplib.send(
        email,
        hostname=smtp_host,
        port=smtp_port,
        start_tls=True,
        username=smtp_username,
        password=smtp_password,
    )