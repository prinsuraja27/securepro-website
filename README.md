# SecurePro Website - FastAPI Full Stack Starter

A professional ready-to-run website with FastAPI backend, SQLite database, JWT login, password hashing, contact form, newsletter, admin messages, rate limiting and security headers.

## Features

- Responsive professional landing page
- Register / login system
- JWT authentication
- Secure password hashing
- Contact form saves data in database
- Newsletter email collection
- Admin-only message dashboard API
- SQLite database by default
- Security headers middleware
- Basic rate limiting for sensitive routes
- Environment-based configuration

## Run Locally

```bash
python -m venv venv

# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API Docs:

```text
http://127.0.0.1:8000/docs
```

## Important Before Public Deployment

1. Change `SECRET_KEY` in `.env` to a long random value.
2. Set `ENV=production`.
3. Update `ALLOWED_ORIGINS` and `ALLOWED_HOSTS` to your real domain.
4. Use HTTPS on the server.
5. For bigger traffic, use PostgreSQL instead of SQLite.
6. Do not upload `.env` publicly.

## First Admin User

The first registered user becomes `admin`. After that, all new users become normal `user` accounts.

## Main API Endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/contact`
- `POST /api/newsletter`
- `GET /api/admin/messages` admin only
- `GET /api/health`

## Project Structure

```text
securepro_website/
  app/
    main.py
    database.py
    models.py
    schemas.py
    security.py
    deps.py
    static/
      index.html
      assets/
        style.css
        app.js
  requirements.txt
  .env.example
  README.md
```
