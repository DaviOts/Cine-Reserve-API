from unittest.mock import patch

import pytest

from apps.reservations.tasks import release_expired_seat_locks
from apps.seats.models import Seat, SeatStatus


@pytest.mark.django_db
class TestReleaseExpiredSeatLocks:

    @patch('apps.reservations.tasks.redis_client')
    def test_releases_seat_when_lock_expired(self, mock_redis, session):
        seat = Seat.objects.create(
            session=session, row='A', number=1, status=SeatStatus.RESERVED
        )
        mock_redis.exists.return_value = False

        result = release_expired_seat_locks()

        seat.refresh_from_db()
        assert seat.status == SeatStatus.AVAILABLE
        assert result == "Released 1 expired seat locks"

    @patch('apps.reservations.tasks.redis_client')
    def test_keeps_seat_reserved_when_lock_active(self, mock_redis, session):
        seat = Seat.objects.create(
            session=session, row='A', number=2, status=SeatStatus.RESERVED
        )
        mock_redis.exists.return_value = True

        release_expired_seat_locks()

        seat.refresh_from_db()
        assert seat.status == SeatStatus.RESERVED

    @patch('apps.reservations.tasks.redis_client')
    def test_ignores_purchased_seats(self, mock_redis, session, purchased_seat):
        mock_redis.exists.return_value = False

        release_expired_seat_locks()

        purchased_seat.refresh_from_db()
        assert purchased_seat.status == SeatStatus.PURCHASED

    @patch('apps.reservations.tasks.redis_client')
    def test_returns_correct_count(self, mock_redis, session):
        for i in range(3):
            Seat.objects.create(
                session=session, row='B', number=i + 1, status=SeatStatus.RESERVED
            )
        mock_redis.exists.return_value = False

        result = release_expired_seat_locks()

        assert result == "Released 3 expired seat locks"