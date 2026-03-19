import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from apps.users.models import User
from apps.movies.models import Movie, Session
from apps.seats.models import Seat, SeatStatus
from model_bakery import baker


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
    return baker.make(
        User,
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
    return baker.make(
        Seat,
        session=session,
        row='A',
        number=1,
        status=SeatStatus.AVAILABLE,
    )
 
 
@pytest.fixture
def purchased_seat(db, session):
    return baker.make(
        Seat,
        session=session,
        row='B',
        number=1,
        status=SeatStatus.PURCHASED,
    )
 
 
@pytest.fixture
def seat_in_past_session(db, past_session):
    return baker.make(
        Seat,
        session=past_session,
        row='A',
        number=1,
        status=SeatStatus.AVAILABLE,
    )