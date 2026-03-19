from django.db import models

from apps.movies.models import Session


#this represents the status of a seat
class SeatStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    RESERVED = 'reserved', 'Reserved'
    PURCHASED = 'purchased', 'Purchased'

class Seat(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='seats')
    row = models.CharField(max_length=10)
    number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=SeatStatus.choices, default=SeatStatus.AVAILABLE)

    
    class Meta:
        #create a command "ADD CONSTRAINT UNIQUE"
        #number and row must be unique together for a session
        unique_together = ('session', 'row', 'number')

        #improve performance for queries that filter by session and status
        indexes = [
            models.Index(fields=['session', 'status'])
        ]
    
