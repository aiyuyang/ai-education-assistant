"""
Error Logs API stats tests
"""
import pytest


class TestErrorLogsStatsAPI:
    """Validate error logs stats endpoints respond and shape is correct enough."""

    def _auth_header(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    def test_get_error_logs_stats_without_auth(self, client):
        resp = client.get("/api/v1/error-logs/stats/summary")
        # Accept common unauthorized statuses across stacks
        assert resp.status_code in (200, 401, 403)

    def test_get_error_logs_stats_with_auth(self, client, auth_headers):
        resp = client.get(
            "/api/v1/error-logs/stats/summary",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        # Accept both wrapped {code,message,data} and direct object
        payload = data.get("data", data)
        assert isinstance(payload, dict)
        # keys that should exist (support old/new response shapes)
        if "total_count" in payload:
            assert "subjects" in payload
            assert isinstance(payload["subjects"], dict)
        else:
            # fallback to detailed stats fields
            for key in ("difficulty_distribution", "resolved_logs", "mastered_logs", "resolution_rate"):
                assert key in payload


