from rest_framework.test import APITestCase
from rest_framework import status
from apps.accounts.models import User
from apps.mechanics.models import Mechanic
from apps.service_requests.models import ServiceRequest


def auth_client(client):
    User.objects.create_user(username="tester", email="t@test.com", password="StrongPass123!")
    res = client.post("/api/v1/auth/login/", {"username": "tester", "password": "StrongPass123!"}, format="json")
    token = res.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class ServiceRequestTests(APITestCase):
    def setUp(self):
        auth_client(self.client)
        self.mechanic = Mechanic.objects.create(name="Rahul", phone="9876543210", location="Gurgaon", rating=4.5, is_open=True, services=["engine repair"])

    def test_create_success_default_pending(self):
        data = {"customer_name": "Arjun Mehra", "customer_phone": "9876543210", "vehicle_number": "MH01AB1234", "mechanic": self.mechanic.id, "service": "engine repair", "problem_description": "Noise"}
        res = self.client.post("/api/v1/service-requests/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["status"], "PENDING")
        self.assertEqual(res.data["mechanic"], self.mechanic.id)

    def test_mechanic_relationship(self):
        data = {"customer_name": "Arjun", "customer_phone": "9876543210", "vehicle_number": "DL08CA5678", "mechanic": self.mechanic.id, "service": "oil change"}
        res = self.client.post("/api/v1/service-requests/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        sr = ServiceRequest.objects.get(id=res.data["id"])
        self.assertEqual(sr.mechanic.id, self.mechanic.id)

    def test_nonexistent_mechanic(self):
        data = {"customer_name": "Arjun", "customer_phone": "9876543210", "vehicle_number": "MH01AB1234", "mechanic": 9999, "service": "engine repair"}
        res = self.client.post("/api/v1/service-requests/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("mechanic", res.data)

    def test_invalid_mechanic_not_integer(self):
        data = {"customer_name": "Arjun", "customer_phone": "9876543210", "vehicle_number": "MH01AB1234", "mechanic": "abc", "service": "engine repair"}
        res = self.client.post("/api/v1/service-requests/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_required_fields(self):
        data = {"customer_name": "Arjun", "customer_phone": "9876543210"}  # missing vehicle_number, mechanic, service
        res = self.client.post("/api/v1/service-requests/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("vehicle_number", res.data)
        self.assertIn("mechanic", res.data)
        self.assertIn("service", res.data)

    def test_invalid_service_blank(self):
        data = {"customer_name": "Arjun", "customer_phone": "9876543210", "vehicle_number": "MH01AB1234", "mechanic": self.mechanic.id, "service": ""}
        res = self.client.post("/api/v1/service-requests/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("service", res.data)

    def test_invalid_phone(self):
        data = {"customer_name": "Arjun", "customer_phone": "abc", "vehicle_number": "MH01AB1234", "mechanic": self.mechanic.id, "service": "engine repair"}
        res = self.client.post("/api/v1/service-requests/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("customer_phone", res.data)

    def test_invalid_vehicle_number(self):
        data = {"customer_name": "Arjun", "customer_phone": "9876543210", "vehicle_number": "!!", "mechanic": self.mechanic.id, "service": "engine repair"}
        res = self.client.post("/api/v1/service-requests/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("vehicle_number", res.data)

    def test_list_and_retrieve(self):
        data = {"customer_name": "Arjun", "customer_phone": "9876543210", "vehicle_number": "MH01AB1234", "mechanic": self.mechanic.id, "service": "engine repair"}
        res = self.client.post("/api/v1/service-requests/", data, format="json")
        sid = res.data["id"]
        res_list = self.client.get("/api/v1/service-requests/")
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(res_list.data["count"], 1)
        res_get = self.client.get(f"/api/v1/service-requests/{sid}/")
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertEqual(res_get.data["customer_name"], "Arjun")

    def test_invalid_status_transition(self):
        data = {"customer_name": "Arjun", "customer_phone": "9876543210", "vehicle_number": "MH01AB1234", "mechanic": self.mechanic.id, "service": "engine repair"}
        res = self.client.post("/api/v1/service-requests/", data, format="json")
        sid = res.data["id"]
        # PENDING -> COMPLETED is invalid (must go via IN_PROGRESS)
        res2 = self.client.patch(f"/api/v1/service-requests/{sid}/", {"status": "COMPLETED"}, format="json")
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", res2.data)

    def test_valid_status_transition(self):
        data = {"customer_name": "Arjun", "customer_phone": "9876543210", "vehicle_number": "MH01AB1234", "mechanic": self.mechanic.id, "service": "engine repair"}
        res = self.client.post("/api/v1/service-requests/", data, format="json")
        sid = res.data["id"]
        res2 = self.client.patch(f"/api/v1/service-requests/{sid}/", {"status": "IN_PROGRESS"}, format="json")
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data["status"], "IN_PROGRESS")
        res3 = self.client.patch(f"/api/v1/service-requests/{sid}/", {"status": "COMPLETED"}, format="json")
        self.assertEqual(res3.status_code, status.HTTP_200_OK)

    def test_protected_without_auth(self):
        self.client.credentials()  # clear
        res = self.client.get("/api/v1/service-requests/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
