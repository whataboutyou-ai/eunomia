import sys

from eunomia.instruments import RbacInstrument, SqlInstrument
from eunomia.orchestra import Orchestra

# Define policy for "alice"
instrument_alice = SqlInstrument(
    allowed_columns=["id", "email", "status", "first_name", "last_name", "total"],
    allowed_functions=["CONCAT", "COUNT"],  # Alice can use CONCAT and COUNT
    row_filters=["tenant_id = 100", "first_name = 'Mario' "],  # multiple row filters
)

# Define policy for "bob"
instrument_bob = SqlInstrument(
    allowed_columns=["id", "email", "tenant_id"],
    allowed_functions=["COUNT"],  # Bob can only use COUNT, not CONCAT
    row_filters=["tenant_id = 200"],  # single row filter
)

# Create the Orchestra with an RBAC layer:
orchestra = Orchestra(
    instruments=[
        RbacInstrument(
            role="alice",
            instruments=[instrument_alice],
        ),
        RbacInstrument(
            role="bob",
            instruments=[instrument_bob],
        ),
    ]
)

test_query = """
    SELECT
        id,
        email,
        secret_col,
        CONCAT(first_name, ' ', last_name) AS full_name,
        COUNT(id) AS total,
        SUBSTR(email, 1, 5) AS partial_email
    FROM users
    WHERE status = 'active' OR is_test = 1
"""

if __name__ == "__main__":
    # Run for "alice"
    try:
        rewritten_for_alice = orchestra.run(test_query, role="alice")
        print("=== ALICE ORIGINAL QUERY ===")
        print(test_query)
        print("\n=== ALICE REWRITTEN QUERY ===")
        print(rewritten_for_alice)
    except Exception as e:
        print("Alice rewrite error:", e)

    # Run for "bob"
    try:
        rewritten_for_bob = orchestra.run(test_query, role="bob")
        print("\n=== BOB ORIGINAL QUERY ===")
        print(test_query)
        print("\n=== BOB REWRITTEN QUERY ===")
        print(rewritten_for_bob)
    except Exception as e:
        print("Bob rewrite error:", e)
