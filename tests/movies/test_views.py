import pytest
from apps.movies.models import Movie, Session
from django.urls import reverse

@pytest.mark.django_db
class TestMovieViewSet:
 
    def test_list_movies_is_public(self, api_client, movie):
        response = api_client.get(reverse('movie-list'))
        assert response.status_code == 200
 
    def test_list_returns_paginated_results(self, api_client, movie):
        response = api_client.get(reverse('movie-list'))
        assert 'results' in response.data
        assert len(response.data['results']) >= 1
 
    def test_retrieve_movie_is_public(self, api_client, movie):
        response = api_client.get(reverse('movie-detail', args=[movie.id]))
        assert response.status_code == 200
        assert response.data['title'] == movie.title
 
    def test_retrieve_nonexistent_movie_returns_404(self, api_client):
        response = api_client.get(reverse('movie-detail', args=[99999]))
        assert response.status_code == 404
 
    def test_create_movie_requires_auth(self, api_client):
        payload = {
            'title': 'Oppenheimer',
            'description': 'kaboommm',
            'duration_minutes': 180,
            'genre': 'Drama',
        }
        response = api_client.post(reverse('movie-list'), payload)
        assert response.status_code == 401
 
    def test_create_movie_authenticated(self, auth_client):
        payload = {
            'title': 'Oppenheimer',
            'description': 'kaboommm',
            'duration_minutes': 180,
            'genre': 'Drama',
        }
        response = auth_client.post(reverse('movie-list'), payload)
        assert response.status_code == 201
        assert Movie.objects.filter(title='Oppenheimer').exists()
 
 
@pytest.mark.django_db
class TestSessionViewSet:
 
    def test_list_sessions_is_public(self, api_client, session):
        response = api_client.get(reverse('session-list'))
        assert response.status_code == 200
 
    def test_filter_sessions_by_movie_id(self, api_client, movie, session):
        response = api_client.get(reverse('session-list'), {'movie_id': movie.id})
        assert response.status_code == 200
        results = response.data['results']
        assert all(s['movie'] == movie.id for s in results)
 
    def test_filter_by_nonexistent_movie_returns_empty(self, api_client):
        response = api_client.get(reverse('session-list'), {'movie_id': 99999})
        assert response.status_code == 200
        assert response.data['results'] == []
 
    def test_retrieve_session_returns_correct_data(self, api_client, session):
        response = api_client.get(reverse('session-detail', args=[session.id]))
        assert response.status_code == 200
        assert response.data['room'] == session.room