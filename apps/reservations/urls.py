from django.urls import path
from .views import ReserveSeatView

urlpatterns = [
    path('sessions/<int:session_id>/seats/<int:seat_id>/reserve/', ReserveSeatView.as_view(), name='reserve-seat'),
]