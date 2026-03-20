#use for a dependency injection
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer

User = get_user_model()

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

