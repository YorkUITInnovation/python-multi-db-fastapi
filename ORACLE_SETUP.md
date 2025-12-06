# Oracle Database Setup Guide

This guide explains how to set up and debug Oracle database connections in this FastAPI application.

## Prerequisites

### 1. Install Oracle Instant Client

The application requires Oracle Instant Client to support older password verifier types. We've provided an installation script:

```bash
./install_oracle_client.sh
```

This script will:
- Download Oracle Instant Client Basic Light (version 21.15)
- Extract it to `/opt/oracle/instantclient_21_15`
- Install required dependencies (`libaio1`)
- Configure the system library path

### 2. Configure Environment Variables

Add the following to your `.env` file:

```bash
ORACLE_CLIENT_LIB=/opt/oracle/instantclient_21_15
```

This enables "thick mode" which supports older Oracle password verifier types.

## Configuration

### Single Oracle Server

For a single Oracle database, use these environment variables:

```bash
ORACLE_HOST=your-oracle-host.example.com
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=your_service_name
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password
```

### Multiple Oracle Servers

For multiple Oracle databases, use the `ORACLE_CONFIGS` JSON object:

```bash
ORACLE_CONFIGS={"server1":{"dsn":"(DESCRIPTION=...)","user":"user1","password":"pass1"},"server2":{"host":"host2","port":1521,"service_name":"service2","user":"user2","password":"pass2"}}
```

Each server config can use either:
- **DSN string** (recommended for complex connection strings):
  ```json
  {
    "dsn": "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=host)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=service)))",
    "user": "username",
    "password": "password"
  }
  ```

- **Individual parameters**:
  ```json
  {
    "host": "hostname",
    "port": 1521,
    "service_name": "service_name",
    "user": "username",
    "password": "password"
  }
  ```

## Testing Connections

### Via API

Test the Oracle connection through the API:

```bash
curl -X 'GET' \
  'http://localhost:8082/oracle/sample?server=yustart' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: password'
```

### Via Python Script

Test directly using Python:

```python
from app.db_oracle import OracleDB
from app.config import get_oracle_config

config = get_oracle_config('yustart')
db = OracleDB(config)
try:
    rows = db.query('SELECT 1 AS one FROM dual')
    print('Success:', rows)
except Exception as e:
    print('Error:', e)
finally:
    db.close()
```

## Common Issues and Debugging

### Error: DPY-3015 (Password verifier type not supported)

**Problem**: `DPY-3015: password verifier type 0x939 is not supported by python-oracledb in thin mode`

**Solution**: 
1. Install Oracle Instant Client (see above)
2. Set `ORACLE_CLIENT_LIB` environment variable
3. Restart the application

**Why**: Older Oracle databases use password verifier types that require the Oracle Instant Client. The python-oracledb library needs to run in "thick mode" to support these.

### Error: DPY-6001 (Service not registered)

**Problem**: `DPY-6001: Service "..." is not registered with the listener`

**Possible causes**:
1. Wrong service name
2. Oracle listener not running
3. Network connectivity issues
4. Firewall blocking port 1521

**Debugging**:
```bash
# Test network connectivity
nc -zv oracle-host 1521

# Check if you can connect with SQLPlus (if available)
sqlplus username/password@host:1521/service_name
```

### Error: Connection timeout

**Possible causes**:
1. Firewall blocking traffic
2. Wrong host/port
3. Database server down

**Debugging**:
```bash
# Test if port is accessible
telnet oracle-host 1521
# or
nc -zv oracle-host 1521
```

### Debugging with Logging

The application includes comprehensive logging. Enable debug logging to see detailed connection information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Logs will show:
- Whether thick mode is enabled
- DSN being used (or parameters used to build it)
- Connection attempts and results
- Query execution details

### Verify Thick Mode

Check if thick mode is active:

```python
import oracledb
print("Thick mode:", oracledb.is_thin_mode() == False)
```

Or check the application logs when it starts - you should see:
```
INFO:app.db_oracle:Oracle client initialized in thick mode
```

## Troubleshooting Checklist

- [ ] Oracle Instant Client installed (`ls /opt/oracle/instantclient_21_15`)
- [ ] `ORACLE_CLIENT_LIB` set in `.env` file
- [ ] `libaio1` package installed (`dpkg -l | grep libaio`)
- [ ] Library path configured (`ldconfig -p | grep oracle`)
- [ ] Correct DSN or host/port/service_name in config
- [ ] Network connectivity to Oracle server (test with `nc -zv host port`)
- [ ] Valid credentials
- [ ] Application restarted after config changes

## Performance Tips

1. **Connection Pooling**: For production, consider using connection pools:
   ```python
   pool = oracledb.create_pool(user=user, password=password, dsn=dsn, min=2, max=10)
   ```

2. **Reuse Connections**: The current implementation creates a new connection per request. Consider implementing connection pooling for better performance.

3. **Query Optimization**: Use bind variables instead of string concatenation:
   ```python
   db.query("SELECT * FROM users WHERE id = :id", (user_id,))
   ```

## Security Notes

- Never commit `.env` files with real credentials
- Use environment-specific configurations
- Consider using secret management tools (AWS Secrets Manager, HashiCorp Vault, etc.)
- Rotate passwords regularly
- Use read-only database users when possible

## References

- [python-oracledb Documentation](https://python-oracledb.readthedocs.io/)
- [Oracle Instant Client Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html)
- [Thick vs Thin Mode](https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html)

