from rest_framework.test import APITestCase
from rest_framework import status
from apps.accounts.models import User
from apps.mechanics.models import Mechanic


def auth_client(client):
    user = User.objects.create_user(username="tester", email="t@test.com", password="StrongPass123!")
    res = client.post("/api/v1/auth/login/", {"username": "tester", "password": "StrongPass123!"}, format="json")
    token = res.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return user


class MechanicTests(APITestCase):
    def setUp(self):
        auth_client(self.client)

    def test_create_mechanic(self):
        data = {"name": "Rahul Sharma", "phone": "9876543210", "location": "Gurgaon", "rating": 4.5, "is_open": True, "services": ["engine repair", "oil change"]}
        res = self.client.post("/api/v1/mechanics/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], "Rahul Sharma")
        self.assertEqual(Mechanic.objects.count(), 1)

    def test_retrieve_mechanic(self):
        m = Mechanic.objects.create(name="Amit", phone="9876543211", location="Delhi", rating=4.2, is_open=True, services=["brake service"])
        res = self.client.get(f"/api/v1/mechanics/{m.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Amit")

    def test_update_mechanic_put(self):
        m = Mechanic.objects.create(name="Amit", phone="9876543211", location="Delhi", rating=4.2, is_open=True, services=["brake service"])
        data = {"name": "Amit Verma", "phone": "9876543211", "location": "Delhi", "rating": 4.8, "is_open": False, "services": ["brake service", "oil change"]}
        res = self.client.put(f"/api/v1/mechanics/{m.id}/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["rating"], "4.80")
        self.assertEqual(res.data["is_open"], False)

    def test_partial_update_patch(self):
        m = Mechanic.objects.create(name="Amit", phone="9876543211", location="Delhi", rating=4.2, is_open=True, services=["brake service"])
        res = self.client.patch(f"/api/v1/mechanics/{m.id}/", {"is_open": False}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["is_open"], False)

    def test_delete_mechanic(self):
        m = Mechanic.objects.create(name="Amit", phone="9876543211", location="Delhi", rating=4.2, is_open=True, services=["brake service"])
        res = self.client.delete(f"/api/v1/mechanics/{m.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Mechanic.objects.count(), 0)

    def test_invalid_mechanic_id(self):
        res = self.client.get("/api/v1/mechanics/9999/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_validation_invalid_phone(self):
        data = {"name": "Test", "phone": "abc", "location": "Gurgaon", "rating": 4.5, "is_open": True, "services": ["engine repair"]}
        res = self.client.post("/api/v1/mechanics/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", res.data)

    def test_validation_invalid_rating(self):
        data = {"name": "Test", "phone": "9876543210", "location": "Gurgaon", "rating": 10, "is_open": True, "services": ["engine repair"]}
        res = self.client.post("/api/v1/mechanics/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", res.data)

    def test_validation_missing_required(self):
        data = {"name": "", "phone": "9876543210", "location": "Gurgaon", "rating": 4.5, "is_open": True, "services": []}
        res = self.client.post("/api/v1/mechanics/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search(self):
        Mechanic.objects.create(name="Rahul Sharma", phone="9876543210", location="Gurgaon", rating=4.5, is_open=True, services=["engine repair"])
        Mechanic.objects.create(name="Amit Verma", phone="9876543211", location="Delhi", rating=4.2, is_open=True, services=["brake service"])
        res = self.client.get("/api/v1/mechanics/?search=rahul")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(res.data["results"][0]["name"], "Rahul Sharma")

    def test_filtering(self):
        Mechanic.objects.create(name="Rahul", phone="9876543210", location="Gurgaon", rating=4.5, is_open=True, services=["engine repair"])
        Mechanic.objects.create(name="Amit", phone="9876543211", location="Delhi", rating=4.2, is_open=False, services=["brake service"])
        res = self.client.get("/api/v1/mechanics/?location=Gurgaon")
        self.assertEqual(res.data["count"], 1)
        res2 = self.client.get("/api/v1/mechanics/?is_open=true")
        self.assertEqual(res2.data["count"], 1)
        res3 = self.client.get("/api/v1/mechanics/?is_open=false")
        self.assertEqual(res3.data["count"], 1)

    def test_ordering(self):
        Mechanic.objects.create(name="Low", phone="9876543210", location="Gurgaon", rating=2.0, is_open=True, services=["engine repair"])
        Mechanic.objects.create(name="High", phone="9876543211", location="Gurgaon", rating=5.0, is_open=True, services=["engine repair"])
        res = self.client.get("/api/v1/mechanics/?ordering=-rating")
        self.assertEqual(res.data["results"][0]["name"], "High")
        res2 = self.client.get("/api/v1/mechanics/?ordering=rating")
        self.assertEqual(res2.data["results"][0]["name"], "Low")

    def test_pagination(self):
        for i in range(15):
            Mechanic.objects.create(name=f"M{i}", phone=f"98765432{i:02d}", location="Gurgaon", rating=4.0, is_open=True, services=["engine repair"])
        res = self.client.get("/api/v1/mechanics/?page=1")
        self.assertEqual(len(res.data["results"]), 10)
        self.assertIsNotNone(res.data["next"])
        res2 = self.client.get("/api/v1/mechanics/?page=2")
        self.assertEqual(len(res2.data["results"]), 5)
        self.assertIsNone(res2.data["next"])
