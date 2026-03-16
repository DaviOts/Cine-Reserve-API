from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SeatViewSet

router = DefaultRouter()

router.register(r'seats', SeatViewSet, basename='seat')

urlpatterns = [
    path('', include(router.urls)),
]