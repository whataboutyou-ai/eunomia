## `SqlInstrument` 

`SqlInstrument` is an instrument that sanitizes SQL queries by:

1. **Whitelisting** only certain columns and SQL functions in the `SELECT` clause.  
2. **Enforcing** row-level filters by appending specific `WHERE` conditions (e.g., tenant or user-based).  
3. **Discarding** any disallowed columns or functions from the final SQL.

The SQL Instrument uses [SQLGlot][sql-glot-website].

## Configuration

| Argument           | Type           | Description                                                                                                                                                                                                                                                                                                                                               |
| ------------------ | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `allowed_columns`  | `list[str]`   | List of columns that are permitted to appear in the final `SELECT` or `WHERE`. Any column reference **not** in this list will be removed from the query.                                                                                                                                                                                                 |
| `allowed_functions`| `list[str]`   | List of SQL function names allowed in the `SELECT` expressions. For example, `["COUNT", "CONCAT", "SUBSTR"]`. Any function call **not** in this list will be removed from the final query.                                                                                                                                                                  |
| `row_filter`       | `list[str]`   | One or more SQL boolean expressions (without the `WHERE` keyword) that will be appended to the existing `WHERE` clause. Multiple filters get combined with an `AND`. For example, `["tenant_id = 100", "deleted_at IS NULL"]`. If these filters reference columns **not** in `allowed_columns`, they may also be sanitized away or cause the filter to be dropped. |

## Usage Example

```py title="examples/sql_instrument_usage.py"
from eunomia.instruments import SqlInstrument

# Example: Alice can view only certain columns and use CONCAT, COUNT
instrument_alice = SqlInstrument(
    allowed_columns=["id", "email", "tenant_id", "first_name", "last_name"],
    allowed_functions=["CONCAT", "COUNT"],
    row_filter=["tenant_id = 100", "deleted_at IS NULL"]
)

# Example SQL query that references both allowed and disallowed items
original_query = """
    SELECT
        id,
        email,
        secret_col,
        CONCAT(first_name, ' ', last_name) AS full_name,
        COUNT(*) AS total,
        SUBSTR(email, 1, 5) AS partial_email
    FROM users
    WHERE status = 'active' OR is_test = 1
"""

rewritten_query = instrument_alice.run(original_query)
print("Rewritten query for Alice:")
print(rewritten_query)
```

This snippet will:

1. **Drop** any references to columns not in `allowed_columns` (e.g., `secret_col`, if not added to the list).  
2. **Remove** function calls not in `allowed_functions` (e.g., `SUBSTR` here).  
3. **Append** the row filters `(tenant_id = 100 AND deleted_at IS NULL)` to the existing `WHERE` condition, provided those columns exist in `allowed_columns`.  

As a result, you get a final sanitized SQL that enforces row-level security and strips out disallowed columns or functions.

[sql-glot-website]: https://sqlglot.com/sqlglot.html