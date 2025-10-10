"""
Conversations API tests
"""
import pytest


class TestConversationsAPI:
    def _auth_header(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    def test_list_conversations_unauthorized(self, client):
        resp = client.get("/api/v1/conversations/")
        assert resp.status_code in (401, 403)

    def test_conversation_crud_flow(self, client, auth_headers):
        headers = auth_headers

        # Create
        create_payload = {
            "title": "测试对话",
            "subject": "数学",
            "difficulty_level": "beginner",
            "is_public": False
        }
        r = client.post("/api/v1/conversations/", json=create_payload, headers=headers)
        assert r.status_code in (200, 201)
        body = r.json()
        conv = body.get("data", body)
        conv_id = conv.get("id")
        assert conv_id

        # List
        r = client.get("/api/v1/conversations/", headers=headers)
        assert r.status_code == 200
        items = r.json().get("data") or r.json()
        assert isinstance(items, list)

        # Stats
        r = client.get("/api/v1/conversations/stats/summary", headers=headers)
        assert r.status_code == 200

        # Messages (list)
        r = client.get(f"/api/v1/conversations/{conv_id}/messages", headers=headers)
        assert r.status_code == 200

        # Update
        r = client.put(f"/api/v1/conversations/{conv_id}", json={"title": "更新后的对话"}, headers=headers)
        assert r.status_code in (200, 204)

        # Delete
        r = client.delete(f"/api/v1/conversations/{conv_id}", headers=headers)
        assert r.status_code in (200, 204)


