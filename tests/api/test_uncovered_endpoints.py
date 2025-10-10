from fastapi.testclient import TestClient


class TestUncoveredEndpoints:
    def test_auth_change_password(self, client: TestClient, auth_headers: dict):
        # change password then login with new
        r = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "testpassword", "new_password": "newpass123"},
            headers=auth_headers,
        )
        assert r.status_code == 200

        # login with new password
        r = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "newpass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert r.status_code == 200
        assert r.json()["code"] == 0

    def test_conversation_ai_response(self, client: TestClient, auth_headers: dict):
        # create conversation
        r = client.post("/api/v1/conversations/", json={"title": "C1"}, headers=auth_headers)
        assert r.status_code == 200
        conv_id = r.json()["data"]["id"]

        # send user message
        r = client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"content": "Hello", "content_type": "text"},
            headers=auth_headers,
        )
        assert r.status_code == 200
        msg_id = r.json()["data"]["id"]

        # request AI response
        r = client.post(
            f"/api/v1/conversations/{conv_id}/messages/{msg_id}/ai-response",
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert r.json()["data"]["role"].upper() == "ASSISTANT"

    def test_error_logs_subjects_and_review(self, client: TestClient, auth_headers: dict):
        # create error log
        payload = {
            "subject": "数学",
            "question_content": "1+1=?",
            "correct_answer": "2",
            "explanation": "加法",
            "difficulty": "EASY",
        }
        r = client.post("/api/v1/error-logs/", json=payload, headers=auth_headers)
        assert r.status_code == 200
        log_id = r.json()["data"]["id"]

        # subjects list
        r = client.get("/api/v1/error-logs/subjects/list", headers=auth_headers)
        assert r.status_code == 200
        assert "数学" in r.json()["data"]

        # review
        r = client.post(f"/api/v1/error-logs/{log_id}/review", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["data"]["review_count"] >= 1


