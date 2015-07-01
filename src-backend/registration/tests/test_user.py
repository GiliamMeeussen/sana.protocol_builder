from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class UserTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('username', 'test@test.com', 'password')
        self.test_user.save()

    def test_user_has_token(self):
        token = Token.objects.get(user=self.test_user)
        self.assertTrue(token is not None)
