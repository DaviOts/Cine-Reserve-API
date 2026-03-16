from .models import Ticket
from django.utils import timezone
from django.db import transaction
from apps.movies.models import Session
from apps.seats.models import Seat, SeatStatus


class TicketService:
    @staticmethod
    def create_ticket(user, session_id, seat_id):
        #deal with race condition
        with transaction.atomic():
            try:
                session = Session.objects.get(id=session_id)
            except Session.DoesNotExist:
                raise ValueError("Session not found")

            try:
                #freeze seat until checkout
                seat = Seat.objects.select_for_update().get(id=seat_id)
            except Seat.DoesNotExist:
                raise ValueError("Seat not found")

            if session.starts_at < timezone.now():
                raise ValueError("Session has already started")
            
            if seat.session.id != session_id:
                raise ValueError("Seat is not in the session")
            
            if seat.status != SeatStatus.AVAILABLE:
                raise ValueError("Seat is not available")
            
            seat.status = SeatStatus.PURCHASED
            seat.save()
            
            ticket = Ticket.objects.create(
                user=user,
                session=session,
                seat=seat,
            )
            
            return ticket