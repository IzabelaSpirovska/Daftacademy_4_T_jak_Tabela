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

@app.get("/tracks/composers")
async def comp_name(composer_name: str):
    app.db_connection.row_factory = lambda cursor, x: x[0]
    data = app.db_connection.execute('''SELECT Name 
                                        FROM tracks 
                                        WHERE Composer=:composerName
                                        ORDER BY Name''', {'composerName': composer_name}).fetchall()
    if not data:
        raise HTTPException(status_code=404, detail={"error": "Not Found"})
    return data

class Album(BaseModel):
    title: str
    artist_id: int


@app.post("/albums")
async def add_album(album: Album, response: Response):
    cursor = app.db_connection.cursor()
    data = cursor.execute('''
                            SELECT *
                            FROM artists
                            WHERE ArtistId=:artist_id;''', {'artist_id': album.artist_id}).fetchall()
    if not data:
        raise HTTPException(status_code=404, detail={"error": "Not Found"})
    cursor.execute('''
                    INSERT INTO albums (Title,ArtistId) 
                    VALUES (:title,:artist_id);''', {'title': album.title, 'artist_id': album.artist_id})
    app.db_connection.commit()
    response.status_code = status.HTTP_201_CREATED
    return {"AlbumId": cursor.lastrowid, "Title": album.title, "ArtistId": album.artist_id}

@app.get("/albums/{album_id}")
async def show_album(album_id: int):
    data = app.db_connection.execute('''
                            SELECT *
                            FROM albums
                            WHERE AlbumId = :albumid''',{'albumid': album_id}).fetchone()
    if not data:
        raise HTTPException(status_code=404, detail={"error": "Not Found"})
    return data

class Customer(BaseModel):
    company: str = None
    address: str = None
    city: str = None
    state: str = None
    country: str = None
    postalcode: str = None
    fax: str = None


@app.put("/customers/{customer_id}")
async def modify_customer(customer: Customer,customer_id:int):
    cursor = app.db_connection.cursor()
    data = cursor.execute('''
                            SELECT * 
                            FROM customers 
                            WHERE CustomerId=:customerid''', {'customerid': customer_id}).fetchone()
    if not data:
        raise HTTPException(status_code=404, detail={"error": "Not Found"})
    
    update_data = [f"{key} = '{value}'" for key, value in customer.dict(exclude_unset=True).items()]
    update_data_str = ','.join(update_data)
    
    cursor = app.db_connection.execute('''
                UPDATE customers
                SET
                company = IFNULL(:company,company),
                address = IFNULL(:address, address),
                city = IFNULL(:city,city),
                state = IFNULL(:state,state),
                country = IFNULL(:country,country),
                PostalCode = IFNULL(:postal_code,PostalCode),
                Fax = IFNULL(:fax,Fax)
                WHERE CustomerId = :customer_id''', {"customer_id": customer_id,
                                            "company": customer.company,
                                            "address": customer.address,
                                            "city": customer.city,
                                            "state": customer.state,
                                            "country": customer.country,
                                            "postal_code":customer.postalcode,
                                            "fax": customer.fax})
    app.db_connection.commit()
    finally_customer = cursor.execute('''SELECT * 
                                    FROM 
                                    customers 
                                    WHERE 
                                    CustomerId = :customer_id
                                    ''', {"customer_id": customer_id}).fetchone()
    return finally_customer


@app.get("/sales")
async def sel_method(category: str):
    if category == "customers":
        data = app.db_connection.execute('''
                                SELECT
                                    invoices.CustomerId,
                                    Email,
                                    Phone,
                                    ROUND(SUM(Total), 2) AS Sum
                                FROM
                                    customers
                                JOIN invoices ON customers.CustomerId = invoices.CustomerId
                                GROUP BY
                                    invoices.CustomerId
                                ORDER BY
                                    Sum DESC,
                                    invoices.CustomerId ASC''').fetchall()
        return data
    if category == "genres":
        data = app.db_connection.execute('''
                                        SELECT
                                            genres."Name",
                                            SUM(Quantity) as Sum
                                        FROM invoice_items
                                        JOIN tracks ON invoice_items.TrackId = tracks.TrackId
                                        JOIN genres on tracks.GenreId = genres.GenreId
                                        GROUP BY
                                            tracks.GenreId 
                                        ORDER BY
                                            Sum DESC,
                                            genres."Name" ASC
                                        ''').fetchall()
        return data
    else:
        raise HTTPException(status_code=404, detail={"error": "Not Found"})


@app.get("/")
async def main_page():
    return{'message': 'hello on [/] page'}
