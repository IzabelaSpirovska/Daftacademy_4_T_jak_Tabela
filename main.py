from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
import sqlite3
app = FastAPI()

@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect('chinook.db')
    app.db_connection.row_factory = sqlite3.Row


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/tracks")
async def tracks(page: int = 0, per_page:int = 10):
    cursor = app.db_connection.cursor()
    data = cursor.execute("SELECT * FROM tracks ORDER BY TrackId LIMIT :per_page OFFSET :per_page*:page",
        {'page': page, 'per_page': per_page}).fetchall()
    return data
