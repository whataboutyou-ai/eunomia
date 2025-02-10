import sys

from eunomia.instruments.sql_instrument import SqlInstrument


def test_sql_instrument_initialization(sql_instrument: SqlInstrument) -> None:
    assert sql_instrument._allowed_columns == {"id", "email", "status", "tenant_id"}
    assert sql_instrument._allowed_functions == {"concat", "count"}
    assert sql_instrument._row_filters == ["tenant_id = 100", "first_name = 'Mario'"]


def test_sql_instrument_run(
    sql_instrument: SqlInstrument, sql_sample_query: str
) -> None:
    rewritten_query = sql_instrument.run(sql_sample_query)

    # Check that 'secret_col' was dropped
    assert "secret_col" not in rewritten_query

    # 'id' and 'email' should remain
    assert "id" in rewritten_query
    assert "email" in rewritten_query

    # Row filters appended: expect "tenant_id = 100" and "first_name = 'Mario'"
    # combined with the existing WHERE:
    assert "tenant_id = 100" in rewritten_query
    assert "first_name = 'Mario'" in rewritten_query


def test_sql_instrument_run_with_where(
    sql_instrument: SqlInstrument, sql_sample_query_with_where: str
) -> None:
    rewritten_query = sql_instrument.run(sql_sample_query_with_where)

    # Check that 'secret_col' was dropped
    assert "secret_col" not in rewritten_query

    # 'id' and 'email' should remain
    assert "id" in rewritten_query
    assert "email" in rewritten_query

    # Row filters appended: expect "tenant_id = 100" and "first_name = 'Mario'"
    # combined with the existing WHERE:
    assert "status = 'active'" in rewritten_query
    assert "tenant_id = 100" in rewritten_query
    assert "first_name = 'Mario'" in rewritten_query
