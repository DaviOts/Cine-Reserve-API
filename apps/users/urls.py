from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

login_view = method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='post')(TokenObtainPairView)
register_view = method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')(RegisterView)

urlpatterns = [
    path('register/', register_view.as_view(), name='register'),

    path('login/', login_view.as_view(), name='login'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]