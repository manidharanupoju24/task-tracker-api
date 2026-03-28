# Task Tracker API

FastAPI backend for Task Tracker. Handles authentication via Supabase Auth and all task CRUD operations backed by Supabase PostgreSQL.

## Tech Stack

| Layer | Choice |
|-------|--------|
| Framework | FastAPI 0.115 |
| Server | Uvicorn |
| Auth | Supabase Auth (JWT Bearer tokens) |
| Database | Supabase PostgreSQL |
| Validation | Pydantic v2 |
| Rate Limiting | SlowAPI |

## Project Structure

```
app/
├── routers/
│   ├── auth.py       # /auth/signup, /signin, /signout
│   └── todos.py      # /todos/ CRUD endpoints
├── auth.py           # JWT validation via Supabase
├── config.py         # Environment variable settings
├── limiter.py        # Rate limiter setup (slowapi)
├── models.py         # Pydantic request/response models
└── supabase_client.py  # Supabase admin client
main.py               # FastAPI app entry point
supabase_setup.sql    # Database schema + RLS policies
requirements.txt
```

## API Endpoints

### Auth — `/auth`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/signup` | Create account (rate limited: 5/min) |
| `POST` | `/auth/signin` | Sign in, returns JWT access token (rate limited: 5/min) |
| `POST` | `/auth/signout` | Invalidate session (requires Bearer token) |

### Todos — `/todos`

All todo endpoints require `Authorization: Bearer <token>`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/todos/` | Fetch all todos (paginated). Query params: `limit` (1–100, default 50), `offset` (default 0) |
| `POST` | `/todos/` | Create a new todo |
| `PATCH` | `/todos/{id}` | Update a todo (must be owner) |
| `DELETE` | `/todos/{id}` | Delete a todo (must be owner) |

### Other

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |

## Getting Started

### Prerequisites

- Python 3.12
- A Supabase project with the schema from `supabase_setup.sql` applied

### 1. Set up the database

Run `supabase_setup.sql` in your Supabase SQL editor to create the `todos` table, RLS policies, indexes, and triggers.

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret        # optional, for legacy HS256
ALLOWED_ORIGINS=http://localhost:3000       # comma-separated for multiple
```

### 3. Create a virtual environment and install dependencies

```bash
python3.12 -m venv venv312
source venv312/bin/activate
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn main:app --reload --port 8000
```

### 5. Open the API docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Schema

Key columns on the `todos` table:

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | UUID | References `auth.users` |
| `text` | TEXT | Task title |
| `completed` | BOOLEAN | Completion status |
| `priority` | TEXT | `low` / `medium` / `high` |
| `category` | TEXT | `personal` / `work` / `shopping` / `other` |
| `due_date` | DATE | Optional due date |
| `notes` | TEXT | Optional notes/description |
| `created_by_email` | TEXT | Email of creator |
| `created_by_name` | TEXT | Display name of creator |
| `created_at` | TIMESTAMPTZ | Auto-set on insert |
| `updated_at` | TIMESTAMPTZ | Auto-updated via trigger |

## Security

- **Row Level Security** — users can read all todos but can only insert/update/delete their own
- **Ownership checks** — PATCH and DELETE verify ownership at the application layer, returning `403` if the requesting user is not the owner
- **Rate limiting** — auth endpoints are limited to 5 requests/minute per IP
- **Supabase service role key** — used server-side only, never exposed to the frontend
