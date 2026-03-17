import redis
from django.conf import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)

LOCK_TIMEOUT = 600

class ReservationService:
    @staticmethod
    def acquire_seat_lock(seat_id, user_id) -> bool:
        lock_key = f"seat_lock:{seat_id}"

        lock_owner = str(user_id)

        result = redis_client.set(lock_key, lock_owner, ex=LOCK_TIMEOUT, nx=True)

        return result is not None

    @staticmethod
    def release_seat_lock(seat_id, user_id) -> bool:
        lock_key = f"seat_lock:{seat_id}"

        current_owner = redis_client.get(lock_key)

        if current_owner == str(user_id):
            redis_client.delete(lock_key)
            return True
        return False
        
    @staticmethod
    def get_lock_ttl(seat_id) -> int:
        return redis_client.ttl(f"seat_lock:{seat_id}")


        
        
        
        
