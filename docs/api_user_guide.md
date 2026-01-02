# API User Guide

## Authentication
All endpoints require an `X-API-KEY` header. Valid keys live in the `.env` configuration under `API_KEYS`. FastAPI registers an OpenAPI security scheme for this header, so `Authorize` in Swagger UI accepts the key once and reuses it for all requests.

## Common Parameters
- `dbtype`: expects `oracle`, `mysql`, `postgres`, or `mssql`. Determines which helper handles the SQL.
- `server`: selects a named connection defined per-DB in the `.env`. When only one server exists, `server` may be omitted.
- `parameters`: JSON object with field names as keys and their typed values. Helpers bind these safely to `:param` placeholders.
- `fields`: Optional comma-separated list overriding the default `*` select list.
- `page` / `page_size`: Used by paginated endpoints like `sqlExec` to limit responses.

## Endpoints
### `GET /get-record`
Returns a single matching row.
- Required: `dbtype`, `table`, `parameters` (JSON object), `server` optional if only one server defined.
- Optional: `fields` overrides columns returned.
- Fails with 400 if zero rows or more than one row match; use `sqlExec` for multi-row results.

### `POST /sql-exec`
Generic SQL runner with pagination.
- Required: `dbtype`, `sql` (a SELECT statement using placeholders like `:myparam`), `parameters` for the WHERE clause.
- Optional: `server`, `page`, `page_size` (capped at 300 and defaults to 100).
- Returns pagination metadata: `page`, `page_size`, `record_count`, `total_records`, and `total_pages` so you know the position inside the full result set.
- Use `parameters` keys to bind into the SQL statement (e.g., `"firstname": "patrick"` allows `WHERE firstname = :firstname`).

### `POST /insert-record`
Inserts a row into the specified table.
- Required: `dbtype`, `table`, `parameters` (field → value map), `server` optional when only one server is defined.
- `parameters` uses a JSON object where each key is the column name and its value is the literal inserted value.
- Returns the native database response and affected row count where supported.

### `POST /update-record`
Updates rows matching the provided criteria.
- Required: `dbtype`, `table`, `parameters` for values to set, `filters` for W WHERE clause, optional `server`, `fields` not used.
- The `filters` object uses the same format as `parameters` but is only used inside the `WHERE` clause to identify target rows.
- If more than one row matches, the update still runs; `record_count` reports how many rows were changed.

### `DELETE /delete-record`
Deletes rows based on the supplied filters.
- Required: `dbtype`, `table`, `filters` as a JSON object mapping column names to values, optional `server` when only one configured.
- Returns how many rows were deleted.

## Parameter Format Example
```json
{
  "dbtype": "mysql",
  "table": "users",
  "parameters": {
    "firstname": "Patrick",
    "id": 42
  }
}
```
The keys become bind parameters in the generated SQL (e.g., `firstname = :firstname`). Numbers and strings are handled automatically by the underlying drivers.

## DSN vs. Host/Service
- Oracle connections support full DSN strings for complex descriptors (failover, load balancing, etc.). Supply the descriptor via the `.env` entry for that server.
- Simple host/port/service combinations also work for Oracle, MySQL, PostgreSQL, and MSSQL.

## Pagination Notes
- `sqlExec` enforces a maximum of 300 records per page. Use `page` to request successive slices.
- Response fields:
  - `page`: current page number.
  - `page_size`: how many rows were requested.
  - `record_count`: rows actually returned.
  - `total_records`: total matches ignoring pagination (useful for UI progress bars).
  - `total_pages`: derived from `total_records`/`page_size`.

## Debugging Tips
- Enable verbose logging in your client and watch the FastAPI console for SQL/parameter output.
- Use `curl` or Postman with `X-API-KEY` and inspect HTTP status codes to determine whether failures are authentication-, syntax-, or backend-specific.
- For Oracle DSN issues, test connectivity via `sqlplus` or SQL Developer with the same descriptor to confirm listener availability before retrying through the API.
