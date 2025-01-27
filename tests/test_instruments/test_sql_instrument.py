import sys

from eunomia.instruments.sql_instrument import SqlInstrument


def sql_instrument() -> SqlInstrument:
    return SqlInstrument(
        allowed_columns=["id", "email", "status", "tenant_id"],
        allowed_functions=["CONCAT", "COUNT"],
        row_filter=["tenant_id = 100", "first_name = 'Mario'"],
    )


def test_sql_instrument_initialization(sql_instrument: SqlInstrument) -> None:
    assert sql_instrument._allowed_columns == {"id", "email", "status", "tenant_id"}
    assert sql_instrument._allowed_functions == {"concat", "count"}
    assert sql_instrument._row_filter == ["tenant_id = 100", "first_name = 'Mario'"]


def test_sql_instrument_run(sql_instrument: SqlInstrument) -> None:
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

    # Row filters appended: expect "tenant_id = 100" and "first_name = 'Mario'"
    # combined with the existing WHERE:
    assert "tenant_id = 100" in rewritten_query
    assert "first_name = 'Mario'" in rewritten_query
