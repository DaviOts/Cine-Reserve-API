from unittest.mock import patch

from apps.reservations.services import ReservationService


class TestReservationService:
 
    @patch('apps.reservations.services.redis_client')
    def test_acquire_lock_success(self, mock_redis):
        mock_redis.set.return_value = True
        result = ReservationService.acquire_seat_lock(seat_id=1, user_id=42)
        assert result is True
        mock_redis.set.assert_called_once_with('seat_lock:1', '42', ex=600, nx=True)
 
    @patch('apps.reservations.services.redis_client')
    def test_acquire_lock_fails_when_already_taken(self, mock_redis):
        mock_redis.set.return_value = None
        result = ReservationService.acquire_seat_lock(seat_id=1, user_id=99)
        assert result is False
 
    @patch('apps.reservations.services.redis_client')
    def test_release_lock_success_when_owner(self, mock_redis):
        mock_redis.get.return_value = '42'
        result = ReservationService.release_seat_lock(seat_id=1, user_id=42)
        mock_redis.delete.assert_called_once_with('seat_lock:1')
        assert result is True
 
    @patch('apps.reservations.services.redis_client')
    def test_release_lock_fails_when_not_owner(self, mock_redis):
        mock_redis.get.return_value = '42'
        result = ReservationService.release_seat_lock(seat_id=1, user_id=99)
        mock_redis.delete.assert_not_called()
        assert result is False
 
    @patch('apps.reservations.services.redis_client')
    def test_release_lock_fails_when_no_lock_exists(self, mock_redis):
        mock_redis.get.return_value = None
        result = ReservationService.release_seat_lock(seat_id=1, user_id=42)
        assert result is False
 
    @patch('apps.reservations.services.redis_client')
    def test_get_lock_ttl_returns_remaining_seconds(self, mock_redis):
        mock_redis.ttl.return_value = 350
        ttl = ReservationService.get_lock_ttl(seat_id=1)
        assert ttl == 350
        mock_redis.ttl.assert_called_once_with('seat_lock:1')
 
    @patch('apps.reservations.services.redis_client')
    def test_lock_key_format_is_correct(self, mock_redis):
        mock_redis.set.return_value = True
        ReservationService.acquire_seat_lock(seat_id=7, user_id=13)
        call_args = mock_redis.set.call_args
        assert call_args[0][0] == 'seat_lock:7'
        assert call_args[0][1] == '13'