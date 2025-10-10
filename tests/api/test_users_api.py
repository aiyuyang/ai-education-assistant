"""
Users API profile and stats tests
"""

from fastapi.testclient import TestClient


class TestUsersAPI:
    def test_profile_and_stats(self, client: TestClient, auth_headers: dict):
        # Get profile
        r = client.get("/api/v1/users/me", headers=auth_headers)
        assert r.status_code == 200
        profile = r.json()["data"]
        assert "username" in profile

        # Update profile
        r = client.put("/api/v1/users/me", json={"nickname": "Updated"}, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["data"]["nickname"] == "Updated"

        # Get stats
        r = client.get("/api/v1/users/me/stats", headers=auth_headers)
        assert r.status_code == 200
        stats = r.json()["data"]
        assert "study_plans_count" in stats
        assert "conversations_count" in stats


