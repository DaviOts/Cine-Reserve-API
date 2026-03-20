from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.seats.models import Seat

from .models import Session


@receiver(post_save, sender=Session)
def create_seats_for_session(sender, instance, created, **kwargs):
    if not created:
        return

    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    seats_per_row = instance.total_seats // len(rows)

    seats = [
        Seat(session=instance, row=row, number=number)
        for row in rows
        for number in range(1, seats_per_row + 1)
    ]
    Seat.objects.bulk_create(seats)