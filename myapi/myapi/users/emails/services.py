import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings



def send_reset_email(to_email, reset_link):
    print("SENDGRID SEND TRIGGERED")
    subject = "Password Reset Request"
    html_content = f"""
        <p>Hello,</p>
        <p>You requested to reset your password. Click the link below to continue:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p>If you didn't request this, you can ignore this email.</p>
        <br/>
        <p>Thanks,<br/> codewithshoaib </p>
    """

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        print(f"Failed to send email: {e}")