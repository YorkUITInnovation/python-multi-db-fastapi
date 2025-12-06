# getRecord API Endpoint Documentation

## Overview

The `getRecord` endpoint is a universal function that retrieves a **single record** from any configured database (Oracle, MySQL, PostgreSQL, or MS SQL Server). It automatically generates the appropriate SQL query based on the database type and parameters provided.

## Endpoint

**POST** `/getRecord`

## Authentication

Requires API key in header:
```
X-API-KEY: your_api_key
```

## Request Body

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dbtype` | string | Yes | Database type: `oracle`, `mysql`, `postgres`, or `mssql` |
| `server` | string | No | Server name from config (optional if only one server configured) |
| `table` | string | Yes | Table name to query |
| `parameters` | object | Yes | WHERE conditions as key-value pairs (see below) |
| `fields` | string | No | Comma-separated field names (default: `*`) |

### Parameters Format

The `parameters` field is a JSON object where each key is a field name and the value is what to match. Values can be integers, strings, or other JSON-compatible types.

Example:
```json
{
  "user_id": 12345,
  "status": "active"
}
```

Or with a single parameter:
```json
{
  "username": "jsmith"
}
```

## Response

### Success (200)

Returns the single matching record:

```json
{
  "status": "success",
  "dbtype": "oracle",
  "server": "yustart",
  "table": "users",
  "record": {
    "user_id": 12345,
    "username": "jsmith",
    "email": "jsmith@example.com",
    "status": "active"
  }
}
```

### Errors

| Status | Description |
|--------|-------------|
| 400 | Invalid parameters, invalid dbtype, or multiple records found |
| 404 | No record found matching the parameters |
| 500 | Database connection or query error |

**Multiple Records Error (400):**
```json
{
  "detail": "Multiple records found (5 records). Expected only one record. Please refine your parameters."
}
```

**No Record Error (404):**
```json
{
  "detail": "No record found matching the specified parameters"
}
```

## Examples

### Example 1: Oracle - Get User by ID

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8082/getRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "oracle",
  "server": "yustart",
  "table": "users",
  "parameters": {
    "user_id": 12345
  },
  "fields": "user_id,username,email,created_date"
}'
```

**Generated SQL:**
```sql
SELECT user_id,username,email,created_date 
FROM users 
WHERE user_id = :1
```

### Example 2: MySQL - Get Student Record

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8082/getRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "mysql",
  "server": "Early Alerts",
  "table": "mdl_user",
  "parameters": {
    "username": "student123"
  },
  "fields": "id,username,email,firstname,lastname"
}'
```

**Generated SQL:**
```sql
SELECT id,username,email,firstname,lastname 
FROM mdl_user 
WHERE username = %s
```

### Example 3: PostgreSQL - Get Order with Multiple Conditions

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8082/getRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "postgres",
  "table": "orders",
  "parameters": {
    "order_id": "ORD-12345",
    "customer_id": 567
  }
}'
```

**Generated SQL:**
```sql
SELECT * 
FROM orders 
WHERE order_id = %s AND customer_id = %s
```

### Example 4: MS SQL Server - Get Employee

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8082/getRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "mssql",
  "table": "employees",
  "parameters": {
    "employee_id": "EMP001"
  },
  "fields": "employee_id,first_name,last_name,department"
}'
```

**Generated SQL:**
```sql
SELECT employee_id,first_name,last_name,department 
FROM employees 
WHERE employee_id = ?
```

### Example 5: Oracle - Get Record from dual (Test)

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8082/getRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "oracle",
  "server": "yustart",
  "table": "dual",
  "parameters": {
    "DUMMY": "X"
  },
  "fields": "DUMMY"
}'
```

**Response:**
```json
{
  "status": "success",
  "dbtype": "oracle",
  "server": "yustart",
  "table": "dual",
  "record": {
    "DUMMY": "X"
  }
}
```

## SQL Parameter Placeholders

The endpoint automatically uses the correct parameter placeholder for each database:

| Database | Placeholder | Example |
|----------|-------------|---------|
| Oracle | `:1`, `:2`, `:3`, ... | `WHERE id = :1` |
| MySQL | `%s` | `WHERE id = %s` |
| PostgreSQL | `%s` | `WHERE id = %s` |
| MS SQL Server | `?` | `WHERE id = ?` |

## Important Notes

### 1. Single Record Requirement

This endpoint is designed to return **exactly one record**. If your query matches:
- **0 records**: Returns 404 error
- **1 record**: Returns success with the record
- **2+ records**: Returns 400 error with count

If you need to retrieve multiple records, use a different endpoint or modify the function.

### 2. Security - SQL Injection Protection

The endpoint uses **parameterized queries** to prevent SQL injection:
- ✅ **Safe**: Values are passed as parameters, not concatenated into SQL
- ✅ Database driver handles proper escaping
- ✅ Protected against SQL injection attacks

### 3. Field Selection

- **Default**: If `fields` is not provided or is empty, `*` is used (all fields)
- **Specific fields**: Provide comma-separated field names (no spaces recommended)
- **Case sensitivity**: Field names should match database conventions
  - Oracle: Usually UPPERCASE
  - MySQL: Usually lowercase or mixed case
  - PostgreSQL: Usually lowercase
  - MS SQL Server: Usually mixed case

### 4. Server Selection

- If you have **only one server** configured for a database type, the `server` parameter is **optional**
- If you have **multiple servers** configured (using `*_CONFIGS` in .env), you must specify which server to use
- Example: `"server": "yustart"` for Oracle, `"server": "Early Alerts"` for MySQL

## Error Handling

### Invalid Database Type
```json
{
  "detail": "Invalid dbtype 'mongo'. Must be one of: oracle, mysql, postgres, mssql"
}
```

### Missing Required Parameters
```json
{
  "detail": "At least one parameter is required"
}
```

### Database Connection Error
```json
{
  "detail": "Database query failed: [specific error message]"
}
```

## Use Cases

1. **User Lookup**: Retrieve user details by ID or username
2. **Order Verification**: Get specific order information
3. **Student Records**: Fetch student data by student ID
4. **Product Details**: Get product information by SKU or product ID
5. **Validation**: Check if a record exists with specific criteria
6. **Data Verification**: Ensure only one record matches certain conditions

## Testing with Python

```python
import requests

url = "http://localhost:8082/getRecord"
headers = {
    "accept": "application/json",
    "X-API-KEY": "password",
    "Content-Type": "application/json"
}
payload = {
    "dbtype": "oracle",
    "server": "yustart",
    "table": "dual",
    "parameters": {
        "DUMMY": "X"
    },
    "fields": "DUMMY"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

## Interactive Documentation

When running in DEV mode, visit:
- Swagger UI: `http://localhost:8082/docs`
- ReDoc: `http://localhost:8082/redoc`

You can test the endpoint interactively using the Swagger UI interface.

