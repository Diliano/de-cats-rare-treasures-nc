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
    def test_201_adds_new_treasure_and_returns_confirmation(self, client):
        """
        Test verifies:
        - status code
        - response contains newly generated treasure_id
        """
        response = client.post("/api/treasures", json={
            "treasure_name": "new-treasure",
            "colour": "saffron",
            "age": 30,
            "cost_at_auction": 70.99,
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
            "cost_at_auction": 70.99,
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
            "cost_at_auction": 70.99,
            "shop_id": 4
        })
        assert response.status_code == 500
        assert response.json() == {
            "detail": "Server error: logged for investigation"
        }


class TestPatchUpdateTreasurePrice:
    def test_200_updates_treasure_price_and_returns_confirmation(self, client):
        """
        Test verifies:
        - status code
        - treasure cost has been updated
        """
        response = client.patch("/api/treasures/1", json={
            "cost_at_auction": 15
        })
        assert response.status_code == 200
        assert response.json() == {
            "treasure": {
                "treasure_id": 1,
                "treasure_name": "treasure-a",
                "colour": "turquoise",
                "age": 200,
                "cost_at_auction": 15,
                "shop_id": 1
            }
        }

    """
    Error handling considerations for PATCH "/api/treasures/:treasure_id" are tested below:
    """
    """
    Path is incorrect; 404 handled by FastAPI
    """
    def test_404_if_path_is_incorrect(self, client):
        response = client.patch("/api/treasure/1", json={
            "cost_at_auction": 15
        })
        assert response.status_code == 404

    """
    Method does not exist; 405 handled by FastAPI
    """
    def test_405_if_method_does_not_exist(self, client):
        response = client.post("/api/treasures/1", json={
            "cost_at_auction": 15
        })
        assert response.status_code == 405

    """
    Treasure ID parameter does not exist; custom 404 implemented
    """
    def test_custom_404_if_treasure_id_does_not_exist(self, client):
        response = client.patch("/api/treasures/500", json={
            "cost_at_auction": 15
        })
        assert response.status_code == 404
        assert response.json() == {
            "detail": "No treasure found with given ID: 500"
        }

    """
    422s handled by FastAPI
    - new price is 0 or below
    - request body is the wrong type
    - request body is the correct type, but empty
    - request body contains a key that is not allowed
    - request body contains a value that is not the correct type
    """
    def test_422_for_invalid_request_body(self, client):
        response = client.patch("/api/treasures/1", json={
            "cost_at_auction": -50
        })
        assert response.status_code == 422

        response = client.patch("/api/treasures/1", json="hi")
        assert response.status_code == 422

        response = client.patch("/api/treasures/1", json={})
        assert response.status_code == 422  

        response = client.patch("/api/treasures/1", json={
            "colour": 15
        })
        assert response.status_code == 422

        response = client.patch("/api/treasures/1", json={
            "cost_at_auction": "fifteen"
        })
        assert response.status_code == 422


class TestDeleteTreasure:
    def test_204_treasure_has_been_deleted(self, client):
        """
        Test verifies:
        - status code
        - remaining treasure data does not contain a record with the id of the deleted treasure
        """
        response = client.delete("/api/treasures/1")
        assert response.status_code == 204

        response = client.get("/api/treasures")
        treasures = response.json()["treasures"]
        assert any(treasure["treasure_id"] == 1 for treasure in treasures) is False

    """
    Error handling considerations for the DELETE "/api/treasures/:treasure_id are below, except for:
    - Method does not exist; tested above for PATCH "/api/treasures/:treasure_id" as base endpoint is the same
    """
    """
    Path is invalid; 404 handled by FastAPI
    """
    def test_404_if_path_is_invalid(self, client):
        response = client.delete("/api/treasure/1")
        assert response.status_code == 404

    """
    Treasure parameter does not exist; custom 404 implemented
    """
    def test_404_if_treasure_does_not_exist(self, client):
        response = client.delete("/api/treasures/50")
        assert response.status_code == 404
        assert response.json() == {
            "detail": "No treasure found with given ID: 50"
        }

    """
    Parameter is wrong type; 422 handled by FastAPI
    """
    def test_422_if_parameter_is_wrong_type(self, client):
        response = client.delete("/api/treasures/one")
        assert response.status_code == 422


class TestGetAllShops:
    def test_200_returns_formatted_treasures(self, client):
        response = client.get("/api/shops")
        shops = response.json()["shops"]
        assert response.status_code == 200
        assert len(shops) == 11
        for shop in shops:
            assert type(shop["shop_id"]) ==  int
            assert type(shop["shop_name"]) == str
            assert type(shop["slogan"]) == str
            assert type(shop["stock_value"]) ==  float
        assert shops[0]["stock_value"] == 2421.98
        assert shops[1]["stock_value"] == 1015.98
        