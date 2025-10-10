"""
Error Logs API CRUD and listing tests
"""

from fastapi.testclient import TestClient


class TestErrorLogsAPIEndpoints:
    def test_create_list_get_update_delete(self, client: TestClient, auth_headers: dict):
        # Create
        payload = {
            "subject": "Math",
            "topic": "Algebra",
            "question_content": "Solve x+2=5",
            "correct_answer": "x=3",
            "explanation": "Subtract 2 from both sides",
            "difficulty": "easy",
        }
        r = client.post("/api/v1/error-logs/", json=payload, headers=auth_headers)
        assert r.status_code == 200
        created = r.json()["data"]
        log_id = created["id"]
        assert created["subject"] == "Math"
        assert created["difficulty"] in ("easy", "EASY")

        # List
        r = client.get("/api/v1/error-logs/?page=1&per_page=20", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()["data"]
        assert isinstance(data, list)
        assert any(item["id"] == log_id for item in data)

        # Filter by difficulty
        r = client.get("/api/v1/error-logs/?difficulty=easy", headers=auth_headers)
        assert r.status_code == 200

        # Get by id
        r = client.get(f"/api/v1/error-logs/{log_id}", headers=auth_headers)
        assert r.status_code == 200
        fetched = r.json()["data"]
        assert fetched["id"] == log_id

        # Update
        update = {"explanation": "Move 2 to RHS"}
        r = client.put(f"/api/v1/error-logs/{log_id}", json=update, headers=auth_headers)
        assert r.status_code == 200
        updated = r.json()["data"]
        assert updated["explanation"].startswith("Move 2")

        # Delete
        r = client.delete(f"/api/v1/error-logs/{log_id}", headers=auth_headers)
        assert r.status_code == 200

        # Ensure deleted
        r = client.get(f"/api/v1/error-logs/{log_id}", headers=auth_headers)
        assert r.status_code in (404, 400)


