from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Camera

User = get_user_model()


class CameraAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")
        self.client.force_authenticate(user=self.user)

        self.camera = Camera.objects.create(
            name="Камера #1",
            rtsp_url="rtsp://192.168.1.1:554/stream",
            latitude=42.870000,
            longitude=74.590000,
            is_active=True,
        )

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def test_list_cameras(self):
        url = reverse("camera-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_camera(self):
        url = reverse("camera-list")
        data = {
            "name": "Камера #2",
            "rtsp_url": "rtsp://10.0.0.1:554/ch1",
            "latitude": "42.870123",
            "longitude": "74.591234",
            "is_active": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Camera.objects.count(), 2)

    def test_create_camera_invalid_rtsp(self):
        url = reverse("camera-list")
        data = {
            "name": "Плохая камера",
            "rtsp_url": "http://not-rtsp.com",
            "latitude": "42.0",
            "longitude": "74.0",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rtsp_url", response.data)

    def test_retrieve_camera(self):
        url = reverse("camera-detail", args=[self.camera.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.camera.name)

    def test_update_camera(self):
        url = reverse("camera-detail", args=[self.camera.pk])
        response = self.client.patch(url, {"name": "Обновлённая камера"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.camera.refresh_from_db()
        self.assertEqual(self.camera.name, "Обновлённая камера")

    def test_delete_camera(self):
        url = reverse("camera-detail", args=[self.camera.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Camera.objects.count(), 0)

    # ------------------------------------------------------------------
    # Дополнительные экшены
    # ------------------------------------------------------------------

    def test_toggle_camera(self):
        url = reverse("camera-toggle", args=[self.camera.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.camera.refresh_from_db()
        self.assertFalse(self.camera.is_active)

    def test_geo_endpoint(self):
        url = reverse("camera-geo")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["type"], "FeatureCollection")
        self.assertEqual(len(response.data["features"]), 1)

    def test_active_endpoint(self):
        Camera.objects.create(
            name="Неактивная",
            rtsp_url="rtsp://1.2.3.4/s",
            latitude=0,
            longitude=0,
            is_active=False,
        )
        url = reverse("camera-active")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # только активная

    def test_unauthorized_access(self):
        self.client.logout()
        url = reverse("camera-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)