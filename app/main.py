from turtle import update
from typing import Optional
from fastapi import Body, Depends, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models, schemas
from .database import engine, get_db
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# connecting to Postgres database
check_again = 0

while True:
    try:
        conn = psycopg2.connect(host='localhost', 
                                database='fastapi',
                                user='postgres', 
                                password='postgres9195',
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
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    # print(posts)
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    '''
    # using f strings might lead to sql injection
    cursor.execute("""INSERT INTO posts (title, content, published) \
        VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    # data needs to be committed/saved to reflect in database
    conn.commit()
    '''
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    # print(post)
    new_post = models.Post(**post.dict()) # unpacks the fields
    db.add(new_post)
    db.commit()
    db.refresh(new_post) # equivalent to RETURNING * in SQL command
    return {"data": new_post}


@app.get("/posts/latest")
def get_latest_post():
    # return the latest post
    return {"detail": my_posts[len(my_posts)-1]}


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)): #,  response: Response):
    # cursor.execute("""SELECT * FROM posts WHERE id=%s""", str(id)) # id needs to be converted back to string
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id==id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post {id} not found"
        )
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post {id} not found"}
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts where id=%s RETURNING *""",(str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    deleted_post = db.query(models.Post).filter(models.Post.id==id)

    if deleted_post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post {id} not found to delete"
        )
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",
    #     (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id==id)
    updated_post = post_query.first()

    if updated_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post {id} not found to update"
        )

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return {"data": post_query.first()}