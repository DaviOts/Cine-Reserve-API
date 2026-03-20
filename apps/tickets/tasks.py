from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_ticket_email(email, ticket_id, username ):
    send_mail(
        subject='Your Ticket',
        message=f'Hey {username}, your ticket has been confirmed\n\nTicket ID: {ticket_id}\n\n Let\'s go to the moviesss',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )

