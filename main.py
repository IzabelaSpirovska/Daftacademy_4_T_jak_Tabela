import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse


class album_data(BaseModel):
	title: str
	artist_id: int = 1

class albums_entry:
	AlbumId: int
	Title: str
	ArtistId: str

class customer_data(BaseModel):
	company: str 
	address: str 
	city: str 
	state: str 
	country: str 
	postalcode: str 
	fax: str 

app = FastAPI()


#--- TASK 1 -----------------------------------------------------------
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


#--- TASK 2 -----------------------------------------------------------
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


#--- TASK 3 -----------------------------------------------------------
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

		current_data = app.db_connection.execute("INSERT INTO albums (Title, ArtistId) VALUES (:title, :artistId)", {"title": album_rq.title, "artistId": album_rq.artist_id})
		app.db_connection.commit()
		

		new_album_id = current_data.lastrowid
		app.db_connection.row_factory = sqlite3.Row
		get_data = app.db_connection.execute("SELECT * FROM albums WHERE AlbumId=:new_album_id", {"new_album_id": new_album_id}).fetchall()

		extract = albums_entry()
		for elem in get_data:
			extract.AlbumId = elem["AlbumId"]
			extract.Title = elem["Title"]
			extract.ArtistId = elem["ArtistId"]

		if get_data != None:
			return JSONResponse (status_code = 201, content = {"AlbumId": extract.AlbumId, "Title": extract.Title, "ArtistId": extract.ArtistId})
				
	else:
		raise HTTPException (status_code = 404, detail= {"error": "Not found."})


#--- TASK 4 -----------------------------------------------------------
@app.put('/customers/{customer_id}')
async def edit_customer(customer_id: int, edit_rq: customer_data):
	app.db_connection.row_factory = sqlite3.Row

	check_customer = app.db_connection.execute("SELECT FirstName FROM customers WHERE CustomerId=:customer_id", {"customer_id": customer_id}).fetchone()
	if check_customer != None:
		search = {k: v for k, v in edit_rq.__dict__.items() if v is not None}
		for key, value in search.items():
			dummy_key = key.capitalize()
			sql_command = "UPDATE customers SET " + str(dummy_key) + " = '" + str(value) + "' WHERE CustomerID = " + str(customer_id)
			edit = app.db_connection.execute(sql_command)
			app.db_connection.commit()
		current_command = app.db_connection.execute("SELECT * FROM customers WHERE CustomerId=:customer_id", {"customer_id": customer_id}).fetchone()
		return current_command
	else:
		raise HTTPException (status_code=404, detail= {"error": "Not found."}
		
