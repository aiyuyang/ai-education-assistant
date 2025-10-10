"""
Additional Auth API tests: refresh and logout
"""

from fastapi.testclient import TestClient


class TestAuthMoreAPI:
    def test_refresh_and_logout(self, client: TestClient):
        # Register a user
        r = client.post(
            "/api/v1/auth/register",
            json={
                "username": "user_refresh",
                "email": "user_refresh@example.com",
                "password": "password123",
                "nickname": "UR"
            }
        )
        assert r.status_code == 200

        # Login (OAuth2 form)
        r = client.post(
            "/api/v1/auth/login",
            data={"username": "user_refresh", "password": "password123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert r.status_code == 200
        tokens = r.json()["data"]
        access = tokens["access_token"]
        refresh = tokens["refresh_token"]

        # Refresh
        r = client.post(
            "/api/v1/auth/refresh",
            params={"refresh_token": refresh},
        )
        assert r.status_code == 200
        new_tokens = r.json()["data"]
        assert new_tokens["access_token"] != access

        # Logout (should succeed with bearer)
        r = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
        )
        assert r.status_code == 200


