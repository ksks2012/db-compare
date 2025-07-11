#!/bin/bash
curl -X POST "http://localhost:8000/users/mysql" -H "Content-Type: application/json" -d '{"name":"John Doe","email":"john@example.com"}'
curl -X POST "http://localhost:8000/users/postgres" -H "Content-Type: application/json" -d '{"name":"Jane Doe","email":"jane@example.com"}'

curl "http://localhost:8000/users/mysql/1"
curl "http://localhost:8000/users/postgres/1"