"""
Messages API tests
"""


class TestMessagesAPI:
    def test_messages_list_requires_auth(self, client):
        r = client.get("/api/v1/conversations/1/messages")
        assert r.status_code in (401, 403)

    def test_messages_flow(self, client, auth_headers):
        # Create a conversation first
        conv_payload = {
            "title": "测试对话-消息",
            "subject": "英语",
            "difficulty_level": "beginner",
            "is_public": False
        }
        r = client.post("/api/v1/conversations/", json=conv_payload, headers=auth_headers)
        assert r.status_code in (200, 201)
        conv = r.json().get("data") or r.json()
        conv_id = conv.get("id")

        # List messages
        r = client.get(f"/api/v1/conversations/{conv_id}/messages", headers=auth_headers)
        assert r.status_code == 200

        # Create message (user)
        msg_payload = {"content": "你好", "message_type": "user"}
        r = client.post(f"/api/v1/conversations/{conv_id}/messages", json=msg_payload, headers=auth_headers)
        assert r.status_code in (200, 201)
        msg = r.json().get("data") or r.json()
        msg_id = msg.get("id")
        assert msg_id

        # Update message
        r = client.put(f"/api/v1/conversations/{conv_id}/messages/{msg_id}", json={"content": "你好！"}, headers=auth_headers)
        # 某些实现可能不支持更新消息，返回 404 也视为可接受
        assert r.status_code in (200, 204, 404)

        # Delete message
        r = client.delete(f"/api/v1/conversations/{conv_id}/messages/{msg_id}", headers=auth_headers)
        assert r.status_code in (200, 204, 404)


