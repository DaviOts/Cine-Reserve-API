import redis
from celery import shared_task
from django.conf import settings

from apps.seats.models import Seat, SeatStatus

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


@shared_task
def release_expired_seat_locks():
    reserved_seats = Seat.objects.filter(status=SeatStatus.RESERVED)

    released = 0
    for seat in reserved_seats:
        lock_key = f"seat_lock:{seat.id}"
        if not redis_client.exists(lock_key):
            seat.status = SeatStatus.AVAILABLE
            seat.save()
            released += 1

    return f"Released {released} expired seat locks"