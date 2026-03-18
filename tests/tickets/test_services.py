import pytest
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta
from apps.tickets.models import Ticket
from apps.seats.models import SeatStatus
from apps.tickets.services import TicketService
from apps.movies.models import Session
from apps.seats.models import Seat
from apps.reservations.services import ReservationService
import uuid


@pytest.mark.django_db
class TestTicketService:
    
    @patch('apps.tickets.services.redis_client')
    @patch('apps.tickets.services.ReservationService.release_seat_lock')
    def test_create_ticket_success(self, mock_release, mock_redis, user, session, seat):
        mock_redis.get.return_value = str(user.id)
 
        ticket = TicketService.create_ticket(user, session.id, seat.id)
 
        assert ticket is not None
        assert ticket.user == user
        assert ticket.session == session
        assert ticket.seat == seat
    
    @patch('apps.tickets.services.redis_client')
    def test_create_ticket_changes_seat_status_to_purchased(self, mock_redis, user, session, seat):
        mock_redis.get.return_value = str(user.id)
 
        TicketService.create_ticket(user, session.id, seat.id)
 
        seat.refresh_from_db()
        assert seat.status == SeatStatus.PURCHASED
    
    @patch('apps.tickets.services.redis_client')
    def test_create_ticket_fails_when_seat_already_purchased(self, mock_redis, user, session, purchased_seat):
        mock_redis.get.return_value = str(user.id)
 
        with pytest.raises(ValueError, match='not available'):
            TicketService.create_ticket(user, session.id, purchased_seat.id)
    
    @patch('apps.tickets.services.redis_client')
    def test_create_ticket_fails_for_past_session(self, mock_redis, user, past_session, seat_in_past_session):
        mock_redis.get.return_value = str(user.id)
 
        with pytest.raises(ValueError, match='already started'):
            TicketService.create_ticket(user, past_session.id, seat_in_past_session.id)
    
    @patch('apps.tickets.services.redis_client')
    def test_create_ticket_fails_when_seat_not_in_session(self, mock_redis, user, session, movie, db):
 
        other_session = Session.objects.create(
            movie=movie,
            room='Sala X',
            starts_at=timezone.now() + timedelta(hours=3),
            total_seats=10,
        )
        other_seat = Seat.objects.create(session=other_session, row='A', number=5)
 
        mock_redis.get.return_value = str(user.id)
 
        with pytest.raises(ValueError, match='not in the session'):
            TicketService.create_ticket(user, session.id, other_seat.id)
    
    @patch('apps.tickets.services.redis_client')
    def test_create_ticket_fails_when_lock_belongs_to_other_user(self, mock_redis, user, rival_user, session, seat):
 
        mock_redis.get.return_value = str(rival_user.id)
 
        with pytest.raises(ValueError, match='not available'):
            TicketService.create_ticket(user, session.id, seat.id)
 
    def test_create_ticket_fails_for_nonexistent_session(self, user, seat):
 
        with pytest.raises(ValueError, match='Session not found'):
            TicketService.create_ticket(user, 99999, seat.id)
 
    def test_create_ticket_fails_for_nonexistent_seat(self, user, session):
 
        with pytest.raises(ValueError, match='Seat not found'):
            TicketService.create_ticket(user, session.id, 99999)
    
    @patch('apps.tickets.services.redis_client')
    def test_ticket_has_uuid_primary_key(self, mock_redis, user, session, seat):
 
        mock_redis.get.return_value = str(user.id)
 
        ticket = TicketService.create_ticket(user, session.id, seat.id)
 
        assert isinstance(ticket.id, uuid.UUID)

    @pytest.mark.django_db(transaction=True)
    @patch('apps.tickets.services.redis_client')
    @patch('apps.tickets.services.ReservationService.release_seat_lock')
    def test_redis_lock_released_after_successful_checkout(self, mock_release, mock_redis, user, session, seat):
 
        mock_redis.get.return_value = str(user.id)
 
        TicketService.create_ticket(user, session.id, seat.id)
 
        mock_release.assert_called_once_with(seat.id, user.id)

        
        
        
        
        

