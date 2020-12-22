from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your tests here.
class HomeTestCase(TestCase):
    def setUp(self):
        User.objects.create(email='thomasrea0113@gmail.com')

    def test_user(self):
        self.assertEqual(1, User.objects.filter(email='thomasrea0113@gmail.com').count())
