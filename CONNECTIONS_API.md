# Connections Endpoint Documentation

## Overview

The `/connections` endpoint provides a comprehensive list of all database connections configured on the server. This is useful for developers to discover which database servers are available for use with the `getRecord` and `sqlExec` endpoints.

## Endpoint

**GET** `/connections`

## Authentication

Requires API key in header:
```
X-API-KEY: your_api_key
```

## Request

No request body or parameters required. Simply make a GET request to the endpoint.

## Response

### Success (200)

Returns a comprehensive list of all configured database connections:

```json
{
  "status": "success",
  "summary": {
    "total_connections": 5,
    "by_type": {
      "oracle": 2,
      "mysql": 2,
      "postgres": 1,
      "mssql": 0
    }
  },
  "connections": {
    "oracle": {
      "yustart": {
        "name": "yustart",
        "type": "oracle",
        "config": {
          "host": "exacc-sisdss.uit.yorku.ca",
          "port": 1521,
          "service_name": "sisdss.uit.yorku.ca",
          "user": "yustart",
          "password": "***HIDDEN***"
        },
        "is_default": false
      },
      "eclass": {
        "name": "eclass",
        "type": "oracle",
        "config": {
          "host": "exacc-sisdss.uit.yorku.ca",
          "port": 1521,
          "service_name": "sisdss.uit.yorku.ca",
          "user": "moodle_reader",
          "password": "***HIDDEN***"
        },
        "is_default": false
      }
    },
    "mysql": {
      "Early Alerts": {
        "name": "Early Alerts",
        "type": "mysql",
        "config": {
          "host": "localhost",
          "port": 3306,
          "db": "moodle",
          "user": "moodle",
          "password": "***HIDDEN***"
        },
        "is_default": false
      },
      "default": {
        "name": "default",
        "type": "mysql",
        "config": {
          "host": "localhost",
          "port": 3306,
          "db": "testdb",
          "user": "testuser",
          "password": "***HIDDEN***"
        },
        "is_default": true
      }
    },
    "postgres": {
      "default": {
        "name": "default",
        "type": "postgres",
        "config": {
          "host": "localhost",
          "port": 5432,
          "db": "testdb",
          "user": "postgres",
          "password": "***HIDDEN***"
        },
        "is_default": true
      }
    },
    "mssql": {}
  }
}
```

### Response Structure

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always "success" |
| `summary` | object | Summary of all connections |
| `summary.total_connections` | integer | Total number of configured connections |
| `summary.by_type` | object | Count of connections per database type |
| `connections` | object | Detailed connection information organized by database type |

### Connection Object

Each connection contains:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Server identifier (used in API calls) |
| `type` | string | Database type (oracle, mysql, postgres, mssql) |
| `config` | object | Connection configuration (passwords masked) |
| `is_default` | boolean | Whether this is the default connection for its type |

### Security

- **Passwords are masked**: All password fields show `***HIDDEN***`
- **API key required**: Endpoint requires authentication
- **Read-only**: This endpoint only displays configuration, it doesn't expose credentials

## Usage Examples

### Example 1: List All Connections

```bash
curl -X 'GET' \
  'http://localhost:8082/connections' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password'
```

### Example 2: Using with Python

```python
import requests

url = "http://localhost:8082/connections"
headers = {
    "accept": "application/json",
    "X-API-KEY": "password"
}

response = requests.get(url, headers=headers)
data = response.json()

# Display summary
print(f"Total connections: {data['summary']['total_connections']}")
print(f"Oracle servers: {data['summary']['by_type']['oracle']}")
print(f"MySQL servers: {data['summary']['by_type']['mysql']}")

# List all Oracle connections
print("\nOracle Connections:")
for name, info in data['connections']['oracle'].items():
    print(f"  - {name}: {info['config']['host']}:{info['config']['port']}")

# List all MySQL connections
print("\nMySQL Connections:")
for name, info in data['connections']['mysql'].items():
    print(f"  - {name}: {info['config']['host']}:{info['config']['db']}")
```

### Example 3: Discovering Available Servers

```python
import requests

def get_available_servers(dbtype):
    """Get list of available server names for a database type"""
    url = "http://localhost:8082/connections"
    headers = {"X-API-KEY": "password"}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    servers = list(data['connections'][dbtype].keys())
    return servers

# Get all Oracle servers
oracle_servers = get_available_servers('oracle')
print(f"Available Oracle servers: {oracle_servers}")

# Get all MySQL servers
mysql_servers = get_available_servers('mysql')
print(f"Available MySQL servers: {mysql_servers}")
```

### Example 4: Find Default Connection

```python
import requests

def get_default_server(dbtype):
    """Get the default server name for a database type"""
    url = "http://localhost:8082/connections"
    headers = {"X-API-KEY": "password"}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    for name, info in data['connections'][dbtype].items():
        if info['is_default']:
            return name
    return None

# Find default MySQL server
default_mysql = get_default_server('mysql')
print(f"Default MySQL server: {default_mysql}")
```

## Use Cases

### 1. Discovery
Developers can discover which database connections are available without accessing the `.env` file or configuration.

### 2. Documentation
Use this endpoint to generate documentation about available data sources.

### 3. Dynamic UI
Build dynamic user interfaces that show available database options.

### 4. Validation
Verify that expected database connections are properly configured before making queries.

### 5. Monitoring
Check which database servers are configured in different environments (dev, staging, prod).

## Integration with Other Endpoints

### Using with getRecord

```python
import requests

# 1. Get available connections
connections_url = "http://localhost:8082/connections"
headers = {"X-API-KEY": "password", "Content-Type": "application/json"}

conn_response = requests.get(connections_url, headers=headers)
oracle_servers = list(conn_response.json()['connections']['oracle'].keys())

# 2. Use discovered server in getRecord
getrecord_url = "http://localhost:8082/getRecord"
payload = {
    "dbtype": "oracle",
    "server": oracle_servers[0],  # Use first available Oracle server
    "table": "users",
    "parameters": {"user_id": 12345}
}

record_response = requests.post(getrecord_url, json=payload, headers=headers)
print(record_response.json())
```

### Using with sqlExec

```python
import requests

# Discover MySQL servers
connections = requests.get(
    "http://localhost:8082/connections",
    headers={"X-API-KEY": "password"}
).json()

mysql_servers = connections['connections']['mysql']

# Execute query on each MySQL server
for server_name, server_info in mysql_servers.items():
    print(f"\nQuerying {server_name}...")
    
    response = requests.post(
        "http://localhost:8082/sqlExec",
        headers={"X-API-KEY": "password", "Content-Type": "application/json"},
        json={
            "dbtype": "mysql",
            "server": server_name,
            "sql": "SELECT COUNT(*) as total FROM users",
            "page": 1,
            "page_size": 10
        }
    )
    
    result = response.json()
    if result['status'] == 'success':
        print(f"  Total users: {result['records'][0]['total']}")
```

## Response Details

### Empty Database Type

If no connections are configured for a database type, it returns an empty object:

```json
{
  "oracle": {},
  "mysql": {},
  "postgres": {},
  "mssql": {}
}
```

### Default vs Named Connections

- **Default connection**: Set via individual environment variables (`ORACLE_HOST`, `MYSQL_HOST`, etc.)
  - Shows as `"default"` in the connections list
  - `is_default: true`

- **Named connections**: Set via `*_CONFIGS` JSON environment variables
  - Shows with the configured name
  - `is_default: false`

### Example with Multiple MySQL Servers

```json
{
  "mysql": {
    "production": {
      "name": "production",
      "type": "mysql",
      "config": {
        "host": "prod-db.example.com",
        "port": 3306,
        "db": "prod_db",
        "user": "prod_user",
        "password": "***HIDDEN***"
      },
      "is_default": false
    },
    "analytics": {
      "name": "analytics",
      "type": "mysql",
      "config": {
        "host": "analytics-db.example.com",
        "port": 3306,
        "db": "analytics",
        "user": "analytics_user",
        "password": "***HIDDEN***"
      },
      "is_default": false
    },
    "default": {
      "name": "default",
      "type": "mysql",
      "config": {
        "host": "localhost",
        "port": 3306,
        "db": "dev_db",
        "user": "dev_user",
        "password": "***HIDDEN***"
      },
      "is_default": true
    }
  }
}
```

## Security Considerations

### 1. Password Masking
All password fields are automatically masked with `***HIDDEN***`. This prevents accidental exposure of credentials.

### 2. API Key Required
The endpoint requires authentication via API key, preventing unauthorized access.

### 3. Read-Only
This endpoint is read-only and cannot be used to modify configurations.

### 4. Environment-Based
Actual passwords are only in the `.env` file, which should never be committed to version control.

## Error Responses

### 401 Unauthorized

Missing or invalid API key:

```json
{
  "detail": "Invalid or missing API key"
}
```

**Solution**: Provide valid API key in `X-API-KEY` header.

## Interactive Documentation

When running in DEV mode, this endpoint is available in:
- Swagger UI: `http://localhost:8082/docs`
- ReDoc: `http://localhost:8082/redoc`

You can test the endpoint interactively using the "Try it out" feature.

## Best Practices

1. **Cache the response**: Connection configurations don't change frequently, so cache the response for better performance
2. **Use for validation**: Before executing queries, verify the server name exists in the connections list
3. **Environment-specific**: Use this in dev/staging to verify configuration without accessing `.env` files
4. **Documentation**: Generate API documentation that includes available database connections

## Summary

The `/connections` endpoint provides:
- ✅ Complete list of all configured database connections
- ✅ Summary counts by database type
- ✅ Connection details (with passwords masked)
- ✅ Identification of default connections
- ✅ Secure, read-only access
- ✅ Integration-ready response format

Perfect for discovering available database servers before using `getRecord` or `sqlExec` endpoints!

