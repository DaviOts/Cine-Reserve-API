import pytest
from apps.movies.models import Movie, Session
from apps.movies.serializers import MovieSerializer, SessionSerializer

@pytest.mark.django_db
class TestMovieSerializer:
 
    def test_serializes_all_fields(self, movie):
        serializer = MovieSerializer(movie)
        data = serializer.data
        assert data['id'] == movie.id
        assert data['title'] == movie.title
        assert data['genre'] == movie.genre
        assert data['duration_minutes'] == movie.duration_minutes
 
    def test_valid_data_creates_movie(self):
        data = {
            'title': 'Interstellar', 
            'description': 'the biggesttt movie, sickk',
            'duration_minutes': 169,
            'genre': 'Sci-Fi',
        }
        serializer = MovieSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
 
    def test_missing_required_fields_is_invalid(self):
        serializer = MovieSerializer(data={})
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

@pytest.mark.django_db
class TestSessionSerializer:
 
    def test_serializes_all_fields(self, session):
        serializer = SessionSerializer(session)
        data = serializer.data
        assert data['id'] == session.id
        assert data['room'] == session.room
        assert data['movie'] == session.movie.id
 
    def test_missing_required_fields_is_invalid(self):
        serializer = SessionSerializer(data={})
        assert not serializer.is_valid()