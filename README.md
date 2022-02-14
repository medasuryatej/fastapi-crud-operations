# fastapi-crud-operations
Basic CRUD operations performed on a Postgres database created with FastAPI and tested using PostMan

Requirements
```
pip install fastapi[all] psycopg2==2.9.3 pydantic==1.9.0 SQLAlchemy==1.4.31
```

Software Required
```
PostGreSQL  Visual Studio Code  Postman
```

Command to run server
```
uvicorn main:app --reload
```

About CRUD
```
Create POST /posts @app.post("/posts)

Read GET  /posts/:id @app.get("/posts/{id})
     GET  /posts @app.get("/posts)

Update PUT/PATCH  /posts/:id @app.put("/posts/{id})

Delete DELETE  /posts/:id @app.delete("/posts/{id})
```

PostMan test routes
```
GET all posts: http://127.0.0.1:8000/posts
GET single post: http://127.0.0.1:8000/posts/<post_id>
POST create post: http://127.0.0.1:8000/posts
  # body
  {
    "title": "Welcome to Wano",
    "content": "Hey Monkey D Luffy",
    "published": true
  }
DELETE post: http://127.0.0.1:8000/posts/<post_id>
UPDATE post: http://127.0.0.1:8000/posts/<post_id>
  # body
  {
    "title": "Welcome to Onigashima",
    "content": "I will be the pirate king"
  }
```
