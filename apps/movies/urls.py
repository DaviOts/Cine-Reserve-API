from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MovieViewSet, SessionViewSet

router = DefaultRouter()

router.register(r'movies', MovieViewSet, basename='movie')
router.register(r'sessions', SessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
]
