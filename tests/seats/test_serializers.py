
import pytest

from apps.seats.models import Seat, SeatStatus
from apps.seats.serializers import SeatSerializer


@pytest.mark.django_db
class TestSeatSerializer:
 
    def test_serializes_correct_fields(self, seat):
        serializer = SeatSerializer(seat)
        data = serializer.data
        assert data['id'] == seat.id
        assert data['row'] == seat.row
        assert data['number'] == seat.number
        assert data['status'] == SeatStatus.AVAILABLE
        assert data['session'] == seat.session.id
 
    def test_default_status_is_available(self, session):
        seat = Seat.objects.create(session=session, row='Z', number=99)
        serializer = SeatSerializer(seat)
        assert serializer.data['status'] == SeatStatus.AVAILABLE
