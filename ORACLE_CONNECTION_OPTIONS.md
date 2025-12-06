# Oracle Connection Configuration Options

## TL;DR - You have TWO options:

With Oracle Instant Client installed and thick mode enabled, you can use **either**:

### Option 1: Simple (Recommended for most cases)
```json
{
  "host": "a-host-url",
  "port": 1521,
  "service_name": "a-service-name",
  "user": "username",
  "password": "password"
}
```

### Option 2: Full DSN String (Only needed for advanced features)
```json
{
  "dsn": "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=a-host-url)(PORT=1521))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=a-service-name)(FAILOVER_MODE=(TYPE=select)(METHOD=basic))))",
  "user": "username",
  "password": "password"
}
```

---

## Detailed Comparison

### Simple Method (host, port, service_name)

**Pros:**
- ✅ Much easier to read and maintain
- ✅ Less prone to typos
- ✅ Easier to edit individual values
- ✅ Works for 95% of use cases

**Cons:**
- ❌ Cannot specify advanced Oracle options (like FAILOVER_MODE, LOAD_BALANCE, etc.)

**Example in .env:**
```bash
ORACLE_CONFIGS={"yustart":{"host":"a-host-url","port":1521,"service_name":"a-service-name","user":"yustart","password":"pass123"},"eclass":{"host":"a-host-url","port":1521,"service_name":"a-service-name","user":"moodle_reader","password":"pass456"}}
```

**What it generates internally:**
```
(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=a-host-url)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=a-service-name)))
```

---

### Full DSN String Method

**Pros:**
- ✅ Supports all Oracle connection features
- ✅ Can specify FAILOVER_MODE, LOAD_BALANCE, multiple addresses, etc.
- ✅ Exact control over connection parameters

**Cons:**
- ❌ Much longer and harder to read
- ❌ Easy to make syntax errors in parentheses
- ❌ Difficult to edit individual values

**Example in .env:**
```bash
ORACLE_CONFIGS={"yustart":{"dsn":"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=a-host-url)(PORT=1521))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=a-service-name)(FAILOVER_MODE=(TYPE=select)(METHOD=basic))))","user":"yustart","password":"pass123"}}
```

**When to use:**
- You need Oracle RAC failover/load balancing
- You have multiple connection addresses
- You need specific connection timeout settings
- Your DBA gave you a specific connection string

---

## Recommendation

**Use the simple method** (host, port, service_name) unless:
1. Your DBA specifically requires a certain DSN format
2. You need Oracle RAC features (failover, load balancing)
3. You have multiple addresses for the same service

The simple method is:
- Easier to maintain
- Less error-prone
- More readable
- Sufficient for most applications

---

## Your Current Configuration

Your `.env` file now uses the **simple method**:

```bash
ORACLE_CONFIGS={"yustart":{"host":"a-host-url","port":1521,"service_name":"a-service-name","user":"yustart","password":"Srlyz7ejGUrFLsh"},"eclass":{"host":"a-host-url","port":1521,"service_name":"a-service-name","user":"moodle_reader","password":"R3ad4M00der"}}
```

This is much cleaner and easier to manage! ✅

---

## Advanced DSN Features (if you need them)

If you do need the advanced features, here's what the DSN string can specify:

```
(DESCRIPTION=
  (ADDRESS=(PROTOCOL=TCP)(HOST=host1)(PORT=1521))
  (ADDRESS=(PROTOCOL=TCP)(HOST=host2)(PORT=1521))  # Multiple hosts for failover
  (CONNECT_DATA=
    (SERVER=DEDICATED)                              # or SHARED
    (SERVICE_NAME=myservice)
    (FAILOVER_MODE=                                 # Automatic failover
      (TYPE=select)                                 # or session
      (METHOD=basic)                                # or preconnect
    )
  )
  (LOAD_BALANCE=yes)                               # Load balancing across addresses
  (CONNECT_TIMEOUT=60)                             # Connection timeout in seconds
)
```

But again, **you don't need this complexity for your current setup!**

---

## Testing Both Methods

Both methods were tested and confirmed working:

```bash
# Test 1: Simple method
✓ Individual parameters method works! Result: (1,)

# Test 2: DSN string method  
✓ DSN string method works! Result: (1,)
```

**Conclusion:** Use the simple method for easier maintenance! 🎉

