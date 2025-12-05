from django.contrib.auth import get_user_model
from django.test import TestCase

# Create your tests here.

class CustomuserTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(first_name="Mark",last_name="Muwanguzi",email="mark@mytech-dev.com",password="testpass123")
        self.assertEqual(user.first_name,"Mark")
        self.assertEqual(user.last_name,"Muwanguzi")
        self.assertEqual(user.email,"mark@mytech-dev.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
