import sys
from eunomia.instruments.sql_instrument import SqlInstrument

def sql_instrument() -> SqlInstrument:
    """
    A pytest fixture that instantiates the SqlInstrument with some
    sample allowed columns, functions, and row filters.
    """
    return SqlInstrument(
        allowed_columns=["id", "email", "status", "tenant_id"],
        allowed_functions=["CONCAT", "COUNT"],
        row_filter=["tenant_id = 100", "first_name = 'Mario'"]
    )

def test_sql_instrument_initialization(sql_instrument: SqlInstrument) -> None:
    """
    Test that the SqlInstrument is initialized with the correct settings.
    """
    # The instrument lower-cases the columns/functions internally
    assert sql_instrument._allowed_columns == {"id", "email", "status", "tenant_id"}
    assert sql_instrument._allowed_functions == {"concat", "count"}
    assert sql_instrument._row_filter == ["tenant_id = 100", "first_name = 'Mario'"]

def test_sql_instrument_run(sql_instrument: SqlInstrument) -> None:
    """
    Test that the 'run' method correctly rewrites a sample SQL query:
      - Removes disallowed columns (e.g., 'secret_col')
      - Preserves allowed columns (e.g., 'id', 'email')
      - Preserves allowed functions (e.g., 'COUNT')
      - Appends row filters (tenant_id=100 AND first_name='Mario')
    """

    original_query = """
        SELECT
            id,
            email,
            secret_col,    -- disallowed column
            CONCAT(first_name, ' ', last_name) AS full_name, -- allowed function, but 'first_name' & 'last_name' not in allowed_columns
            COUNT(*) AS total
        FROM users
        WHERE status = 'active'
    """

    rewritten_query = sql_instrument.run(original_query)

    # Check that 'secret_col' was dropped
    assert "secret_col" not in rewritten_query

    # 'id' and 'email' should remain
    assert "id" in rewritten_query
    assert "email" in rewritten_query

    # 'CONCAT' might be removed if 'first_name' or 'last_name' aren't in allowed_columns
    # But 'COUNT(*)' should remain, unless your sanitizer disallows `*` within COUNT.
    # Let's just check for 'COUNT' as an example:
    assert "COUNT" in rewritten_query

    # Row filters appended: expect "tenant_id = 100" and "first_name = 'Mario'" 
    # combined with the existing WHERE:
    assert "tenant_id = 100" in rewritten_query
    assert "first_name = 'Mario'" in rewritten_query

    # Optionally, check final structure if you want:
    # e.g. "WHERE status = 'active' AND tenant_id = 100 AND first_name = 'Mario'"
    # (Exact spacing may vary, so a substring check is often enough)
    assert "status = 'active'" in rewritten_query
    assert "AND tenant_id = 100" in rewritten_query
    assert "AND first_name = 'Mario'" in rewritten_query
