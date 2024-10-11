'''This module is the entrypoint for the `Cat's Rare Treasures` FastAPI app.'''
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from db.connection import connect_to_db
from pg8000.native import DatabaseError, identifier, literal


app = FastAPI()


class SortBy(Enum):
    age = "age"
    cost_at_auction = "cost_at_auction"
    treasure_name = "treasure_name"

class Order(Enum):
    asc = "asc"
    desc = "desc"

class Colour(Enum):
    turquoise = "turquoise"
    mikado = "mikado"
    ivory = "ivory"
    onyx = "onyx"
    carmine = "carmine"
    cobalt = "cobalt"
    magenta = "magenta"
    gold = "gold"
    azure = "azure"
    silver = "silver"
    khaki = "khaki"
    saffron = "saffron"
    burgundy = "burgundy"

@app.get("/api/treasures")
def get_all_treasures(sort_by: SortBy = SortBy.age, order: Order = Order.asc, colour: Colour = None):
    
    db = None

    try:
        db = connect_to_db()

        select_query = f"""
            SELECT 
                treasures.treasure_id, treasures.treasure_name, treasures.colour,
                treasures.age, treasures.cost_at_auction, shops.shop_name
            FROM treasures
            JOIN shops ON treasures.shop_id = shops.shop_id
        """

        if colour:
            select_query += f"""WHERE colour = {literal(colour.value)}"""

        select_query += f"""ORDER BY treasures.{identifier(sort_by.value)} {identifier(order.value)};"""

        treasures_data = db.run(sql=select_query)
        column_names = [c["name"] for c in db.columns]
        formatted_data = [dict(zip(column_names, treasure)) for treasure in treasures_data]
        return {"treasures": formatted_data}
    finally:
        if db:
            db.close()


class NewTreasure(BaseModel):
    treasure_name: str
    colour: str
    age: int
    cost_at_auction: float
    shop_id: int

@app.post("/api/treasures", status_code=201)
def add_new_treasure(new_treasure: NewTreasure):
    db = None

    try:
        db = connect_to_db()

        insert_query = f"""
            INSERT INTO treasures
                (treasure_name, colour, age, cost_at_auction, shop_id)
            VALUES
                ({literal(new_treasure.treasure_name)}, {literal(new_treasure.colour)}, {literal(new_treasure.age)},
                {literal(new_treasure.cost_at_auction)}, {literal(new_treasure.shop_id)})
            RETURNING *;
        """

        treasure_data = db.run(sql=insert_query)[0]
        column_names = [c["name"] for c in db.columns]
        formatted_data = dict(zip(column_names, treasure_data))
        return {"treasure": formatted_data}
    finally:
        if db:
            db.close()


class UpdatedTreasurePrice(BaseModel):
    cost_at_auction: float = Field(gt=0)

@app.patch("/api/treasures/{treasure_id}")
def update_treasure_price(treasure_id: int, updated_treasure_price: UpdatedTreasurePrice):
    db = None
    try:
        db = connect_to_db()

        update_query = f"""
            UPDATE treasures
            SET cost_at_auction = {literal(updated_treasure_price.cost_at_auction)}
            WHERE treasure_id = {literal(treasure_id)}
            RETURNING *;
        """

        treasure_data = db.run(sql=update_query)[0]
        column_names = [c["name"] for c in db.columns]
        formatted_data = dict(zip(column_names, treasure_data))
        return {"treasure": formatted_data}
    except IndexError:
        raise HTTPException(status_code=404, detail=f"No treasure found with given ID: {treasure_id}")
    finally:    
        if db:
            db.close()


@app.delete("/api/treasures/{treasure_id}", status_code=204)
def delete_treasure(treasure_id: int):
    db = None
    try:
        db = connect_to_db()
        db.run(f"""DELETE FROM treasures WHERE treasure_id = {literal(treasure_id)}""")
    finally:
        if db:
            db.close()


@app.exception_handler(DatabaseError)
def handle_db_error(request: Request, exc: DatabaseError):
    print(exc)
    raise HTTPException(status_code=500, detail="Server error: logged for investigation")