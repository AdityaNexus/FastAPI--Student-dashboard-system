# Student Dashboard System

A student-record management application built with FastAPI, PostgreSQL,
SQLAlchemy, Docker Compose, and a vanilla HTML/CSS/JavaScript frontend.

The application supports creating, viewing, updating, deleting, filtering,
sorting, and paginating student records. PostgreSQL stores the records
persistently, while FastAPI exposes the API and serves the web dashboard.

## Architecture

```mermaid
flowchart LR
    Browser["Browser<br/>http://localhost:8000"] -->|HTTP| API["FastAPI API<br/>student-fastapi"]
    API -->|SQLAlchemy / psycopg<br/>db:5432| DB["PostgreSQL 17<br/>student-postgres-db"]
    DB --> Volume[("postgres_data<br/>persistent volume")]
    API --> Web["web/<br/>HTML + CSS + JavaScript"]
```

### How the containers communicate

Docker Compose creates a private network for the services:

```text
Browser
  |
  | localhost:8000
  v
FastAPI container (student-fastapi)
  |
  | postgresql+psycopg://student_user:student_password@db:5432/student_db
  v
PostgreSQL container (student-postgres-db)
  |
  v
postgres_data volume
```

The API must use `db` as the database hostname inside Compose. `localhost`
inside the API container would refer to the API container itself, not
PostgreSQL.

## Project layout

```text
C:\FastAPI
├── postgress-infra
│   ├── compose.yml       # PostgreSQL and FastAPI services
│   ├── Dockerfile        # FastAPI image definition
│   ├── main.py           # Database-backed FastAPI application
│   └── README.md         # Container-specific notes
├── web
│   ├── index.html         # Dashboard page
│   ├── app.js             # Frontend API calls and interactions
│   └── styles.css         # Dashboard styling
├── templates              # Older server-rendered examples
├── revision              # Earlier learning/example code
├── pyproject.toml         # Local Python project dependencies
└── README.md              # This documentation
```

The production-style Compose image copies only `postgress-infra/main.py` and
the `web/` directory. The older example folders are not required by the
containerized application.

## Requirements

- Docker Desktop with Docker Compose
- PowerShell on Windows
- Ports `8000` and `5432` available

You do not need to install Python or PostgreSQL on the host to run the
containerized stack.

## Start the application

From the repository root:

```powershell
cd C:\FastAPI
docker compose -f postgress-infra\compose.yml up --build
```

Or start it in the background:

```powershell
docker compose -f postgress-infra\compose.yml up -d --build
```

The PostgreSQL healthcheck runs first. The API starts only after PostgreSQL is
healthy, and the FastAPI startup hook also retries the database connection.

Open the dashboard at:

```text
http://localhost:8000/
```

Open interactive API documentation at:

```text
http://localhost:8000/docs
```

Use `localhost`, not `0.0.0.0`, in the browser.

## Stop the application

Stop and remove the containers and Compose network:

```powershell
docker compose -f postgress-infra\compose.yml down
```

This keeps the `postgres_data` volume and its records.

Stop the containers and delete all stored database records:

```powershell
docker compose -f postgress-infra\compose.yml down -v
```

The `-v` option is destructive for the database data. The next startup
creates a new empty database and table.

## Useful Docker commands

View container status:

```powershell
docker compose -f postgress-infra\compose.yml ps
```

View API logs:

```powershell
docker compose -f postgress-infra\compose.yml logs -f api
```

View PostgreSQL logs:

```powershell
docker compose -f postgress-infra\compose.yml logs -f db
```

Rebuild after changing Python or frontend files:

```powershell
docker compose -f postgress-infra\compose.yml up -d --build
```

Validate the Compose file without starting services:

```powershell
docker compose -f postgress-infra\compose.yml config
```

## Database configuration

The Compose database uses:

```text
Database: student_db
User:     student_user
Password: student_password
Host:     db (inside Compose)
Port:     5432
```

The API receives this connection string from Compose:

```text
postgresql+psycopg://student_user:student_password@db:5432/student_db
```

The database is stored in the named Docker volume `postgres_data`, so normal
`docker compose down` and container recreation do not delete student records.
The API creates the `student_records` table automatically if it does not
already exist. It does not seed or reset data automatically.

For a real deployment, replace the example database password with a secret and
avoid committing credentials to source control.

## API endpoints

### Current database-backed endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/students` | List students with filtering, sorting, and pagination |
| `GET` | `/students/{student_id}` | Get one student |
| `POST` | `/CreateStudent` | Create a student |
| `PUT` | `/updateStudent/{student_id}` | Update a student |
| `DELETE` | `/deleteStudent/{student_id}` | Delete a student |

Example request:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/CreateStudent `
  -ContentType "application/json" `
  -Body '{"id":"001","name":"John Doe","age":20,"course":"Computer Science","email":"john@example.com","marks":85}'
```

Example list request:

```powershell
Invoke-RestMethod "http://localhost:8000/students?page=1&limit=10&sort_by=marks&order=desc"
```

### Frontend compatibility endpoints

The existing `web/app.js` uses these routes, which are also provided by
`postgress-infra/main.py`:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/student` | Get all students as an ID-keyed object |
| `GET` | `/student/{student_id}` | Find one student |
| `GET` | `/paginate` | Paginated dashboard data |
| `GET` | `/filter?course=...` | Filter by course |
| `GET` | `/sort?sort_by=...&order=...` | Sort students |
| `POST` | `/create` | Create from the dashboard |
| `PUT` | `/update/{student_id}` | Edit from the dashboard |
| `DELETE` | `/delete/{student_id}` | Delete from the dashboard |

These compatibility routes allow the existing frontend to work without
rewriting the dashboard around the newer endpoint names.

## Student model

Each student record contains:

```json
{
  "id": "001",
  "name": "John Doe",
  "age": 20,
  "course": "Computer Science",
  "email": "john@example.com",
  "marks": 85
}
```

Validation includes:

- Required student ID, name, age, course, email, and marks
- Age between `0` and `150`
- Marks between `0` and `100`
- Valid email format
- Names containing letters and spaces
- Unique student IDs and email addresses
- Computed grades in API responses

## Local development without Docker

The supported complete workflow is Docker Compose because it provides both
services consistently. For API-only development, install the project
dependencies and provide a reachable PostgreSQL `DATABASE_URL`:

```powershell
cd C:\FastAPI
uv sync
$env:DATABASE_URL = "postgresql+psycopg://student_user:student_password@localhost:5432/student_db"
Set-Location postgress-infra
uv run uvicorn main:app --reload
```

Because `postgress-infra` contains a hyphen, direct local module execution may
be less convenient than running the Compose image. Docker Compose is the
recommended path.

## Troubleshooting

### The browser shows a connection error

Check that the containers are running:

```powershell
docker compose -f postgress-infra\compose.yml ps
```

If they are stopped, start them:

```powershell
docker compose -f postgress-infra\compose.yml up -d --build
```

Use `http://localhost:8000/`, not `http://0.0.0.0:8000/`.

### The API container exits

Read its logs:

```powershell
docker compose -f postgress-infra\compose.yml logs api
```

Then check the PostgreSQL health status:

```powershell
docker compose -f postgress-infra\compose.yml ps
```

The database should show `healthy`.

### Port 8000 is already in use

Find the process using the port:

```powershell
Get-NetTCPConnection -LocalPort 8000
```

Stop that application or change the host side of the API mapping in
`postgress-infra/compose.yml`, for example `8001:8000`, and then open
`http://localhost:8001/`.

### Port 5432 is already in use

If PostgreSQL is already running on the host, either stop it or change the
host side of the database mapping. The API container still connects to the
Compose service as `db:5432`.

### Data disappeared

Do not use `docker compose down -v` unless you intentionally want to delete the
database volume. Check existing volumes with:

```powershell
docker volume ls
```

## Verification performed

The stack was verified with:

- Python syntax compilation for `postgress-infra/main.py`
- FastAPI route and static frontend smoke tests
- `docker compose ... config`
- Successful API Docker image build
- Live PostgreSQL and FastAPI Compose startup
- Successful requests to `/` and `/docs`
