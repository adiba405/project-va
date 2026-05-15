import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    """Send password reset email via SMTP.

    Required env vars:
      SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM

    Optional:
      SMTP_USE_TLS (default: true)
      SMTP_SUBJECT_PREFIX (default: "AI-Study Assistant")
    """
    smtp_host = os.getenv('SMTP_HOST', '').strip()
    smtp_port = int(os.getenv('SMTP_PORT', '587').strip() or '587')
    smtp_username = os.getenv('SMTP_USERNAME', '').strip()
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    smtp_from = os.getenv('SMTP_FROM', '').strip()

    if not smtp_host or not smtp_username or not smtp_from:
        raise RuntimeError('SMTP is not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM')

    use_tls = os.getenv('SMTP_USE_TLS', 'true').strip().lower() in {'1', 'true', 'yes', 'y'}
    subject_prefix = os.getenv('SMTP_SUBJECT_PREFIX', 'AI-Study Assistant').strip() or 'AI-Study Assistant'

    subject = f"{subject_prefix} - Password Reset"

    html_body = f"""
    <div style='font-family: Arial, sans-serif; line-height: 1.5;'>
      <p>We received a request to reset your password.</p>
      <p><strong>Click the link below to reset your password:</strong></p>
      <p><a href='{reset_link}'>{reset_link}</a></p>
      <p>This link will expire shortly. If you did not request a password reset, please ignore this email.</p>
    </div>
    """

    text_body = (
        "We received a request to reset your password.\n\n"
        f"Reset link: {reset_link}\n\n"
        "This link will expire shortly. If you did not request a password reset, please ignore this email."
    )

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = smtp_from
    msg['To'] = to_email
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
    try:
        if use_tls:
            server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_from, [to_email], msg.as_string())
    finally:
        try:
            server.quit()
        except Exception:
            pass

