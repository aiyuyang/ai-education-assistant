from fastapi.testclient import TestClient


class TestStudyPlansFilters:
    def test_list_plans_case_insensitive_status_and_fields(self, client: TestClient, auth_headers: dict):
        # create two plans
        payload1 = {
            "title": "Plan A",
            "description": "Desc A",
            "subject": "编程",
            "difficulty_level": "beginner",
            "estimated_duration": 5,
            "is_public": True,
        }
        payload2 = {
            "title": "Plan B",
            "description": "Desc B",
            "subject": "数学",
            "difficulty_level": "advanced",
            "estimated_duration": 10,
            "is_public": False,
        }

        r = client.post("/api/v1/study-plans/", json=payload1, headers=auth_headers)
        assert r.status_code == 200
        r = client.post("/api/v1/study-plans/", json=payload2, headers=auth_headers)
        assert r.status_code == 200

        # lowercase status filter should work
        r = client.get("/api/v1/study-plans/?status=ongoing", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 2

        # fields should be present
        for item in data:
            assert "subject" in item
            assert "difficulty_level" in item
            assert "estimated_duration" in item
            assert "is_public" in item


