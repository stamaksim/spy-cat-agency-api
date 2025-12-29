# tests/test_cats.py
def test_create_cat_success(client, monkeypatch):
    from app.services import cat_breeds

    monkeypatch.setattr(cat_breeds, "validate_breed", lambda breed: True)

    payload = {
        "name": "Shadow",
        "years_of_experience": 3,
        "breed": "Abyssinian",
        "salary": 1500,
    }

    r = client.post("/cats", json=payload)
    assert r.status_code == 201, r.text

    data = r.json()
    assert data["id"] > 0
    assert data["name"] == "Shadow"
    assert data["breed"] == "Abyssinian"
    assert data["salary"] == 1500


def test_create_cat_invalid_breed_returns_400(client, monkeypatch):
    from app.services import cat_breeds

    monkeypatch.setattr(cat_breeds, "validate_breed", lambda breed: False)

    payload = {
        "name": "BadCat",
        "years_of_experience": 1,
        "breed": "NotARealBreed",
        "salary": 1000,
    }

    r = client.post("/cats", json=payload)
    assert r.status_code in (400, 422), r.text
