from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()


@app.on_event('startup')
async def startup():
    app.database = sqlite3.connect('chinook.db')

@app.on_event('shutdown')
async def shutdown():
    app.database.close() 


@app.get('/track')
async def list_of_objects(page: int = 0, per_page: int = 10):
	app.database.row_factory = sqlite3.Row 
	tracks = app.database.execute(
		f"SELECT * FROM tracks LIMIT {per_page} OFFSET {page*per_page}"
		).fetchall() 
	return tracks
