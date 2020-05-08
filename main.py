import sqlite3
from fastapi import FastAPI, HTTPException


app = FastAPI()


@app.on_event('startup')
async def startup():
    app.db_connection = sqlite3.connect('chinook.db')

@app.on_event('shutdown')
async def shutdown():
    app.db_connection.close() 


@app.get('/tracks')
async def list_of_objects(page: int = 0, per_page: int = 10):
	app.db_connection.row_factory = sqlite3.Row
	tracks = app.db_connection.execute(
		'SELECT * FROM tracks ORDER BY TrackId').fetchall()
	current_tracks = data[per_page * page:per_page * (page+1)] 
	return current_tracks
