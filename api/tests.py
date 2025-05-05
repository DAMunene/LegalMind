from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import CustomUser

class SerializerTests(TestCase):
    def setUp(self):
        # Create a test user with a different email to avoid conflicts
        self.user_data = {
            'email': 'existing@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = CustomUser.objects.create_user(**self.user_data)

    def test_register_serializer_valid(self):
        """Test that valid data is properly validated"""
        valid_data = {
            'email': 'new@example.com',  # Different email from existing user
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_register_serializer_invalid(self):
        """Test that invalid data is properly caught"""
        # Invalid email test
        invalid_data = {
            'email': 'invalid-email',  # Invalid email format
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

        # Duplicate email test
        serializer = RegisterSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

        # Short password test
        invalid_data = {
            'email': 'test@example.com',
            'password': '123',  # Too short
            'first_name': 'Test',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_register_serializer_create(self):
        """Test that user is created with valid data"""
        new_user_data = {
            'email': 'newuser@example.com',
            'password': 'testpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=new_user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, new_user_data['email'])
        self.assertTrue(user.check_password(new_user_data['password']))
        self.assertEqual(user.first_name, new_user_data['first_name'])
        self.assertEqual(user.last_name, new_user_data['last_name'])

    def test_register_serializer_create(self):
        """Test that user is created with valid data"""
        new_user_data = {
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=new_user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, new_user_data['email'])
        self.assertTrue(user.check_password(new_user_data['password']))

    def test_login_serializer_valid(self):
        """Test that valid login data is properly validated"""
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, self.user)

    def test_login_serializer_invalid(self):
        """Test that invalid login data is properly caught"""
        invalid_data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'  # Incorrect password
        }
        serializer = LoginSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_user_serializer(self):
        """Test that user serializer properly serializes user data"""
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['id'], self.user.id)
        self.assertEqual(serializer.data['email'], self.user_data['email'])
        self.assertEqual(serializer.data['first_name'], self.user_data['first_name'])
        self.assertEqual(serializer.data['last_name'], self.user_data['last_name'])

    def test_user_serializer_read_only(self):
        """Test that user serializer doesn't allow updating password"""
        data = {
            'email': self.user_data['email'],
            'password': 'newpassword',  # This should be ignored
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        serializer = UserSerializer(self.user, data=data)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertNotEqual(updated_user.password, data['password'])  # Password should remain unchanged
