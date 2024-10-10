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
    def test_200_returns_formatted_treasures(self):
        """
        Test verifies:
        - status code
        - length of resulting list of treasure dicts
        - treasure dicts content match the data types expected
        - treasures are sorted by age (ascending)
        """
        client = TestClient(app)
        response = client.get("/api/treasures")
        treasures = response.json()["treasures"]
        ages = [treasure["age"] for treasure in treasures]
        assert response.status_code == 200
        assert len(treasures) == 26
        for treasure in treasures:
            assert type(treasure["treasure_id"]) == int
            assert type(treasure["treasure_name"]) == str
            assert type(treasure["colour"]) == str
            assert type(treasure["age"]) == int
            assert type(treasure["cost_at_auction"]) == float
            assert type(treasure["shop_name"]) == str
        assert ages == sorted(ages)
        

    """
    Error handling considerations for GET "/api/treasures":
    - path is incorrect; 404 handled by FastAPI
    - method does not exist; 405 handled by FastAPI
    - db error; custom 500 implemented
    """
    def test_404_if_path_is_incorrect(self):
        client = TestClient(app)
        response = client.get("/api/treasure")
        assert response.status_code == 404
        assert response.json() == {
            "detail": "Not Found"
        }

    def test_405_if_method_does_not_exist(self):
        client = TestClient(app)
        response = client.patch("/api/treasures")
        assert response.status_code == 405
        assert response.json() == {
            "detail": "Method Not Allowed"
        }

    @pytest.mark.xfail
    def test_500_custom_message_if_db_error(self):
        """
        - Tested with a manual error (typo in SQL query)
        - Marked as expected failure as the typo has been fixed for benefit of other tests
        """
        client = TestClient(app)
        response = client.get("/api/treasures")
        assert response.status_code == 500
        assert response.json() == {
            "detail": "Server error: logged for investigation"
        }