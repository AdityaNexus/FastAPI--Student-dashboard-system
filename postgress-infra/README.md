# Student dashboard stack

From this directory, start PostgreSQL and the FastAPI application:

```powershell
docker compose up --build
```

Open <http://localhost:8000> for the web dashboard or
<http://localhost:8000/docs> for the API documentation. The API connects to
PostgreSQL using the Compose service name `db`; the `postgres_data` volume keeps
records between restarts.

To stop the containers without deleting data:

```powershell
docker compose down
```
