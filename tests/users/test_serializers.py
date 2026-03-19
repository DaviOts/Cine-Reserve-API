import pytest

from apps.users.serializers import RegisterSerializer


@pytest.mark.django_db
class TestRegisterSerializer:
 
    def test_valid_data_creates_user(self):
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'strongpass123',
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert user.pk is not None
        assert user.email == 'new@test.com'
 
    def test_password_is_write_only(self):
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'strongpass123',
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        assert 'password' not in serializer.data
 
    def test_password_is_hashed_not_plain_text(self):
        data = {
            'username': 'hashuser',
            'email': 'hash@test.com',
            'password': 'strongpass123',
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.password != 'strongpass123'
        assert user.check_password('strongpass123')
 
    def test_duplicate_email_is_invalid(self, user):
        data = {
            'username': 'another',
            'email': user.email,
            'password': 'strongpass123',
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
 
    def test_missing_required_fields(self):
        serializer = RegisterSerializer(data={})
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
        assert 'username' in serializer.errors
        assert 'password' in serializer.errors