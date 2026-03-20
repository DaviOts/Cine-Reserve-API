import redis
from django.conf import settings
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Seat, SeatStatus
from .serializers import SeatSerializer

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

@method_decorator(ratelimit(key='ip', rate='30/m', method='GET', block=True), name='get')
class SeatViewSet(generics.ListAPIView):
    
    serializer_class = SeatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        #get session id from url
        session_id = self.kwargs.get('session_id')

        #get in my bd all seats from this session
        seats = Seat.objects.filter(session_id=session_id).order_by('row', 'number')

        for seat in seats:
            if seat.status == SeatStatus.AVAILABLE:
                lock_key = f"seat_lock:{seat.id}"
                #transient state, not persisted, only for concurrency control
                if redis_client.exists(lock_key):
                    seat.status = SeatStatus.RESERVED
            
        return seats
                
        
        

