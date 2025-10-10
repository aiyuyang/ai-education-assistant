"""
Study Plans API tests
"""


class TestStudyPlansAPI:
    def test_list_unauthorized(self, client):
        r = client.get("/api/v1/study-plans/")
        assert r.status_code in (401, 403)

    def test_crud_flow(self, client, auth_headers):
        # create
        payload = {
            "title": "高数复习计划",
            "description": "一周强化",
            "subject": "数学",
            "difficulty_level": "beginner",
            "estimated_duration": 7,
            "is_public": False
        }
        r = client.post("/api/v1/study-plans/", json=payload, headers=auth_headers)
        assert r.status_code in (200, 201)
        body = r.json()
        plan = body.get("data", body)
        plan_id = plan.get("id")
        assert plan_id

        # list
        r = client.get("/api/v1/study-plans/", headers=auth_headers)
        assert r.status_code == 200

        # get by id
        r = client.get(f"/api/v1/study-plans/{plan_id}", headers=auth_headers)
        assert r.status_code == 200

        # update
        r = client.put(f"/api/v1/study-plans/{plan_id}", json={"title": "更新后的计划"}, headers=auth_headers)
        assert r.status_code in (200, 204)

        # delete
        r = client.delete(f"/api/v1/study-plans/{plan_id}", headers=auth_headers)
        assert r.status_code in (200, 204)



