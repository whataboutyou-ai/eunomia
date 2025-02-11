## `SqlInstrument` 

`SqlInstrument` is an instrument that sanitizes SQL queries by:

1.  **Whitelisting** only certain columns and SQL functions in the `SELECT`, `UPDATE`, and `INSERT` clauses. 
2.  **Enforcing** row-level filters by:
    -  appending specific `WHERE` conditions to `SELECT` and `UPDATE` clauses.
    -  enforcing specific values for certain columns in `INSERT` clauses.
3.  **Discarding** any disallowed columns or functions from the final SQL statement.

The SQL Instrument uses [SQLGlot][sql-glot-website].

## Configuration

| Argument | Type | Description |
| -------- | ---- | ----------- |
| `allowed_columns` | `list[str]` | List of columns that are permitted to appear in the final `SELECT`, `UPDATE`, or `INSERT` clauses. Any column reference **not** in this list will be removed from the query. |
| `allowed_functions`| `list[str]` | List of SQL function names allowed in the `SELECT`, `UPDATE`, or `INSERT` clauses. For example, `["COUNT", "CONCAT", "SUBSTR"]`. Any function call **not** in this list will be removed from the final query. |
| `row_filters` | `list[str] | None` | One or more SQL boolean expressions (without the `WHERE` keyword). <br/> - In `SELECT` and `UPDATE` queries, these will be appended to the existing `WHERE` clause or create a new one if it doesn't exist. Multiple filters get combined with an `AND`; for example, `["tenant_id = 100", "deleted_at IS NULL"]`. <br/> - In `INSERT` queries, these will be used to enforce specific values for certain columns. |

## Usage Example

```py title="examples/sql_queries.py"
--8<-- "examples/sql_queries.py"
```


This snippet will:

1. **Drop** any references to columns not in `allowed_columns` (e.g., `secret_col`, if not added to the list).  
2. **Remove** function calls not in `allowed_functions` (e.g., `SUBSTR` here).  
3. **Append** the row filters `(tenant_id = 100 AND deleted_at IS NULL)` to the existing `WHERE` condition, provided those columns exist in `allowed_columns`.  

As a result, you get a final sanitized SQL that enforces row-level security and strips out disallowed columns or functions.

[sql-glot-website]: https://sqlglot.com/sqlglot.html
