'''This module contains the test suite for the
`Cat's Rare Treasures` FastAPI app.'''
from fastapi.testclient import TestClient
from main import app
from db.seed import seed_db
import pytest


@pytest.fixture(autouse=True)
def reset_db():
    seed_db(env='test')


class TestGetAllTreasures:
    """
    Test verifies:
    - status code
    - length of resulting list of treasure dicts
    - treasure dicts content match the data types expected
    - age of first treasure is lower than age of last treasure in the list
    """
    def test_200_returns_formatted_treasures(self):
        client = TestClient(app)
        response = client.get("/api/treasures")
        body = response.json()
        assert response.status_code == 200
        assert len(body["treasures"]) == 26
        for treasure in body["treasures"]:
            assert type(treasure["treasure_id"]) == int
            assert type(treasure["treasure_name"]) == str
            assert type(treasure["colour"]) == str
            assert type(treasure["age"]) == int
            assert type(treasure["cost_at_auction"]) == float
            assert type(treasure["shop_name"]) == str
        assert body["treasures"][0]["age"] < body["treasures"][-1]["age"]