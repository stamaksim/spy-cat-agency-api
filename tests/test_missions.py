# tests/test_missions.py
def test_notes_frozen_after_target_complete(client, monkeypatch):
    from app.services import cat_breeds

    monkeypatch.setattr(cat_breeds, "validate_breed", lambda breed: True)

    # 1) Create cat
    cat_payload = {
        "name": "AgentCat",
        "years_of_experience": 2,
        "breed": "Abyssinian",
        "salary": 2000,
    }
    cat = client.post("/cats", json=cat_payload).json()
    cat_id = cat["id"]

    # 2) Create mission with 2 targets
    mission_payload = {
        "targets": [
            {"name": "Alice", "country": "Finland", "notes": "Start observing."},
            {"name": "Bob", "country": "Estonia", "notes": "Collect evidence."},
        ]
    }
    mission = client.post("/missions", json=mission_payload).json()
    mission_id = mission["id"]
    target_id = mission["targets"][0]["id"]

    # 3) Assign cat
    r = client.post(f"/missions/{mission_id}/assign/{cat_id}")
    assert r.status_code == 200, r.text

    # 4) Complete target
    r = client.patch(f"/missions/{mission_id}/targets/{target_id}", json={"complete": True})
    assert r.status_code == 200, r.text

    # 5) Try update notes after complete -> must be blocked
    r = client.patch(
        f"/missions/{mission_id}/targets/{target_id}",
        json={"notes": "New notes after complete"},
    )
    assert r.status_code == 409, r.text
