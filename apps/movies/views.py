from django.core.cache import cache
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Movie, Session
from .serializers import MovieSerializer, SessionSerializer


#ModelViewSet do to get all crud operations
class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all().order_by('id')
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @method_decorator(ratelimit(key='ip', rate='60/m', method='GET', block=True))
    def list(self, request, *args, **kwargs):
        cache_key = f"movies:list:{request.user.id}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 60 * 15)
        return response
    
    @method_decorator(ratelimit(key='ip', rate='60/m', method='GET', block=True))
    def retrieve(self, request, *args, **kwargs):
        cache_key = f"movies:retrieve:{kwargs['pk']}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, 60 * 15)
        return response


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all().order_by('id')
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        movie_id = self.request.query_params.get('movie_id')
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        return queryset

    @method_decorator(ratelimit(key='ip', rate='60/m', method='GET', block=True))
    def list(self, request, *args, **kwargs):
        cache_key = f"sessions:list:{request.get_full_path()}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 60 * 15)
        return response
    
    @method_decorator(ratelimit(key='ip', rate='60/m', method='GET', block=True))
    def retrieve(self, request, *args, **kwargs):
        cache_key = f"sessions:retrieve:{request.user.id}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, 60 * 15)
        return response
