"""
Study Tasks API tests under Study Plans
"""

from fastapi.testclient import TestClient


class TestStudyTasksAPI:
    def test_tasks_crud_flow(self, client: TestClient, auth_headers: dict):
        # 1) Create a plan first
        plan_payload = {"title": "Plan A", "description": "desc"}
        r = client.post("/api/v1/study-plans/", json=plan_payload, headers=auth_headers)
        assert r.status_code == 200
        plan_id = r.json()["data"]["id"]

        # 2) Create task
        task_payload = {"title": "Task 1", "description": "read", "priority": "medium"}
        r = client.post(f"/api/v1/study-plans/{plan_id}/tasks", json=task_payload, headers=auth_headers)
        assert r.status_code == 200
        task = r.json()["data"]
        task_id = task["id"]

        # 3) List tasks
        r = client.get(f"/api/v1/study-plans/{plan_id}/tasks", headers=auth_headers)
        assert r.status_code == 200
        items = r.json()["data"]
        assert any(t["id"] == task_id for t in items)

        # 4) Update task
        update = {"status": "completed"}
        r = client.put(f"/api/v1/study-plans/{plan_id}/tasks/{task_id}", json=update, headers=auth_headers)
        assert r.status_code == 200
        updated = r.json()["data"]
        assert updated["status"].lower() == "completed"

        # 5) Delete task
        r = client.delete(f"/api/v1/study-plans/{plan_id}/tasks/{task_id}", headers=auth_headers)
        assert r.status_code == 200


