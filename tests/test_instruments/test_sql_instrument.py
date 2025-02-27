from sqlglot import exp

from eunomia.instruments.sql_instrument import SqlInstrument


def test_sql_instrument_initialization(sql_instrument: SqlInstrument) -> None:
    assert sql_instrument._allowed_columns == {"id", "email", "status", "tenant_id"}
    assert sql_instrument._allowed_functions == {"concat", "count"}
    assert sql_instrument._row_filters == [
        exp.EQ(
            this=exp.Column(this=exp.Identifier(this="tenant_id", quoted=False)),
            expression=exp.Literal(this="100", is_string=False),
        ),
        exp.EQ(
            this=exp.Column(this=exp.Identifier(this="first_name")),
            expression=exp.Literal(this="Mario", is_string=True),
        ),
    ]


def test_sql_instrument_select_run(
    sql_instrument: SqlInstrument, sql_select_query: str
) -> None:
    rewritten_query = sql_instrument.run(sql_select_query)

    # Check that 'secret_col' was dropped
    assert "secret_col" not in rewritten_query

    # 'id' and 'email' should remain
    assert "id" in rewritten_query
    assert "email" in rewritten_query

    # Row filters appended: expect "tenant_id = 100" and "first_name = 'Mario'"
    # combined with the existing WHERE:
    assert "tenant_id = 100" in rewritten_query
    assert "first_name = 'Mario'" in rewritten_query


def test_sql_instrument_select_run_with_where(
    sql_instrument: SqlInstrument, sql_select_query_with_where: str
) -> None:
    rewritten_query = sql_instrument.run(sql_select_query_with_where)

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


def test_sql_instrument_update_run(
    sql_instrument: SqlInstrument, sql_update_query: str
) -> None:
    rewritten_query = sql_instrument.run(sql_update_query)

    assert "email = 'example@example,com'" in rewritten_query
    assert "secret_col" not in rewritten_query

    assert "status = 'active'" in rewritten_query
    assert "tenant_id = 100" in rewritten_query
    assert "first_name = 'Mario'" in rewritten_query


def test_sql_instrument_insert_run(
    sql_instrument: SqlInstrument, sql_insert_query: str
) -> None:
    rewritten_query = sql_instrument.run(sql_insert_query)

    assert "email" in rewritten_query
    assert "secret_col" not in rewritten_query
    assert "tenant_id" in rewritten_query

    # row filters
    assert "100" in rewritten_query
    assert "200" not in rewritten_query
