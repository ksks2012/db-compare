# Database Comparison with FastAPI

This project demonstrates a FastAPI application that interacts with both MySQL and PostgreSQL databases to perform basic CRUD operations. It is designed to compare the behavior and performance of these two databases in a Dockerized environment.

## Project Structure

```
db-compare/
├── cmd/
│   └── main.py           # FastAPI application
├── docker-compose.yml    # Docker Compose configuration
├── dockerfile            # Dockerfile for FastAPI service
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Prerequisites

- **Docker** and **Docker Compose** (latest versions recommended)
- **Python 3.12** (for local development)
- MySQL 8.0+ and PostgreSQL 15+ (if running databases locally)

## Setup

### 1. Install Dependencies

For local development, activate a virtual environment and install dependencies:

```bash
python -m venv rt-sandbox
source rt-sandbox/bin/activate  # Linux/Mac
.\rt-sandbox\Scripts\activate   # Windows
pip install -r requirements.txt
```

The `requirements.txt` includes:

```
fastapi==0.116.0
uvicorn==0.30.6
sqlalchemy==2.0.35
pymysql==1.1.1
psycopg2-binary==2.9.9
python-dotenv==1.0.1
cryptography==43.0.1
```

### 2. Configure Environment Variables

Create a `.env` file in the project root for local runs:

```env
MYSQL_DATABASE_URL=mysql+pymysql://user:password@localhost:3306/testdb
POSTGRES_DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/testdb
```

Replace `user`, `password`, and `testdb` with your MySQL and PostgreSQL credentials.

For Docker, environment variables are defined in `docker-compose.yml`.

### 3. Set Up Databases

- **Local Setup**:
  Ensure MySQL and PostgreSQL are running locally and create the `testdb` database:
  ```bash
  mysql -u root -p -h localhost -e "CREATE DATABASE IF NOT EXISTS testdb;"
  psql -U postgres -h localhost -c "CREATE DATABASE testdb;"
  ```
  Grant permissions:
  ```sql
  # MySQL
  GRANT ALL PRIVILEGES ON testdb.* TO 'user'@'localhost' IDENTIFIED BY 'password';
  FLUSH PRIVILEGES;

  # PostgreSQL
  GRANT ALL ON DATABASE testdb TO user;
  ```

- **Docker Setup**:
  The `docker-compose.yml` automatically sets up MySQL and PostgreSQL containers with the `testdb` database.

## Running the Application

### Option 1: Local Run

1. Activate the virtual environment:
   ```bash
   source rt-sandbox/bin/activate
   ```

2. Start the FastAPI application:
   ```bash
   uvicorn cmd.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. Access the API at `http://localhost:8000`.

### Option 2: Docker Run

1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

2. Access the API at `http://localhost:8000`.

To stop the containers:
```bash
docker-compose down
```

To reset databases (clears data):
```bash
docker-compose down -v
```

## API Endpoints

The application provides endpoints to manage users in both MySQL and PostgreSQL databases.

- **Create User**:
  - **URL**: `POST /users/{db_type}`
  - **Parameters**: `db_type` = `mysql` or `postgres`
  - **Body**: `{"name": "John Doe", "email": "john@example.com"}`
  - **Example**:
    ```bash
    curl -X POST "http://localhost:8000/users/mysql" -H "Content-Type: application/json" -d '{"name":"John Doe","email":"john@example.com"}'
    curl -X POST "http://localhost:8000/users/postgres" -H "Content-Type: application/json" -d '{"name":"Jane Doe","email":"jane@example.com"}'
    ```

- **Get User**:
  - **URL**: `GET /users/{db_type}/{user_id}`
  - **Parameters**: `db_type` = `mysql` or `postgres`, `user_id` = integer
  - **Example**:
    ```bash
    curl "http://localhost:8000/users/mysql/1"
    curl "http://localhost:8000/users/postgres/1"
    ```

## Verifying Table Creation

- **MySQL**:
  ```bash
  docker exec -it <mysql-container-name> mysql -u user -ppassword testdb
  SHOW TABLES;
  SELECT * FROM users;
  ```

- **PostgreSQL**:
  ```bash
  docker exec -it <postgres-container-name> psql -U user -d testdb
  \dt
  SELECT * FROM users;
  ```

## MySQL vs. PostgreSQL Comparison

| Feature | MySQL | PostgreSQL |
|---------|-------|------------|
| **Authentication** | Uses `sha256_password` or `caching_sha2_password` (requires `cryptography` for `pymysql`) | Uses `md5` or `scram-sha-256` (no extra dependencies needed) |
| **Initialization Speed** | Faster startup in Docker | Slower due to `initdb` process |
| **Performance** | Better for simple, high-concurrency reads | Excels in complex queries and analytics |
| **Features** | Basic SQL, JSON support | Advanced features like JSONB, full-text search, GIS |
| **Table Creation** | Simple and fast | Robust schema management |

### Performance Testing
To compare performance, insert 1,000 records into each database:
```bash
for i in {1..1000}; do curl -X POST "http://localhost:8000/users/mysql" -H "Content-Type: application/json" -d "{\"name\":\"User$i\",\"email\":\"user$i@example.com\"}"; done
for i in {1..1000}; do curl -X POST "http://localhost:8000/users/postgres" -H "Content-Type: application/json" -d "{\"name\":\"User$i\",\"email\":\"user$i@example.com\"}"; done
```

## Troubleshooting

- **ModuleNotFoundError**:
  Ensure all dependencies are installed:
  ```bash
  pip install -r requirements.txt
  ```

- **Database Connection Issues**:
  - Verify environment variables in `.env` or `docker-compose.yml`.
  - Check MySQL authentication plugin:
    ```sql
    SELECT user, host, plugin FROM mysql.user WHERE user = 'user';
    ALTER USER 'user'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';
    ```

- **Table Not Created**:
  - Check logs for connection errors:
    ```bash
    docker-compose logs fastapi
    ```
  - Reset databases:
    ```bash
    docker-compose down -v
    docker-compose up --build
    ```

## Future Enhancements

- Add JSONB support in PostgreSQL to compare with MySQL’s JSON.
- Implement indexing on the `email` column to test query performance.
- Add a backup script for MySQL and PostgreSQL databases.