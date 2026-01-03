# Mini Social Media Feed API

> A small REST API implementing a mini social media feed.

This project provides endpoints to create and manage users and posts (including image upload and likes). It is built with FastAPI and SQLAlchemy and uses Pydantic settings for configuration.

## Features
- Create, update, delete users
- Create, update, delete posts
- Upload and delete post images
- Like / unlike posts
- Full-text search for posts and users

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=flat-square&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat-square&logo=fastapi&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red?style=flat-square&logo=sqlalchemy&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-2.0+-e92063?style=flat-square&logo=pydantic&logoColor=white) ![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI-green?style=flat-square&logo=uvicorn&logoColor=white)

- Python 3.10+
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn (ASGI server)

## Requirements
- Create and activate a virtual environment
- Install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you don't have a `requirements.txt` generated yet, install the main deps directly:

```powershell
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings
```

## Environment variables
The project uses `pydantic_settings.Settings`. Set the following at minimum:

- `DATABASE_URL` — the SQLAlchemy database URL for your database (e.g. `postgresql+psycopg2://user:pass@localhost:5432/dbname`).

You can create a `.env` file in the project root with:

```
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/dbname
```

## Run the app (development)

```powershell
# from project root (Altschool-Project)
uvicorn app.main:app --reload
```

Open the interactive docs at: `http://127.0.0.1:8000/docs` (Swagger UI) or `http://127.0.0.1:8000/redoc`.

### Users (example routes)
- `GET /users/` — list users (supports `offset`, `limit`, `sort`, `order`).
- `GET /users/?q=...` — search users by username.
- `GET /users/{username}/` — get user by username.
- `GET /users/{user_id}/` — get user by id.
- `POST /users/` — create user (send JSON payload according to `UserCreateV1` schema).
- `PATCH /users/{user_id}/` — update user (send only fields to update).
- `DELETE /users/{user_id}/` — delete user.

### Posts (example routes)
- `GET /posts/feed/` — paginated feed (supports `offset`, `limit`, `sort`, `order`).
- `GET /posts/?q=...` — search posts by title.
- `GET /post/{post_id}/` — get single post by id.
- `POST /posts/` — create a post (JSON matching `PostCreateV1`).
- `POST /posts/images/upload/` — upload images for posts (multipart form upload of files).
- `POST /posts/{post_id}/like/` — like a post.
- `PATCH /posts/{post_id}/` — update a post.
- `DELETE /posts/{post_id}/unlike/{user_id}/` — remove a like.
- `DELETE /posts/{post_id}/images/{image_name}/` — delete a post image.
- `DELETE /posts/{post_id}/` — delete a post.

## Database
- Ensure `DATABASE_URL` points to a running DB (Postgres recommended for full-text search used in services).
- If using Postgres full-text search features in services, make sure the DB has the required extensions and tables.
- If you use Alembic or migrations, run those here (project does not include migrations by default in this README).

## Troubleshooting
- If you hit import errors, confirm your virtual env is active and `PYTHONPATH` includes project root (running from project root is recommended).
- For DB connection issues, confirm `DATABASE_URL` and that the DB server accepts connections from your machine.
