import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse

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
    current_tracks = tracks[per_page * page:per_page * (page+1)] 
    return current_tracks

'''
@app.get('/tracks')
async def list_of_objects(page: int = 0, per_page: int = 10):
	app.db_connection.row_factory = sqlite3.Row 
	current_tracks = app.db_connection.execute(
		'SELECT * FROM tracks LIMIT :page OFFSET :offset ORDER BY TrackId', {page: per_page, offset: per_page * page}).fetchall()
    	return current_tracks
'''

@app.get('/tracks/composers/')
async def composers(composer_name: str):
	app.db_connection.row_factory = sqlite3.Row
	current_tracks = app.db_connection.execute(
		"SELECT Name FROM tracks WHERE Composer= :composer_name ORDER BY Name",
		{'composer_name': composer_name}).fetchall()

	list = []
	for elem in current_tracks:
		list.append(elem["Name"])

	if len(current_tracks) == 0:
		raise HTTPException (status_code=404, detail = {"error": "Not found."})
	return list



class album_data(BaseModel):
	title: str
	artist_id: int = 1

class albums_entry:
	AlbumId: int
	Title: str
	ArtistId: str

class customer_data(BaseModel):
	company: str = None
	address: str = None
	city: str = None
	state: str = None
	country: str = None
	postalcode: str = None
	fax: str = None

@app.get('/albums/{album_id}')
async def read_albums(album_id: int):
	app.db_connection.row_factory = sqlite3.Row
	data = app.db_connection.execute("SELECT * FROM albums WHERE AlbumId=:album_id", {"album_id": album_id}).fetchall()
	return data[0]

@app.post('/albums')
async def create_album(album_rq: album_data):

	app.db_connection.row_factory = sqlite3.Row

	check_artist = app.db_connection.execute("SELECT Name FROM artists WHERE ArtistId=:artistId", 
		{"artistId": album_rq.artist_id}).fetchone()

	if check_artist != None:

		current_data = app.db_connection.execute("INSERT INTO albums (Title, ArtistId) VALUES (:title, :artistId)",
			{"title": album_rq.title, "artistId": album_rq.artist_id})
		app.db_connection.commit()
		

		new_album_id = current_data.lastrowid
		app.db_connection.row_factory = sqlite3.Row
		get_data = app.db_connection.execute("SELECT * FROM albums WHERE AlbumId=:new_album_id", {"new_album_id": new_album_id}).fetchall()

		temp = albums_entry()
		for elem in get_data:
			temp.AlbumId = elem["AlbumId"]
			temp.Title = elem["Title"]
			temp.ArtistId = elem["ArtistId"]

		if get_data != None:
			return JSONResponse (status_code = 201, content = {"AlbumId": temp.AlbumId, "Title": temp.Title, "ArtistId": temp.ArtistId})
				
	else:
		raise HTTPException ( status_code = 404, detail= {"error": "Not found."})
		
