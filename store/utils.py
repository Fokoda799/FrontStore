# from django.conf import settings
from django.core.mail import send_mail


def send_email(subject, message, recipient_list):
    print("Email sending...")
    send_mail(
        subject=subject,
        message=message,
        from_email="feyt2003@gmail.com",
        recipient_list=recipient_list,
        fail_silently=False,
    )
    print("Email Sent!")
