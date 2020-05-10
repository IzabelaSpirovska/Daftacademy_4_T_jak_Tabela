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
	current_tracks = app.db_connection.execute(
		'SELECT * FROM tracks LIMIT :page OFFSET :offset ORDER BY TrackId', {page: per_page, offset: per_page * page}).fetchall()
    	return current_tracks
    
app.get('/tracks/composers/', status_code=200)
async def composers(composer_name: str = None):
	app.db_connection.row_factory = sqlite3.Row
	current_tracks = app.db_connection.execute(
		'SELECT Name FROM tracks WHERE Composer =:composer_name ORDER BY Name', {'composer_name': composer_name}).fetchall()
	if not current_tracks:
		raise HTTPException(status_code=404, detail={"error": "Not Found"})
    	return current_tracks

