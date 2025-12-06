# insertRecord, updateRecord, and deleteRecord API Documentation

## Overview

The `insertRecord`, `updateRecord`, and `deleteRecord` endpoints provide simple, secure ways to insert, update, and delete records across any configured database (Oracle, MySQL, PostgreSQL, MS SQL Server).

## insertRecord Endpoint

### Endpoint

**POST** `/insertRecord`

### Authentication

Requires API key in header:
```
X-API-KEY: your_api_key
```

### Request Body

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dbtype` | string | Yes | Database type: `oracle`, `mysql`, `postgres`, or `mssql` |
| `server` | string | No | Server name from config (optional if only one server configured) |
| `table` | string | Yes | Table name to insert into |
| `data` | object | Yes | Column-value pairs to insert |

### Request Example

```json
{
  "dbtype": "mysql",
  "server": "default",
  "table": "users",
  "data": {
    "username": "johndoe",
    "email": "john@example.com",
    "firstname": "John",
    "lastname": "Doe",
    "status": "active"
  }
}
```

### Response

#### Success (200)

```json
{
  "status": "success",
  "dbtype": "mysql",
  "server": "default",
  "table": "users",
  "rows_affected": 1,
  "inserted_id": 12345,
  "message": "Successfully inserted 1 record(s)"
}
```

**Note**: `inserted_id` is only returned for MySQL (last_insert_id). Other databases don't include this field.

#### Error (400)

Invalid database type or empty data:
```json
{
  "detail": "Invalid dbtype 'mongodb'. Must be one of: oracle, mysql, postgres, mssql"
}
```

#### Error (500)

Insert failed (e.g., constraint violation, missing required field):
```json
{
  "detail": "Insert failed: column 'email' cannot be null"
}
```

### Examples

#### Example 1: MySQL Insert

```bash
curl -X 'POST' \
  'http://localhost:8082/insertRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "mysql",
  "table": "users",
  "data": {
    "username": "alice",
    "email": "alice@example.com",
    "firstname": "Alice",
    "lastname": "Smith"
  }
}'
```

#### Example 2: Oracle Insert

```bash
curl -X 'POST' \
  'http://localhost:8082/insertRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "oracle",
  "server": "yustart",
  "table": "student_records",
  "data": {
    "student_id": 123456,
    "student_name": "Bob Johnson",
    "enrollment_date": "2024-01-15",
    "status": "active"
  }
}'
```

#### Example 3: PostgreSQL Insert

```bash
curl -X 'POST' \
  'http://localhost:8082/insertRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "postgres",
  "table": "orders",
  "data": {
    "order_id": "ORD-2024-001",
    "customer_id": 567,
    "total_amount": 99.99,
    "order_date": "2024-01-15"
  }
}'
```

---

## updateRecord Endpoint

### Endpoint

**POST** `/updateRecord`

### Authentication

Requires API key in header:
```
X-API-KEY: your_api_key
```

### Request Body

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dbtype` | string | Yes | Database type: `oracle`, `mysql`, `postgres`, or `mssql` |
| `server` | string | No | Server name from config (optional if only one server configured) |
| `table` | string | Yes | Table name to update |
| `data` | object | Yes | Column-value pairs to update |
| `where` | object | Yes | WHERE conditions to identify records to update |

### Request Example

```json
{
  "dbtype": "mysql",
  "server": "default",
  "table": "users",
  "data": {
    "email": "newemail@example.com",
    "status": "active",
    "last_updated": "2024-01-15"
  },
  "where": {
    "user_id": 12345
  }
}
```

### Response

#### Success (200)

```json
{
  "status": "success",
  "dbtype": "mysql",
  "server": "default",
  "table": "users",
  "rows_affected": 1,
  "message": "Successfully updated 1 record(s)"
}
```

**Important**: `rows_affected` can be greater than 1 if the WHERE clause matches multiple records.

#### Error (400)

Missing or invalid parameters:
```json
{
  "detail": "WHERE conditions cannot be empty (to prevent updating all records)"
}
```

#### Error (500)

Update failed:
```json
{
  "detail": "Update failed: column 'email' cannot be null"
}
```

### Examples

#### Example 1: Update Single Record by ID

```bash
curl -X 'POST' \
  'http://localhost:8082/updateRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "mysql",
  "table": "users",
  "data": {
    "email": "alice.new@example.com",
    "status": "verified"
  },
  "where": {
    "user_id": 12345
  }
}'
```

#### Example 2: Update Multiple Fields

```bash
curl -X 'POST' \
  'http://localhost:8082/updateRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "oracle",
  "server": "yustart",
  "table": "student_records",
  "data": {
    "status": "graduated",
    "graduation_date": "2024-06-15",
    "final_gpa": 3.85
  },
  "where": {
    "student_id": 123456
  }
}'
```

#### Example 3: Update with Multiple WHERE Conditions

```bash
curl -X 'POST' \
  'http://localhost:8082/updateRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "postgres",
  "table": "orders",
  "data": {
    "status": "shipped",
    "shipped_date": "2024-01-16"
  },
  "where": {
    "order_id": "ORD-2024-001",
    "customer_id": 567
  }
}'
```

**Note**: This will only update records where BOTH `order_id` AND `customer_id` match.

#### Example 4: Bulk Update (Multiple Records)

```bash
curl -X 'POST' \
  'http://localhost:8082/updateRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "mysql",
  "table": "users",
  "data": {
    "newsletter": true
  },
  "where": {
    "status": "active"
  }
}'
```

**Warning**: This will update ALL users with `status='active'`. The response will show:
```json
{
  "rows_affected": 523,
  "message": "Successfully updated 523 record(s)"
}
```

---

## deleteRecord Endpoint

### Endpoint

**POST** `/deleteRecord`

### Authentication

Requires API key in header:
```
X-API-KEY: your_api_key
```

### Request Body

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dbtype` | string | Yes | Database type: `oracle`, `mysql`, `postgres`, or `mssql` |
| `server` | string | No | Server name from config (optional if only one server configured) |
| `table` | string | Yes | Table name to delete from |
| `where` | object | Yes | WHERE conditions to identify records to delete |

### Request Example

```json
{
  "dbtype": "mysql",
  "server": "default",
  "table": "users",
  "where": {
    "user_id": 12345
  }
}
```

### Response

#### Success (200)

```json
{
  "status": "success",
  "dbtype": "mysql",
  "server": "default",
  "table": "users",
  "rows_affected": 1,
  "message": "Successfully deleted 1 record(s)"
}
```

**Important**: `rows_affected` can be greater than 1 if the WHERE clause matches multiple records.

#### Error (400)

Missing WHERE conditions:
```json
{
  "detail": "WHERE conditions cannot be empty (to prevent deleting all records)"
}
```

#### Error (500)

Delete failed (e.g., foreign key constraint):
```json
{
  "detail": "Delete failed: foreign key constraint violation"
}
```

### Examples

#### Example 1: Delete Single Record by ID

```bash
curl -X 'POST' \
  'http://localhost:8082/deleteRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "mysql",
  "table": "users",
  "where": {
    "user_id": 12345
  }
}'
```

#### Example 2: Delete with Multiple Conditions

```bash
curl -X 'POST' \
  'http://localhost:8082/deleteRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "oracle",
  "server": "yustart",
  "table": "temp_records",
  "where": {
    "session_id": "abc123",
    "expired": true
  }
}'
```

**Note**: This will only delete records where BOTH `session_id` AND `expired` match.

#### Example 3: Delete PostgreSQL Records

```bash
curl -X 'POST' \
  'http://localhost:8082/deleteRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "postgres",
  "table": "audit_logs",
  "where": {
    "log_date": "2023-01-15"
  }
}'
```

#### Example 4: Bulk Delete (Multiple Records)

```bash
curl -X 'POST' \
  'http://localhost:8082/deleteRecord' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbtype": "mysql",
  "table": "sessions",
  "where": {
    "status": "expired"
  }
}'
```

**Warning**: This will delete ALL sessions with `status='expired'`. The response will show:
```json
{
  "rows_affected": 147,
  "message": "Successfully deleted 147 record(s)"
}
```

---

## Important Notes

### Security

1. **SQL Injection Protection**: All endpoints use parameterized queries, making them safe from SQL injection attacks
2. **API Key Required**: All requests require authentication
3. **Transaction Safety**: Failed operations are automatically rolled back

### Data Types

All endpoints handle various data types:
- **Strings**: `"John Doe"`, `"active"`
- **Numbers**: `123`, `99.99`
- **Dates**: `"2024-01-15"` (as strings, database will handle conversion)
- **Booleans**: `true`, `false`
- **Null**: `null`

### WHERE Clause Behavior

**insertRecord**: No WHERE clause (inserts new record)

**updateRecord**: 
- WHERE clause is **required** to prevent accidentally updating all records
- Multiple WHERE conditions are combined with AND
- Can update multiple records if WHERE matches multiple rows

**deleteRecord**:
- WHERE clause is **required** to prevent accidentally deleting all records
- Multiple WHERE conditions are combined with AND
- Can delete multiple records if WHERE matches multiple rows
- **Use with caution** - deletions are permanent!

### Transaction Handling

- Successful operations are automatically committed
- Failed operations are automatically rolled back
- You'll receive an error response if the operation fails

### Field Names

- Field names must match the database column names exactly
- Case sensitivity depends on the database:
  - **Oracle**: Usually UPPERCASE
  - **MySQL**: Usually lowercase (depends on configuration)
  - **PostgreSQL**: Usually lowercase
  - **MS SQL**: Usually mixed case

## Use Cases

### insertRecord Use Cases

1. **User Registration**: Insert new user records
2. **Order Creation**: Create new order records
3. **Log Entries**: Insert audit log or activity records
4. **Data Migration**: Insert records from one system to another
5. **Batch Processing**: Insert records in a loop (call endpoint multiple times)

### updateRecord Use Cases

1. **Profile Updates**: Update user information
2. **Status Changes**: Change order status, user status, etc.
3. **Data Corrections**: Fix incorrect data
4. **Bulk Updates**: Update multiple records with same criteria
5. **Timestamp Updates**: Update last_modified timestamps

### deleteRecord Use Cases

1. **User Account Deletion**: Remove user accounts permanently
2. **Data Cleanup**: Delete old or expired records
3. **Session Management**: Clear expired sessions
4. **Order Cancellation**: Remove cancelled orders
5. **Temporary Data**: Delete cache or temporary records
6. **Compliance**: Delete records as required by data retention policies

**Warning**: Use deleteRecord with caution. Consider implementing soft deletes (setting a `deleted` flag) instead of hard deletes for better auditability.

## Python Examples

### Insert Example

```python
import requests

url = "http://localhost:8082/insertRecord"
headers = {
    "accept": "application/json",
    "X-API-KEY": "password",
    "Content-Type": "application/json"
}

payload = {
    "dbtype": "mysql",
    "table": "users",
    "data": {
        "username": "johndoe",
        "email": "john@example.com",
        "firstname": "John",
        "lastname": "Doe",
        "created_date": "2024-01-15"
    }
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

if result["status"] == "success":
    print(f"Inserted successfully! Rows affected: {result['rows_affected']}")
    if "inserted_id" in result:
        print(f"Inserted ID: {result['inserted_id']}")
else:
    print(f"Error: {result}")
```

### Update Example

```python
import requests

url = "http://localhost:8082/updateRecord"
headers = {
    "accept": "application/json",
    "X-API-KEY": "password",
    "Content-Type": "application/json"
}

payload = {
    "dbtype": "mysql",
    "table": "users",
    "data": {
        "email": "newemail@example.com",
        "status": "verified"
    },
    "where": {
        "user_id": 12345
    }
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

if result["status"] == "success":
    print(f"Updated successfully! Rows affected: {result['rows_affected']}")
else:
    print(f"Error: {result}")
```

### Delete Example

```python
import requests

url = "http://localhost:8082/deleteRecord"
headers = {
    "accept": "application/json",
    "X-API-KEY": "password",
    "Content-Type": "application/json"
}

payload = {
    "dbtype": "mysql",
    "table": "users",
    "where": {
        "user_id": 12345
    }
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

if result["status"] == "success":
    print(f"Deleted successfully! Rows affected: {result['rows_affected']}")
else:
    print(f"Error: {result}")
```

### Helper Functions

```python
def insert_record(dbtype, table, data, server=None):
    """Helper function to insert a record"""
    url = "http://localhost:8082/insertRecord"
    headers = {"X-API-KEY": "password", "Content-Type": "application/json"}
    
    payload = {"dbtype": dbtype, "table": table, "data": data}
    if server:
        payload["server"] = server
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def update_record(dbtype, table, data, where, server=None):
    """Helper function to update record(s)"""
    url = "http://localhost:8082/updateRecord"
    headers = {"X-API-KEY": "password", "Content-Type": "application/json"}
    
    payload = {"dbtype": dbtype, "table": table, "data": data, "where": where}
    if server:
        payload["server"] = server
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def delete_record(dbtype, table, where, server=None):
    """Helper function to delete record(s)"""
    url = "http://localhost:8082/deleteRecord"
    headers = {"X-API-KEY": "password", "Content-Type": "application/json"}
    
    payload = {"dbtype": dbtype, "table": table, "where": where}
    if server:
        payload["server"] = server
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Usage
result = insert_record("mysql", "users", {
    "username": "alice",
    "email": "alice@example.com"
})

result = update_record("mysql", "users", 
    {"status": "active"}, 
    {"user_id": 12345}
)

result = delete_record("mysql", "users",
    {"user_id": 12345}
)
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid dbtype` | Wrong database type specified | Use oracle, mysql, postgres, or mssql |
| `Data dictionary cannot be empty` | No data provided (insert/update) | Provide at least one field-value pair |
| `WHERE conditions cannot be empty` | Update/delete without WHERE | Provide WHERE clause to prevent mass operations |
| `column 'X' cannot be null` | Required field missing | Include all required fields |
| `Duplicate entry` | Unique constraint violation | Use different value or update existing record |
| `Table doesn't exist` | Wrong table name | Check table name spelling and case |
| `Foreign key constraint` | Delete blocked by foreign key | Delete dependent records first or use CASCADE |

### Best Practices

1. **Validate data before sending**: Check required fields, data types, etc.
2. **Handle errors gracefully**: Always check the response status
3. **Use transactions**: For multiple operations, consider using sqlExec with transaction support
4. **Test with small updates/deletes first**: Especially with updateRecord and deleteRecord to avoid mass operations
5. **Log operations**: Keep track of inserts/updates/deletes for audit purposes
6. **Be cautious with deleteRecord**: Deletions are permanent - consider soft deletes (status flags) instead
7. **Backup before mass operations**: Always have backups before bulk updates or deletes

## Comparison with Other Endpoints

| Feature | insertRecord | updateRecord | deleteRecord | getRecord | sqlExec |
|---------|--------------|--------------|--------------|-----------|---------|
| Purpose | Insert new record | Update existing | Delete existing | Retrieve single record | Execute custom SQL |
| SQL Generated | Auto (INSERT) | Auto (UPDATE) | Auto (DELETE) | Auto (SELECT) | User-provided |
| WHERE Clause | No | Required | Required | Yes | Optional |
| Records Affected | 1 | 1 or more | 1 or more | Exactly 1 | 0 to 300 |
| Returns Data | No (just status) | No (just status) | No (just status) | Yes (the record) | Yes (multiple records) |
| Reversible | No | Sometimes | No | N/A | Depends on query |
| SQL Generated | Auto (INSERT) | Auto (UPDATE) | Auto (SELECT) | User-provided |
| WHERE Clause | No | Required | Yes | Optional |
| Records Affected | 1 | 1 or more | Exactly 1 | 0 to 300 |
| Returns Data | No (just status) | No (just status) | Yes (the record) | Yes (multiple records) |

## Summary

✅ **insertRecord**: Simple, secure record insertion  
✅ **updateRecord**: Safe record updates with mandatory WHERE clause  
✅ **Parameterized queries**: SQL injection protection  
✅ **Multi-database**: Works with Oracle, MySQL, PostgreSQL, MS SQL  
✅ **Transaction safety**: Auto commit/rollback  
✅ **Clear responses**: Detailed success/error messages  

Both endpoints provide a simple, secure way to modify data across all your databases!

## Summary
✅ **insertRecord**: Simple, secure record insertion  
✅ **updateRecord**: Safe record updates with mandatory WHERE clause  
✅ **deleteRecord**: Controlled record deletion with WHERE requirement  
✅ **Parameterized queries**: SQL injection protection  
✅ **Multi-database**: Works with Oracle, MySQL, PostgreSQL, MS SQL  
✅ **Transaction safety**: Auto commit/rollback  
✅ **Clear responses**: Detailed success/error messages  
All three endpoints provide complete CRUD operations (Create, Update, Delete) across all your databases!
