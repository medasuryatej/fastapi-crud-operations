from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Post(BaseModel):
    # defines schema and performs basic validation
    title: str
    content: str
    published: bool = True # optional field
    rating: Optional[int] = None


# connecting to Postgres database
check_again = 0

while True:
    try:
        conn = psycopg2.connect(host='localhost', 
                                database='fastapi',
                                user='postgres', 
                                password='postgres@9195',
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection successful")
        break
    except Exception as error:
        print(f"Connecting to database failed: {error}")
        if check_again == 3:
            break
        time.sleep(2)
        check_again += 1

my_posts = [
    {
        "id": 1,
        "title": "Sample Title",
        "content": "Sample post content"
    }
]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/") # path operation - sending a get request
async def root():
    # automatically got converted to JSON
    return {"message": "Hello World! Surya"}


@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    # print(posts)
    return {"data": posts}


# @app.post("/createposts")
def create_posts_old(payload: dict = Body(...)):
    # data extraction from body of payload
    print(payload)
    return {"new_post": f"content: {payload['content']}"}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    # using f strings might lead to sql injection
    cursor.execute("""INSERT INTO posts (title, content, published) \
        VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    # data needs to be committed/saved to reflect in database
    conn.commit()
    return {"data": new_post}


@app.get("/posts/latest")
def get_latest_post():
    # return the latest post
    return {"detail": my_posts[len(my_posts)-1]}


@app.get("/posts/{id}")
def get_post(id: int): #,  response: Response):
    cursor.execute("""SELECT * FROM posts WHERE id=%s""", str(id)) # id needs to be converted back to string
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post {id} not found"
        )
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post {id} not found"}
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts where id=%s RETURNING *""",(str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post {id} not found to delete"
        )
    # return {"message": "post deleted!"}
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",
        (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post {id} not found to update"
        )
    return {"data": updated_post}