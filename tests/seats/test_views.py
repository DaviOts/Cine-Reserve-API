from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.movies.models import Session
from apps.seats.models import Seat, SeatStatus


@pytest.mark.django_db
class TestSeatMapView:
 
    def test_requires_authentication(self, api_client, session):
        response = api_client.get(reverse('seat-list', args=[session.id]))
        assert response.status_code == 401
 
    def test_returns_seats_for_session(self, auth_client, session, seat):
        response = auth_client.get(reverse('seat-list', args=[session.id]))
        assert response.status_code == 200
        assert len(response.data['results']) >= 1
 
    def test_returns_only_seats_of_the_session(self, auth_client, session, seat, movie, db):
        other_session = Session.objects.create(
            movie=movie,
            room='room 99',
            starts_at=timezone.now() + timedelta(hours=5),
            total_seats=10,
        )
        Seat.objects.create(session=other_session, row='X', number=1)
 
        response = auth_client.get(reverse('seat-list', args=[session.id]))
        seat_ids = [s['id'] for s in response.data['results']]
        assert seat.id in seat_ids
        other_seats = Seat.objects.filter(session=other_session)
        for other in other_seats:
            assert other.id not in seat_ids
 
    def test_available_seat_without_redis_lock_shows_available(self, auth_client, session, seat):
        with patch('apps.seats.views.redis_client') as mock_redis:
            mock_redis.exists.return_value = False
            response = auth_client.get(reverse('seat-list', args=[session.id]))
            assert response.status_code == 200
            seat_data = next(s for s in response.data['results'] if s['id'] == seat.id)
            assert seat_data['status'] == SeatStatus.AVAILABLE
 
    def test_available_seat_with_redis_lock_shows_reserved(self, auth_client, session, seat):
        with patch('apps.seats.views.redis_client') as mock_redis:
            mock_redis.exists.return_value = True
            response = auth_client.get(reverse('seat-list', args=[session.id]))
            assert response.status_code == 200
            seat_data = next(s for s in response.data['results'] if s['id'] == seat.id)
            assert seat_data['status'] == SeatStatus.RESERVED
 
    def test_purchased_seat_stays_purchased_regardless_of_redis(self, auth_client, session, purchased_seat):
        with patch('apps.seats.views.redis_client') as mock_redis:
            mock_redis.exists.return_value = True
            response = auth_client.get(reverse('seat-list', args=[session.id]))
            seat_data = next(s for s in response.data['results'] if s['id'] == purchased_seat.id)
            assert seat_data['status'] == SeatStatus.PURCHASED
 
    def test_empty_session_returns_empty_list(self, auth_client, movie, db):
 
        empty_session = Session.objects.create(
            movie=movie,
            room='empty room',
            starts_at=timezone.now() + timedelta(hours=3),
            total_seats=0,
        )
        response = auth_client.get(reverse('seat-list', args=[empty_session.id]))
        assert response.status_code == 200
        assert response.data['results'] == []