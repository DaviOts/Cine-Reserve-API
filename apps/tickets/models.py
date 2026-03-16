from django.db import models
from apps.users.models import User
from apps.seats.models import Seat
from apps.movies.models import Session
import uuid

class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    #use protect in seat and session to avoid delete them if they are used in a ticket
    seat = models.OneToOneField(Seat, on_delete=models.PROTECT, related_name='tickets')
    #so important to "My Tickets" portal
    session = models.ForeignKey(Session, on_delete=models.PROTECT, related_name='tickets')
    purchased_at = models.DateTimeField(auto_now_add=True)
    #unique digital ticket
    qr_code = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'purchased_at']),
            models.Index(fields=['seat']),
        ]
