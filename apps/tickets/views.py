from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Ticket
from .serializers import TicketSerializer
from .services import TicketService


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class TicketViewSet(APIView):
    permission_classes = [IsAuthenticated]

    #tell swagger that need a form
    @extend_schema(
        request=inline_serializer(
            name ='TicketPurchaseRequest',
            fields ={
                'session_id': serializers.IntegerField(),
                'seat_id': serializers.IntegerField(),
            }
        ),
        responses={201: TicketSerializer}
    )

    def post(self, request):
        session_id = request.data.get('session_id')
        seat_id = request.data.get('seat_id')

        if not session_id or not seat_id:
            return Response({"error": "Session ID and Seat ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ticket = TicketService.create_ticket(request.user, session_id, seat_id)
            serializer = TicketSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(ratelimit(key='ip', rate='60/m', method='GET', block=True), name='list')
class MyTicketsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer
    
    #this filters tokens for the current user
    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).order_by('-purchased_at')
    
    
    
