'''This module contains the test suite for the
`Cat's Rare Treasures` FastAPI app.'''
from fastapi.testclient import TestClient
from main import app
from db.seed import seed_db
import pytest


@pytest.fixture(autouse=True)
def reset_db():
    seed_db(env='test')
    yield
    seed_db(env='test')

@pytest.fixture()
def client():
    return TestClient(app)


class TestGetAllTreasures:
    def test_200_returns_formatted_treasures_with_default_sort_by_age(self, client):
        """
        Test verifies:
        - status code
        - length of resulting list of treasure dicts
        - treasure dicts content match the data types expected
        - treasures are sorted by age (ascending)
        """
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

    def test_200_returns_formatted_treasures_with_specified_sort_by_column(self, client):
        """
        Test verifies:
        - status code
        - length of resulting list of treasure dicts
        - treasure dicts content match the data types expected
        - treasures are sorted by the specified column
        """
        response = client.get("/api/treasures?sort_by=cost_at_auction")
        treasures = response.json()["treasures"]
        costs_at_auction = [treasure["cost_at_auction"] for treasure in treasures]
        assert response.status_code == 200
        assert len(treasures) == 26
        for treasure in treasures:
            assert type(treasure["treasure_id"]) == int
            assert type(treasure["treasure_name"]) == str
            assert type(treasure["colour"]) == str
            assert type(treasure["age"]) == int
            assert type(treasure["cost_at_auction"]) == float
            assert type(treasure["shop_name"]) == str
        assert costs_at_auction == sorted(costs_at_auction)

    def test_200_returns_formatted_treasures_with_specified_sort_order(self, client):
        """
        Test verifies:
        - status code
        - length of resulting list of treasure dicts
        - treasure dicts content match the data types expected
        - treasures are sorted by the specified order
        """
        response = client.get("/api/treasures?order=desc")
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
        assert ages == sorted(ages, reverse=True)

    def test_200_returns_treasures_filtered_by_specified_colour(self, client):
        response = client.get("/api/treasures?colour=gold")
        treasures = response.json()["treasures"]
        assert response.status_code == 200
        assert len(treasures) == 2
        for treasure in treasures:
            assert treasure["colour"] == "gold"
            assert type(treasure["treasure_id"]) == int
            assert type(treasure["treasure_name"]) == str
            assert type(treasure["age"]) == int
            assert type(treasure["cost_at_auction"]) == float
            assert type(treasure["shop_name"]) == str
        
    """
    Error handling considerations for GET "/api/treasures" are tested below:
    
    Path is incorrect; 404 handled by FastAPI
    """
    def test_404_if_path_is_incorrect(self, client):
        response = client.get("/api/treasure")
        assert response.status_code == 404
        assert response.json() == {
            "detail": "Not Found"
        }

    """
    Method does not exist; 405 handled by FastAPI
    """
    def test_405_if_method_does_not_exist(self, client):
        response = client.patch("/api/treasures")
        assert response.status_code == 405
        assert response.json() == {
            "detail": "Method Not Allowed"
        }

    """
    Sort by parameter empty/invalid; 422 handled by FastAPI
    """
    def test_422_if_specified_sort_column_not_allowed(self, client):
        response = client.get("/api/treasures?sort_by=")
        assert response.status_code == 422

        response = client.get("/api/treasures?sort_by=treasure_id")
        assert response.status_code == 422

        response = client.get("/api/treasures?sort_by=thisdoesnotexist")
        assert response.status_code == 422

    """
    Order parameter empty/invalid; 422 handled by FastAPI
    """
    def test_422_if_specified_order_not_allowed(self, client):
        response = client.get("/api/treasures?order=")
        assert response.status_code == 422

        response = client.get("/api/treasures?order=notallowed")
        assert response.status_code == 422

    """
    Colour parameter empty/invalid; 422 handled by FastAPI
    """
    def test_422_if_specified_colour_does_not_exist(self, client):
        response = client.get("/api/treasures?colour=")
        assert response.status_code == 422

        response = client.get("/api/treasures?colour=notacolour")
        assert response.status_code == 422

    """
    db error; custom 500 implemented
    """
    @pytest.mark.xfail
    def test_500_custom_message_if_db_error(self, client):
        """
        - Tested with a manual error (typo in SQL query)
        - Marked as expected failure as the typo has been fixed for benefit of other tests
        """
        response = client.get("/api/treasures")
        assert response.status_code == 500
        assert response.json() == {
            "detail": "Server error: logged for investigation"
        }


class TestPostNewTreasure:
    def test_200_adds_new_treasure_and_returns_confirmation(self, client):
        """
        Test verifies:
        - status code
        - response contains newly generated treasure_id
        """
        response = client.post("/api/treasures", json={
            "treasure_name": "new-treasure",
            "colour": "saffron",
            "age": 30,
            "cost_at_auction": "70.99",
            "shop_id": 4
        })
        assert response.status_code == 201
        assert response.json() == {
            "treasure": {
                "treasure_id": 27,
                "treasure_name": "new-treasure",
                "colour": "saffron",
                "age": 30,
                "cost_at_auction": 70.99,
                "shop_id": 4
            }
        }

    """
    Error handling considerations for POST "/api/treasures" are tested below, except for:
    - Method does not exist; tested above for GET "/api/treasures" as base endpoint is the same
    """

    """
    Path is incorrect; 404 default handled by FastAPI
    """
    def test_404_if_path_is_incorrect(self, client):
        response = client.post("/api/treasu")
        assert response.status_code == 404
        assert response.json() == {
            "detail": "Not Found"
        }

    """
    Parameter/containing parameters is wrong type; 422 default handled by FastAPI
    """
    def test_422_if_request_body_is_wrong_type(self, client):
        response = client.post("/api/treasures", json="hi")
        assert response.status_code == 422

        response = client.post("/api/treasures", json={
            "treasure_name": 100, # int, rather than str
            "colour": "saffron",
            "age": 30,
            "cost_at_auction": "70.99",
            "shop_id": 4
        })
        assert response.status_code == 422

    """
    Valid, but empty input; 422 default handled by FastAPI
    """
    def test_422_if_request_body_is_wrong_type(self, client):
        response = client.post("/api/treasures", json={})
        assert response.status_code == 422

    @pytest.mark.xfail
    def test_500_if_db_error(self, client):
        """
        - Tested with a manual error (typo in SQL query)
        - Marked as expected failure as the typo has been fixed for benefit of other tests
        """
        response = client.post("/api/treasures", json={
            "treasure_name": "new-treasure",
            "colour": "saffron",
            "age": 30,
            "cost_at_auction": "70.99",
            "shop_id": 4
        })
        assert response.status_code == 500
        assert response.json() == {
            "detail": "Server error: logged for investigation"
        }
