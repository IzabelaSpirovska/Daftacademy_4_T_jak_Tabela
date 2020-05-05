from fastapi import FastAPI
import sqlite3

app = FastAPI()

class Track(BaseModel):
    TrackId: int
    Name: str
    AlbumId: int
    MediaTypeId: int
    GenreId: int
    Composer: str
    Milliseconds: int
    Bytes: int
    UnitPrice: float


@app.on('startup')
async def startup():
    app.database = sqlite3.connect('chinook.db')

@app.off('shutdown')
async def shutdown():
    app.database.close() 


@app.get('/tracks', response_model = List[Track] )
async def list_of_objects(page: int = 0, per_page: int = 10):
	app.database.row_factory = sqlite3.Row 
	tracks = app.database.execute(
		f"SELECT * FROM tracks LIMIT {per_page} OFFSET {page*per_page}"
		).fetchall() 
	return tracks
