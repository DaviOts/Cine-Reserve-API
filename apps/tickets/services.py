import redis
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.movies.models import Session
from apps.reservations.services import ReservationService
from apps.seats.models import Seat, SeatStatus

from .models import Ticket

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


class TicketService:
    @staticmethod
    def create_ticket(user, session_id, seat_id):
        #deal with race condition
        with transaction.atomic():
            #add redis lock
            lock_key = f"seat_lock:{seat_id}"

            lock_owner = redis_client.get(lock_key)

            if lock_owner and lock_owner != str(user.id):
                raise ValueError("Seat is not available")
                
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
            
            #realease if and only if transaction is committed in my bd
            transaction.on_commit(lambda: ReservationService.release_seat_lock(seat_id, user.id))
            
            return ticket