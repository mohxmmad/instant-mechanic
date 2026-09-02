from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from apps.accounts.models import User


class AuthTests(APITestCase):
    def test_register_success(self):
        url = "/api/v1/auth/register/"
        data = {"username": "alice", "email": "alice@example.com", "password": "StrongPass123!"}
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertTrue(User.objects.filter(username="alice").exists())

    def test_register_duplicate_username(self):
        User.objects.create_user(username="bob", email="bob@example.com", password="StrongPass123!")
        url = "/api/v1/auth/register/"
        data = {"username": "bob", "email": "bob2@example.com", "password": "StrongPass123!"}
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", res.data)

    def test_login_success(self):
        User.objects.create_user(username="charlie", email="charlie@example.com", password="StrongPass123!")
        url = "/api/v1/auth/login/"
        res = self.client.post(url, {"username": "charlie", "password": "StrongPass123!"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_login_with_email(self):
        User.objects.create_user(username="dave", email="dave@example.com", password="StrongPass123!")
        url = "/api/v1/auth/login/"
        res = self.client.post(url, {"username": "dave@example.com", "password": "StrongPass123!"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_invalid_credentials(self):
        User.objects.create_user(username="eve", email="eve@example.com", password="StrongPass123!")
        url = "/api/v1/auth/login/"
        res = self.client.post(url, {"username": "eve", "password": "WrongPass"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_protected_endpoint_without_auth(self):
        url = "/api/v1/mechanics/"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        User.objects.create_user(username=" frank", email="frank@example.com", password="StrongPass123!".strip())
        # create via register to get refresh
        res = self.client.post("/api/v1/auth/register/", {"username": "grace", "email": "grace@example.com", "password": "StrongPass123!"}, format="json")
        refresh = res.data["refresh"]
        res2 = self.client.post("/api/v1/auth/refresh/", {"refresh": refresh}, format="json")
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertIn("access", res2.data)
