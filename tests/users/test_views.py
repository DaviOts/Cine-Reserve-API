import pytest
from apps.users.models import User
from django.urls import reverse



@pytest.mark.django_db
class TestRegisterView:
 
    def test_register_returns_201(self, api_client):
        payload = {
            'username': 'miranha',
            'email': 'miranha@espetacular.com',
            'password': 'careca123',
        }
        response = api_client.post(reverse('register'), payload)
        assert response.status_code == 201
 
    def test_register_creates_user_in_db(self, api_client):
        payload = {
            'username': 'dr_octopus',
            'email': 'dr.octopus@test.com',
            'password': 'carequinha123',
        }
        api_client.post(reverse('register'), payload)
        assert User.objects.filter(email='dr.octopus@test.com').exists()
 
    def test_register_does_not_return_password(self, api_client):
        payload = {
            'username': 'nopass',
            'email': 'nopass@test.com',
            'password': 'strongpass123',
        }
        response = api_client.post(reverse('register'), payload)
        assert 'password' not in response.data
 
    def test_register_duplicate_email_returns_400(self, api_client, user):
        payload = {
            'username': 'dup',
            'email': user.email,
            'password': 'strongpass123',
        }
        response = api_client.post(reverse('register'), payload)
        assert response.status_code == 400
 
    def test_register_missing_fields_returns_400(self, api_client):
        response = api_client.post(reverse('register'), {})
        assert response.status_code == 400
 
 
@pytest.mark.django_db
class TestLoginView:
 
    def test_login_returns_access_and_refresh_tokens(self, api_client, user):
        payload = {'email': user.email, 'password': 'strongpass123'}
        response = api_client.post(reverse('login'), payload)
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
 
    def test_login_wrong_password_returns_401(self, api_client, user):
        payload = {'email': user.email, 'password': 'wrongpassword'}
        response = api_client.post(reverse('login'), payload)
        assert response.status_code == 401
 
    def test_login_nonexistent_user_returns_401(self, api_client):
        payload = {'email': 'ghost@test.com', 'password': 'whatever'}
        response = api_client.post(reverse('login'), payload)
        assert response.status_code == 401
 
    def test_token_refresh_works(self, api_client, user):
        login_response = api_client.post(reverse('login'), {
            'email': user.email,
            'password': 'strongpass123',
        })
        refresh_token = login_response.data['refresh']
 
        response = api_client.post(reverse('token_refresh'), {'refresh': refresh_token})
        assert response.status_code == 200
        assert 'access' in response.data