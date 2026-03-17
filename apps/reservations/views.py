from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.seats.models import Seat, SeatStatus
from apps.reservations.services import ReservationService

class ReserveSeatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id, seat_id):
        seat = get_object_or_404(Seat, id=seat_id)

        if seat.status == SeatStatus.PURCHASED:
            return Response({"error": "Seat already purchased"}, status=status.HTTP_400_BAD_REQUEST)

        acquiered = ReservationService.acquire_seat_lock(seat_id, request.user.id)

        if not acquiered:
            ttl = ReservationService.get_lock_ttl(seat_id)

            return Response({"error": "Seat is being processed"}, status=status.HTTP_409_CONFLICT)

        return Response({"message": "Seat reserved"}, status=status.HTTP_200_OK)

    def delete(self, request, session_id, seat_id):
        realesed = ReservationService.release_seat_lock(seat_id, request.user.id)

        if not realesed:
            return Response({"error": "Failed to release seat lock"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Seat lock released"}, status=status.HTTP_200_OK)
        

        
            

        

        
        