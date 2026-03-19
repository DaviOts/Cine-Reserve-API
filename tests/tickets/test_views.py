from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.seats.models import Seat
from apps.tickets.models import Ticket
from apps.tickets.services import TicketService


@pytest.mark.django_db
class TestTicketPurchaseView:
 
    def test_requires_authentication(self, api_client, session, seat):
        response = api_client.post(reverse('ticket-purchase'), {
            'session_id': session.id,
            'seat_id': seat.id,
        })
        assert response.status_code == 401

    @patch('apps.tickets.views.TicketService.create_ticket')
    def test_purchase_returns_201_with_ticket_data(self, mock_create, auth_client, session, seat, user):
 
        fake_ticket = Ticket(user=user, session=session, seat=seat)
        mock_create.return_value = fake_ticket
 
        response = auth_client.post(reverse('ticket-purchase'), {
            'session_id': session.id,
            'seat_id': seat.id,
        })
        assert response.status_code == 201
 
    def test_purchase_missing_session_id_returns_400(self, auth_client, seat):
        response = auth_client.post(reverse('ticket-purchase'), {'seat_id': seat.id})
        assert response.status_code == 400
        assert 'error' in response.data
 
    def test_purchase_missing_seat_id_returns_400(self, auth_client, session):
        response = auth_client.post(reverse('ticket-purchase'), {'session_id': session.id})
        assert response.status_code == 400

    @patch('apps.tickets.views.TicketService.create_ticket')
    def test_purchase_raises_value_error_returns_400(self, mock_create, auth_client, session, seat):
        mock_create.side_effect = ValueError('Seat is not available')
 
        response = auth_client.post(reverse('ticket-purchase'), {
            'session_id': session.id,
            'seat_id': seat.id,
        })
        assert response.status_code == 400
        assert 'Seat is not available' in response.data['error']
 
    @patch('apps.tickets.views.TicketService.create_ticket')
    def test_purchase_unexpected_error_returns_500(self, mock_create, auth_client, session, seat):
        mock_create.side_effect = Exception('Unexpected DB failure')
 
        response = auth_client.post(reverse('ticket-purchase'), {
            'session_id': session.id,
            'seat_id': seat.id,
        })
        assert response.status_code == 500

@pytest.mark.django_db
class TestMyTicketsView:
 
    def test_requires_authentication(self, api_client):
        response = api_client.get(reverse('my-tickets'))
        assert response.status_code == 401
 
    @patch('apps.tickets.services.redis_client')
    def test_returns_only_current_user_tickets(self, mock_redis, auth_client, user, rival_user, session, seat, movie, db):
 
        mock_redis.get.return_value = str(user.id)
        TicketService.create_ticket(user, session.id, seat.id)
 
        seat_b = Seat.objects.create(session=session, row='C', number=5)
        mock_redis.get.return_value = str(rival_user.id)
        TicketService.create_ticket(rival_user, session.id, seat_b.id)
 
        response = auth_client.get(reverse('my-tickets'))
        assert response.status_code == 200
 
        ticket_ids = [t['user'] for t in response.data['results']]
        assert all(uid == user.id for uid in ticket_ids)
 
    def test_returns_empty_list_when_no_tickets(self, auth_client):
        response = auth_client.get(reverse('my-tickets'))
        assert response.status_code == 200
        assert response.data['results'] == []
 
    @patch('apps.tickets.services.redis_client')
    def test_response_contains_expected_fields(self, mock_redis, auth_client, user, session, seat):
        mock_redis.get.return_value = str(user.id)
        TicketService.create_ticket(user, session.id, seat.id)
 
        response = auth_client.get(reverse('my-tickets'))
        assert response.status_code == 200
 
        ticket = response.data['results'][0]
        assert 'id' in ticket
        assert 'seat' in ticket
        assert 'session' in ticket
        assert 'purchased_at' in ticket