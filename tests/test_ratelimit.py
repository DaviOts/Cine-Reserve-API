from unittest.mock import patch

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestMovieRateLimit:

    def test_list_within_limit_returns_200(self, api_client, movie):
        response = api_client.get(reverse('movie-list'))
        assert response.status_code == 200

    def test_list_exceeds_limit_returns_429(self, api_client, movie):
        for _ in range(60):
            api_client.get(reverse('movie-list'))
        response = api_client.get(reverse('movie-list'))
        assert response.status_code == 429
        assert 'error' in response.data

@pytest.mark.django_db
class TestSessionRateLimit:

    def test_list_within_limit_returns_200(self, api_client, session):
        response = api_client.get(reverse('session-list'))
        assert response.status_code == 200

    def test_list_exceeds_limit_returns_429(self, api_client, session):
        for _ in range(60):
            api_client.get(reverse('session-list'))
        response = api_client.get(reverse('session-list'))
        assert response.status_code == 429
        assert 'error' in response.data

    def test_filter_by_movie_exceeds_limit_returns_429(self, api_client, movie, session):
        url = f"{reverse('session-list')}?movie_id={movie.id}"
        for _ in range(60):
            api_client.get(url)
        response = api_client.get(url)
        assert response.status_code == 429

@pytest.mark.django_db
class TestUserRateLimit:

    def test_register_within_limit_returns_201(self, api_client):
        response = api_client.post(reverse('register'), {
            'username': 'novo',
            'email': 'novo@test.com',
            'password': 'strongpass123',
        })
        assert response.status_code == 201

    def test_register_exceeds_limit_returns_429(self, api_client):
        for i in range(5):
            api_client.post(reverse('register'), {
                'username': f'user{i}',
                'email': f'user{i}@test.com',
                'password': 'strongpass123',
            })
        response = api_client.post(reverse('register'), {
            'username': 'blocked',
            'email': 'blocked@test.com',
            'password': 'strongpass123',
        })
        assert response.status_code == 429


@pytest.mark.django_db
class TestReservationRateLimit:

    def test_reserve_exceeds_limit_returns_429(self, auth_client, session, seat):
        with patch('apps.reservations.views.ReservationService.acquire_seat_lock') as mock:
            mock.return_value = True
            url = reverse('reserve-seat', args=[session.id, seat.id])
            for _ in range(10):
                auth_client.post(url)
            response = auth_client.post(url)
            assert response.status_code == 429


@pytest.mark.django_db
class TestTicketRateLimit:

    def test_purchase_exceeds_limit_returns_429(self, auth_client, session, seat):
        with patch('apps.tickets.views.TicketService.create_ticket') as mock:
            mock.side_effect = ValueError('Seat is not available')
            for _ in range(5):
                auth_client.post(reverse('ticket-purchase'), {
                    'session_id': session.id,
                    'seat_id': seat.id,
                })
            response = auth_client.post(reverse('ticket-purchase'), {
                'session_id': session.id,
                'seat_id': seat.id,
            })
            assert response.status_code == 429

@pytest.mark.django_db
class TestSeatRateLimit:

    def test_list_within_limit_returns_200(self, auth_client, session, seat):
        url = reverse('seat-list', args=[session.id])
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_list_exceeds_limit_returns_429(self, auth_client, session, seat):
        url = reverse('seat-list', args=[session.id])
        for _ in range(30):
            auth_client.get(url)
        response = auth_client.get(url)
        assert response.status_code == 429
        assert 'error' in response.data