from rest_framework.test import APITestCase
from rest_framework import status

class HealthTests(APITestCase):
    def test_health_public(self):
        res = self.client.get("/api/v1/health/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "healthy")
        self.assertIn("database", res.data)
