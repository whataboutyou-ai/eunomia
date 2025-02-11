from typing import Optional

from sqlglot import exp, parse_one

from eunomia.instrument import Instrument


class SqlInstrument(Instrument):
    """
    An instrument that edits SQL queries using SQLGlot.
    """

    def __init__(
        self,
        allowed_columns: list[str],
        allowed_functions: list[str],
        row_filters: Optional[list[str]],
    ):
        self._allowed_columns = set([c.lower() for c in allowed_columns])
        self._allowed_functions = set([f.lower() for f in allowed_functions])
        self._row_filters = self._parse_filters(row_filters or [])

    def _parse_filters(self, str_filters: list[str]) -> list[exp.Expression]:
        """Parse string filters into a list of expressions."""
        parsed_filters = []
        for filter_str in str_filters:
            try:
                row_filter_statement = parse_one(
                    f"SELECT * FROM dummy WHERE {filter_str}"
                )
                filter_expression = row_filter_statement.find(exp.Where).this
            except Exception as e:
                raise ValueError(f"Could not parse row filter '{filter_str}': {e}")

            parsed_filters.append(filter_expression)

        return parsed_filters

    def _sanitize_column_expression(
        self, expression: exp.Expression
    ) -> exp.Expression | None:
        """
        Return a sanitized version of the expression if safe,
        or None if the expression references anything disallowed.
        """
        if isinstance(expression, exp.Identifier):
            # Simple column reference (e.g. 'email')
            col_name = expression.name.lower()
            return expression if col_name in self._allowed_columns else None

        elif isinstance(expression, exp.Column):
            # Qualified column reference (e.g. 'users.email')
            col_name = expression.name.lower()
            # Optionally, check table name in expression.table
            return expression if col_name in self._allowed_columns else None

        elif isinstance(expression, exp.Alias):
            # e.g.  email AS e
            # We'll sanitize the underlying expression
            child = self._sanitize_column_expression(expression.this)
            if child is None:
                return None
            # Clone the alias but replace its child with the sanitized child
            new_alias = expression.copy()
            new_alias.set("this", child)
            return new_alias

        elif isinstance(expression, exp.Func):
            # e.g. COUNT(...), CONCAT(...), etc.
            func_name = expression.key.lower()
            if func_name not in self._allowed_functions:
                return None
            # We need to sanitize all function arguments (sub-expressions)
            new_args = []
            for arg in expression.args.values():
                if isinstance(arg, list):
                    # Some functions have a list of expressions (e.g. CONCAT(x, y))
                    safe_args = []
                    for sub_arg in arg:
                        sub_sanitized = self._sanitize_column_expression(sub_arg)
                        if sub_sanitized is None:
                            return None  # If any argument is disallowed, drop the entire function
                        safe_args.append(sub_sanitized)
                    new_args.append(safe_args)
                elif isinstance(arg, exp.Expression):
                    sub_sanitized = self._sanitize_column_expression(arg)
                    if sub_sanitized is None:
                        return None
                    new_args.append(sub_sanitized)
                else:
                    new_args.append(arg)

            # Rebuild the function expression with sanitized arguments
            new_func = expression.copy()
            for key, val in zip(expression.args.keys(), new_args):
                new_func.set(key, val)
            return new_func

        elif isinstance(expression, exp.Literal):
            # E.g. 'active', 123, etc.
            return expression

        elif isinstance(expression, exp.Case):
            # E.g. CASE expressions
            return None

        # Anything else => drop it
        return None

    def _add_where_clause(
        self, main_expression: exp.Expression, connector: type[exp.Connector] = exp.And
    ) -> None:
        """
        Add a WHERE clause or combine existing WHERE clause with new filters.

        Args:
            main_expression: The main expression to add the WHERE clause to.
            connector: Multiple filters are combined using this connector. Defaults to AND.
        """
        combined_row_filters = None
        for row_filter in self._row_filters:
            combined_row_filters = (
                row_filter
                if combined_row_filters is None
                else connector(this=combined_row_filters, expression=row_filter)
            )

        if combined_row_filters is not None:
            where_node = main_expression.args.get("where")

            if where_node:
                # existing WHERE, so combine
                existing_where = where_node.this
                new_where_condition = exp.And(
                    this=existing_where, expression=combined_row_filters
                )
                where_node.set("this", new_where_condition)
            else:
                # create a new WHERE if none exists
                new_where_node = exp.Where()
                new_where_node.set("this", combined_row_filters)
                main_expression.set("where", new_where_node)
        return

    def _run_select_statement(self, select_expression: exp.Select) -> None:
        """
        Run the instrument's logic on a SELECT statement.
        """
        # enforce column-level filters
        sanitized_select_expressions = []
        for expression in select_expression.expressions:
            sanitized_expression = self._sanitize_column_expression(expression)
            if sanitized_expression is not None:
                sanitized_select_expressions.append(sanitized_expression)

        if not sanitized_select_expressions:
            raise ValueError(
                "No valid columns or expressions remain in the SELECT list after sanitization."
            )

        select_expression.set("expressions", sanitized_select_expressions)

        # enforce row-level filters
        self._add_where_clause(select_expression)

        return

    def _run_update_statement(self, update_expression: exp.Update) -> None:
        """
        Run the instrument's logic on an UPDATE statement.
        """
        # enforce column-level filters
        sanitized_update_expressions = []
        for expression in update_expression.expressions:
            # expression is exp.EQ, so we sanitize its child
            sanitized_child_expression = self._sanitize_column_expression(
                expression.this
            )
            if sanitized_child_expression is not None:
                sanitized_expression = expression.copy()
                sanitized_expression.set("this", sanitized_child_expression)
                sanitized_update_expressions.append(sanitized_expression)

        if not sanitized_update_expressions:
            raise ValueError(
                "No valid columns or expressions remain in the UPDATE list after sanitization."
            )

        update_expression.set("expressions", sanitized_update_expressions)

        # enforce row-level filters
        self._add_where_clause(update_expression)

        return

    def _run_insert_statement(self, insert_expression: exp.Insert) -> None:
        """
        Run the instrument's logic on an INSERT statement.
        """
        if not isinstance(insert_expression.expression, exp.Values):
            raise ValueError("Expected a VALUES expression in INSERT statements")

        # prepare row filters in a dict for easier retrieval
        row_filters_dict = {}
        for row_filter in self._row_filters:
            if not isinstance(row_filter, exp.EQ):
                raise ValueError(
                    "Expected only EQ expressions in the row filters for INSERT statements"
                )
            row_filters_dict[row_filter.this.this] = row_filter.expression

        sanitized_insert_expressions, sanitized_insert_values = [], []
        for expression, value in zip(
            insert_expression.this.expressions,
            insert_expression.expression.expressions[0].expressions,
        ):
            sanitized_expression = self._sanitize_column_expression(expression)
            if sanitized_expression is not None:
                sanitized_insert_expressions.append(sanitized_expression)

                sanitized_value = row_filters_dict.get(sanitized_expression) or value
                sanitized_insert_values.append(sanitized_value)

        if not sanitized_insert_expressions:
            raise ValueError(
                "No valid columns or expressions remain in the INSERT list after sanitization."
            )

        insert_expression.this.set("expressions", sanitized_insert_expressions)
        insert_expression.expression.expressions[0].set(
            "expressions", sanitized_insert_values
        )
        return

    def run(self, query: str, **kwargs) -> str:
        try:
            statement = parse_one(query)
        except Exception as e:
            raise ValueError(f"Could not parse SQL: {e}")

        select_expression = (
            statement
            if isinstance(statement, exp.Select)
            else statement.find(exp.Select)
        )
        update_expression = (
            statement
            if isinstance(statement, exp.Update)
            else statement.find(exp.Update)
        )
        insert_expression = (
            statement
            if isinstance(statement, exp.Insert)
            else statement.find(exp.Insert)
        )
        if not select_expression and not update_expression and not insert_expression:
            raise ValueError(
                "SQL instrument only supports SELECT, UPDATE, or INSERT statements."
            )

        if select_expression:
            self._run_select_statement(select_expression)

        if update_expression:
            self._run_update_statement(update_expression)

        if insert_expression:
            self._run_insert_statement(insert_expression)

        return statement.sql()
