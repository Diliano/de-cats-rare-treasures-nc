'''This module is the entrypoint for the `Cat's Rare Treasures` FastAPI app.'''
from fastapi import FastAPI, Request, HTTPException
from db.connection import connect_to_db
from pg8000.native import DatabaseError


app = FastAPI()


@app.get("/api/treasures")
def get_all_treasures():
    db = None
    try:
        db = connect_to_db()
        select_query = f"""
            SELECT 
                treasures.treasure_id, treasures.treasure_name, treasures.colour,
                treasures.age, treasures.cost_at_auction, shops.shop_name
            FROM treasures
            JOIN shops ON treasures.shop_id = shops.shop_id
            ORDER BY treasures.age;
        """
        treasures_data = db.run(sql=select_query)
        column_names = [c["name"] for c in db.columns]
        formatted_data = [dict(zip(column_names, treasure)) for treasure in treasures_data]
        return {"treasures": formatted_data}
    finally:
        if db:
            db.close()


@app.exception_handler(DatabaseError)
def handle_db_error(request: Request, exc: DatabaseError):
    print(exc)
    raise HTTPException(status_code=500, detail="Server error: logged for investigation")