import pytest
from unittest.mock import patch, MagicMock
from apps.reservations.services import ReservationService
from apps.seats.models import SeatStatus
from django.urls import reverse


@pytest.mark.django_db
class TestReserveSeatView:
 
    def test_requires_authentication(self, api_client, session, seat):
        url = reverse('reserve-seat', args=[session.id, seat.id])
        response = api_client.post(url)
        assert response.status_code == 401
 
    @patch('apps.reservations.views.ReservationService.acquire_seat_lock')
    def test_reserve_available_seat_returns_200(self, mock_acquire, auth_client, session, seat):
        mock_acquire.return_value = True
        url = reverse('reserve-seat', args=[session.id, seat.id])
        response = auth_client.post(url)
        assert response.status_code == 200
        assert response.data['message'] == 'Seat reserved'
 
    @patch('apps.reservations.views.ReservationService.acquire_seat_lock')
    @patch('apps.reservations.views.ReservationService.get_lock_ttl')
    def test_reserve_locked_seat_returns_409(self, mock_ttl, mock_acquire, auth_client, session, seat):
        mock_acquire.return_value = False
        mock_ttl.return_value = 300
        url = reverse('reserve-seat', args=[session.id, seat.id])
        response = auth_client.post(url)
        assert response.status_code == 409
        assert 'error' in response.data
 
    def test_reserve_purchased_seat_returns_400(self, auth_client, session, purchased_seat):
        url = reverse('reserve-seat', args=[session.id, purchased_seat.id])
        response = auth_client.post(url)
        assert response.status_code == 400
        assert 'already purchased' in response.data['error'].lower()
 
    def test_reserve_nonexistent_seat_returns_404(self, auth_client, session):
        url = reverse('reserve-seat', args=[session.id, 99999])
        response = auth_client.post(url)
        assert response.status_code == 404
 
    @patch('apps.reservations.views.ReservationService.release_seat_lock')
    def test_delete_releases_lock_successfully(self, mock_release, auth_client, session, seat):
        mock_release.return_value = True
        url = reverse('reserve-seat', args=[session.id, seat.id])
        response = auth_client.delete(url)
        assert response.status_code == 200
        assert response.data['message'] == 'Seat lock released'
 
    @patch('apps.reservations.views.ReservationService.release_seat_lock')
    def test_delete_fails_when_not_owner_returns_400(self, mock_release, auth_client, session, seat):
        mock_release.return_value = False
        url = reverse('reserve-seat', args=[session.id, seat.id])
        response = auth_client.delete(url)
        assert response.status_code == 400
 
    @patch('apps.reservations.views.ReservationService.acquire_seat_lock')
    def test_two_users_cannot_reserve_same_seat(
        self, mock_acquire, auth_client, auth_client_b, session, seat
    ):
        mock_acquire.side_effect = [True, False]
 
        url = reverse('reserve-seat', args=[session.id, seat.id])
 
        response_a = auth_client.post(url)
        response_b = auth_client_b.post(url)
 
        assert response_a.status_code == 200
        assert response_b.status_code == 409