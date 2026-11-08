# DigiWill BD — User Registration & Login

The authentication module of DigiWill BD: account registration, email + password
login, JWT session handling (auto refresh, logout), a protected page, and a
bilingual (English / বাংলা) UI.

**Stack:** Django 5 + Django REST Framework + SimpleJWT · React 19 + Vite

## API

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | `/api/auth/register/` | public | Create account, returns user + tokens |
| POST | `/api/auth/login/` | public | Email + password, returns user + tokens |
| POST | `/api/auth/refresh/` | refresh token | New access token (refresh token rotates) |
| POST | `/api/auth/logout/` | access token | Blacklists the refresh token |
| GET / PATCH | `/api/auth/me/` | access token | Current user's profile |

## Run locally

```bash
# backend  (http://localhost:8000)
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# frontend (http://localhost:5173) — in a second terminal
cd frontend
npm install
npm run dev
```

Run the backend tests: `cd backend && python manage.py test`

## Security notes

- Passwords are hashed by Django (PBKDF2) and checked with Django's validators.
- Access tokens last 15 min, refresh tokens 7 days; refresh tokens rotate and old
  ones are blacklisted. Logout blacklists the current one.
- Register and login are rate-limited (10 requests/min).
- Login returns the same error for a wrong password and an unknown email.
- Clients cannot set `is_staff` / `is_superuser` through the API.