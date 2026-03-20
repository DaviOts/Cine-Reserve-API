from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone
from model_bakery import baker
from rest_framework.test import APIClient

from apps.movies.models import Movie, Session
from apps.seats.models import Seat, SeatStatus
from apps.users.models import User


#client
@pytest.fixture
def api_client():
    return APIClient()
 
 
@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client
 
 
@pytest.fixture
def auth_client_b(api_client, rival_user):
    client = APIClient()
    client.force_authenticate(user=rival_user)
    return client


#users
@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='daviots',
        email='davi@test.com',
        password='strongpass123',
    )
 
 
@pytest.fixture
def rival_user(db):
    return User.objects.create_user(
        username='idkuser',
        email='idkuser@test.com',
        password='strongpass123',
    )

#movies and sessions
@pytest.fixture
def movie(db):
    return baker.make(
        Movie,
        title='Interstellar',
        description='Space odyssey',
        duration_minutes=169,
        genre='Sci-Fi',
    )
 
 
@pytest.fixture
def session(db, movie):
    return baker.make(
        Session,
        movie=movie,
        room='Sala 1',
        starts_at=timezone.now() + timedelta(hours=2),
        total_seats=50,
    )
 
 
@pytest.fixture
def past_session(db, movie):
    return baker.make(
        Session,
        movie=movie,
        room='Sala 2',
        starts_at=timezone.now() - timedelta(hours=1),
        total_seats=50,
    )

#seats
@pytest.fixture
def seat(db, session):
    return Seat.objects.filter(
        session=session,
        status=SeatStatus.AVAILABLE,
    ).first()
 
 
@pytest.fixture
def purchased_seat(db, session):
    s = Seat.objects.filter(
        session=session,
        )[1]
    s.status = SeatStatus.PURCHASED
    s.save()
    return s
 
 
@pytest.fixture
def seat_in_past_session(db, past_session):
    return Seat.objects.filter(
        session=past_session,
        status=SeatStatus.AVAILABLE,
    ).first()

#cache(clears before and after each test)
@pytest.fixture(autouse=True)
def reset_cache():
    cache.clear()
    yield
    cache.clear()