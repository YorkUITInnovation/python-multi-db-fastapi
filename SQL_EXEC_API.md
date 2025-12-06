# sqlExec API Endpoint Documentation

## Overview

The `sqlExec` endpoint allows you to execute **custom SQL queries** with parameterized WHERE clauses across any configured database (Oracle, MySQL, PostgreSQL, or MS SQL Server). It includes built-in pagination support with a maximum of 300 records per page.

## Endpoint

**POST** `/sqlExec`

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
| `sql` | string | Yes | SQL query with named parameters |
| `parameters` | object | No | Parameter values as key-value pairs |
| `page` | integer | No | Page number (default: 1, minimum: 1) |
| `page_size` | integer | No | Records per page (default: 100, max: 300) |

### SQL Parameter Syntax by Database Type

**For your convenience, you can use `:parameter_name` syntax for all databases.** The API will automatically convert it to the correct format for MySQL/PostgreSQL.

| Database | Native Syntax | Also Accepts | Example |
|----------|---------------|--------------|---------|
| **Oracle** | `:parameter_name` | - | `WHERE firstname = :firstname AND id > :min_id` |
| **MySQL** | `%(parameter_name)s` | `:parameter_name` (auto-converted) | `WHERE firstname = %(firstname)s` or `WHERE firstname = :firstname` |
| **PostgreSQL** | `%(parameter_name)s` | `:parameter_name` (auto-converted) | `WHERE firstname = %(firstname)s` or `WHERE firstname = :firstname` |
| **MS SQL** | `:parameter_name` | - | `WHERE firstname = :firstname AND id > :min_id` |

**💡 Tip:** Use `:parameter_name` syntax for all databases. It's simpler and works everywhere!

### Parameters Format

The `parameters` field is a JSON object where each key corresponds to a parameter name in your SQL query:

```json
{
  "firstname": "patrick",
  "starttime": "2024-01-01 11:00:00",
  "endtime": "2024-01-01 13:00:00"
}
```

## Response

### Success (200)

Returns paginated results with metadata:

```json
{
  "status": "success",
  "dbtype": "oracle",
  "server": "yustart",
  "pagination": {
    "page": 1,
    "page_size": 100,
    "record_count": 100,
    "total_records": 1523,
    "total_pages": 16,
    "has_more": true,
    "next_page": 2
  },
  "records": [
    {
      "id": 1,
      "firstname": "patrick",
      "lastname": "smith",
      "timemodified": "2024-01-01 12:30:00"
    },
    ...
  ]
}
```

### Pagination Metadata

| Field | Type | Description |
|-------|------|-------------|
| `page` | integer | Current page number |
| `page_size` | integer | Maximum records per page |
| `record_count` | integer | Number of records returned in this page |
| `total_records` | integer | Total number of records matching the query (without pagination) |
| `total_pages` | integer | Total number of pages available |
| `has_more` | boolean | True if there might be more records (current page is full) |
| `next_page` | integer/null | Next page number if `has_more` is true, otherwise null |

### Errors

| Status | Description |
|--------|-------------|
| 400 | Invalid dbtype or invalid parameters |
| 500 | Database connection or query error |

## Examples

### Example 1: Oracle - Simple Query with Named Parameters

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8082/sqlExec' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "oracle",
  "server": "yustart",
  "sql": "SELECT * FROM users WHERE firstname = :firstname AND lastname = :lastname",
  "parameters": {
    "firstname": "patrick",
    "lastname": "smith"
  },
  "page": 1,
  "page_size": 50
}'
```

### Example 2: Oracle - BETWEEN Clause with Time Range

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8082/sqlExec' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "oracle",
  "server": "yustart",
  "sql": "SELECT * FROM user_activity WHERE firstname = :firstname AND timemodified BETWEEN :starttime AND :endtime ORDER BY timemodified DESC",
  "parameters": {
    "firstname": "patrick",
    "starttime": "2024-01-01 11:00:00",
    "endtime": "2024-01-01 13:00:00"
  },
  "page": 1,
  "page_size": 100
}'
```

### Example 3: MySQL - Query with Named Parameters

**Request (using auto-converted :parameter syntax):**
```bash
curl -X 'POST' \
  'http://localhost:8082/sqlExec' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "mysql",
  "server": "Early Alerts",
  "sql": "SELECT id, username, email, firstname, lastname FROM mdl_user WHERE id >= :min_id AND deleted = :deleted ORDER BY id",
  "parameters": {
    "min_id": 1,
    "deleted": 0
  },
  "page": 1,
  "page_size": 50
}'
```

**Request (using native %(parameter)s syntax):**
```bash
curl -X 'POST' \
  'http://localhost:8082/sqlExec' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "mysql",
  "server": "Early Alerts",
  "sql": "SELECT id, username, email, firstname, lastname FROM mdl_user WHERE id >= %(min_id)s AND deleted = %(deleted)s ORDER BY id",
  "parameters": {
    "min_id": 1,
    "deleted": 0
  },
  "page": 1,
  "page_size": 50
}'
```

Both examples work identically - use whichever syntax you prefer!

### Example 4: PostgreSQL - Pagination Example

**Request for Page 1:**
```bash
curl -X 'POST' \
  'http://localhost:8082/sqlExec' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "postgres",
  "sql": "SELECT * FROM orders WHERE status = %(status)s ORDER BY created_date DESC",
  "parameters": {
    "status": "pending"
  },
  "page": 1,
  "page_size": 100
}'
```

**Request for Page 2:**
```bash
# Just change the page number
curl -X 'POST' \
  'http://localhost:8082/sqlExec' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "postgres",
  "sql": "SELECT * FROM orders WHERE status = %(status)s ORDER BY created_date DESC",
  "parameters": {
    "status": "pending"
  },
  "page": 2,
  "page_size": 100
}'
```

### Example 5: Query Without Parameters

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8082/sqlExec' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "oracle",
  "server": "yustart",
  "sql": "SELECT * FROM system_config ORDER BY id",
  "page": 1,
  "page_size": 50
}'
```

### Example 6: MS SQL Server with Named Parameters

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8082/sqlExec' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "mssql",
  "sql": "SELECT * FROM employees WHERE department = :dept AND salary > :min_salary ORDER BY lastname",
  "parameters": {
    "dept": "Engineering",
    "min_salary": 50000
  },
  "page": 1,
  "page_size": 100
}'
```

## Pagination Usage

### Automatic Pagination

The endpoint automatically handles pagination:
- **Page 1**: Returns records 1-100 (if page_size=100)
- **Page 2**: Returns records 101-200
- **Page 3**: Returns records 201-300
- And so on...

### Using the next_page Field

The easiest way to implement pagination:

```python
import requests

def get_all_records(dbtype, sql, parameters=None, page_size=100):
    """Fetch all records using pagination"""
    all_records = []
    page = 1
    
    while True:
        response = requests.post(
            "http://localhost:8082/sqlExec",
            headers={
                "X-API-KEY": "password",
                "Content-Type": "application/json"
            },
            json={
                "dbtype": dbtype,
                "sql": sql,
                "parameters": parameters or {},
                "page": page,
                "page_size": page_size
            }
        )
        
        data = response.json()
        all_records.extend(data["records"])
        
        # Check if there are more pages
        if not data["pagination"]["has_more"]:
            break
        
        page = data["pagination"]["next_page"]
    
    return all_records

# Example usage
records = get_all_records(
    dbtype="oracle",
    sql="SELECT * FROM users WHERE status = :status ORDER BY id",
    parameters={"status": "active"},
    page_size=100
)
print(f"Total records fetched: {len(records)}")
```

### Manual Pagination Control

```python
# Get specific page
def get_page(dbtype, sql, page, parameters=None, page_size=100):
    response = requests.post(
        "http://localhost:8082/sqlExec",
        headers={
            "X-API-KEY": "password",
            "Content-Type": "application/json"
        },
        json={
            "dbtype": dbtype,
            "sql": sql,
            "parameters": parameters or {},
            "page": page,
            "page_size": page_size
        }
    )
    return response.json()

# Get page 3
page_3_data = get_page(
    dbtype="oracle",
    sql="SELECT * FROM users ORDER BY id",
    page=3,
    page_size=50
)
```

## Important Notes

### 1. Maximum Records Per Page

- **Default**: 100 records per page
- **Maximum**: 300 records per page
- **Minimum**: 1 record per page

If you specify a page_size > 300, it will be automatically capped at 300.

### 2. SQL Injection Protection

The endpoint uses **parameterized queries** to prevent SQL injection:
- ✅ **Safe**: Parameter values are passed separately, not concatenated into SQL
- ✅ Database driver handles proper escaping
- ✅ Protected against SQL injection attacks

**DO NOT** concatenate values into the SQL string:
```json
// ❌ UNSAFE - Don't do this
{
  "sql": "SELECT * FROM users WHERE name = 'patrick'"
}

// ✅ SAFE - Do this instead
{
  "sql": "SELECT * FROM users WHERE name = :name",
  "parameters": {"name": "patrick"}
}
```

### 3. Parameter Naming

- Parameter names must match between SQL and parameters object
- Parameter names are case-sensitive
- Use clear, descriptive names (e.g., `firstname`, `start_date`, `min_value`)

### 4. ORDER BY Required for Consistent Pagination

For reliable pagination, **always include an ORDER BY clause**:

```sql
-- ✅ Good - deterministic order
SELECT * FROM users WHERE status = :status ORDER BY id

-- ❌ Bad - results may vary between pages
SELECT * FROM users WHERE status = :status
```

### 5. Database-Specific Features

You can use database-specific SQL features:

**Oracle:**
```sql
SELECT * FROM users WHERE created_date >= SYSDATE - 7
```

**MySQL:**
```sql
SELECT * FROM users WHERE created_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
```

**PostgreSQL:**
```sql
SELECT * FROM users WHERE created_date >= NOW() - INTERVAL '7 days'
```

## Error Handling

### Invalid Database Type
```json
{
  "detail": "Invalid dbtype 'mongodb'. Must be one of: oracle, mysql, postgres, mssql"
}
```

### SQL Syntax Error
```json
{
  "detail": "Database query failed: ORA-00942: table or view does not exist"
}
```

### Missing Parameter
```json
{
  "detail": "Database query failed: missing bind variable 'firstname'"
}
```

## Use Cases

1. **Complex Queries**: Execute joins, subqueries, aggregations
2. **Time-Based Filtering**: Filter by date/time ranges
3. **Search Functionality**: Implement search with multiple criteria
4. **Reporting**: Generate reports with custom SQL
5. **Data Export**: Export large datasets with pagination
6. **Analytics**: Run analytical queries with parameters

## Comparison with getRecord

| Feature | getRecord | sqlExec |
|---------|-----------|---------|
| Purpose | Single record lookup | Multiple records with custom SQL |
| SQL | Auto-generated | User-provided |
| Return | Exactly 1 record (error if 0 or 2+) | 0 to 300 records per page |
| Pagination | No | Yes (up to 300/page) |
| Complexity | Simple field=value conditions | Any SQL (joins, subqueries, etc.) |
| Use Case | Primary key lookups | Complex queries, reporting |

## Best Practices

1. **Always use ORDER BY** for consistent pagination
2. **Use named parameters** instead of concatenating values
3. **Start with page_size=100** and adjust based on needs
4. **Validate SQL** in a database tool before using in API
5. **Use indexes** on filtered columns for better performance
6. **Monitor response times** for complex queries
7. **Cache results** if running the same query frequently

## Interactive Documentation

When running in DEV mode, visit:
- Swagger UI: `http://localhost:8082/docs`
- ReDoc: `http://localhost:8082/redoc`

You can test the endpoint interactively using the Swagger UI interface.

