from django.urls import path

from .views import SeatViewSet

urlpatterns = [
    path('sessions/<int:session_id>/seats/', SeatViewSet.as_view(), name='seat-list'),
]