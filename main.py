'''This module is the entrypoint for the `Cat's Rare Treasures` FastAPI app.'''
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from db.connection import connect_to_db
from pg8000.native import DatabaseError, identifier, literal


app = FastAPI()


@app.get("/api/treasures")
def get_all_treasures(sort_by: str = "age", order: str = "asc", colour: str = None):
    if not sort_by:
        sort_by = "age"
    elif sort_by not in {"age", "cost_at_auction", "treasure_name"}:
        handle_invalid_query("sort_by", sort_by)
    
    if not order:
        order = "ASC"
    elif order not in {"asc", "desc"}:
        handle_invalid_query("order", order)
    
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
            select_query += f"""WHERE colour = {literal(colour)}"""

        select_query += f"""ORDER BY treasures.{identifier(sort_by)} {identifier(order)};"""

        treasures_data = db.run(sql=select_query)

        if not treasures_data:
            handle_invalid_query("colour", colour)

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


@app.exception_handler(DatabaseError)
def handle_db_error(request: Request, exc: DatabaseError):
    print(exc)
    raise HTTPException(status_code=500, detail="Server error: logged for investigation")

def handle_invalid_query(query_key, query_value):
    raise HTTPException(status_code=400, detail=f"Invalid {query_key} value ({query_value}) provided")