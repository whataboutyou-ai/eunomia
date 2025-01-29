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
        row_filter: list[str],
    ):
        self._allowed_columns = set([c.lower() for c in allowed_columns])
        self._allowed_functions = set([f.lower() for f in allowed_functions])
        self._row_filter = row_filter

    def _sanitize_expression(self, expression: exp.Expression) -> exp.Expression | None:
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
            child = self._sanitize_expression(expression.this)
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
                        sub_sanitized = self._sanitize_expression(sub_arg)
                        if sub_sanitized is None:
                            return None  # If any argument is disallowed, drop the entire function
                        safe_args.append(sub_sanitized)
                    new_args.append(safe_args)
                elif isinstance(arg, exp.Expression):
                    sub_sanitized = self._sanitize_expression(arg)
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

    def run(self, query: str, **kwargs) -> str:
        try:
            statement = parse_one(query)
        except Exception as e:
            raise ValueError(f"Could not parse SQL: {e}")

        # -------------------------------------------------------
        # ENFORCE COLUMN-LEVEL FILTERS
        # -------------------------------------------------------

        # Find the (first) SELECT statement if it's not at the root
        select_expr = (
            statement
            if isinstance(statement, exp.Select)
            else statement.find(exp.Select)
        )
        if not select_expr or not isinstance(select_expr, exp.Select):
            raise ValueError(
                "Rewrite currently only supports a single SELECT statement."
            )

        sanitized_select_expressions = []
        for proj in select_expr.expressions:
            safe_proj = self._sanitize_expression(proj)
            if safe_proj is not None:
                sanitized_select_expressions.append(safe_proj)

        if not sanitized_select_expressions:
            raise ValueError(
                "No valid columns or expressions remain in the SELECT list after sanitization."
            )

        # Replace the original select list with the sanitized list
        select_expr.set("expressions", sanitized_select_expressions)

        # -------------------------------------------------------
        # ENFORCE ROW-LEVEL FILTERS
        # -------------------------------------------------------
        combined_row_filters = None
        for rf_str in self._row_filter:
            try:
                row_filter_stmt = parse_one(f"SELECT * FROM dummy WHERE {rf_str}")
                where_stmt = row_filter_stmt.find(exp.Where)
                filter_exp = row_filter_stmt.find(exp.Where).this
            except Exception as e:
                raise ValueError(f"Could not parse row filter '{rf_str}': {e}")

            if combined_row_filters is None:
                combined_row_filters = filter_exp
            else:
                combined_row_filters = exp.And(
                    this=combined_row_filters, expression=filter_exp
                )

        if combined_row_filters is not None:
            where_node = select_expr.args.get("where")

            if where_node:
                # existing WHERE, so combine
                existing_where = where_node.this
                new_where_condition = exp.And(
                    this=existing_where, expression=combined_row_filters
                )
                where_node.set("this", new_where_condition)
            else:
                # create a new WHERE if none exists
                select_expr.set("where", exp.Where(expression=combined_row_filters))

        # Return the modified SQL
        return statement.sql()
