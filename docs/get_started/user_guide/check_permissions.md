The **`POST /check`** endpoint verifies whether a principal is allowed to perform an action on a resource based on their attributes. The API evaluates the authorization policies using a combination of fetched entity attributes and/or attributes provided at runtime. The endpoint returns a boolean value (`true` for allowed action, `false` for denied action).

You have three options when calling this API:

1. **Using Identifiers Only:**  
   Supply the registered identifiers of the principal and resource. The server will fetch their attributes from the database.

2. **Using New Entities (Attributes Only):**  
   Do not provide registered identifiers. Instead, supply the attributes directly in the request. In this case, no fetching is performed; only the runtime attributes are used.

3. **Using Identifiers and Attributes:**  
   Provide both the registered identifiers and additional attributes. The server will merge the fetched attributes with those given at runtime before performing the authorization check.

---

## Option 1: Using Identifiers Only

In this option, you provide only the **`uri`** for both the principal and resource. The server will fetch the corresponding attributes from the database.

=== "Python"
    ```python
    from eunomia_sdk_python import EunomiaClient

    eunomia = EunomiaClient()

    # Option 1: Using identifiers only.
    # Assume that the entities are already registered in the system.
    # Allowed action (the registered principal's attributes satisfy the policy)
    result1 = eunomia.check({
        "resource": {"uri": "it-desk-agent"},
        "principal": {"uri": "registered-principal-001"}
    })
    print("Allowed:", result1)  # Expected output: True

    # Denied action (the registered principal's attributes do not meet the policy)
    result2 = eunomia.check({
        "resource": {"uri": "hr-agent"},
        "principal": {"uri": "registered-principal-003"}
    })
    print("Allowed:", result2)  # Expected output: False
    ```

=== "Curl"
    ```bash
    # Option 1: Using identifiers only.
    # Allowed action
    curl -X POST 'http://localhost:8000/check' \
         -H "Content-Type: application/json" \
         -d '{"resource": {"uri": "it-desk-agent"}, "principal": {"uri": "registered-principal-001"}}'

    # Denied action
    curl -X POST 'http://localhost:8000/check' \
         -H "Content-Type: application/json" \
         -d '{"resource": {"uri": "hr-agent"}, "principal": {"uri": "registered-principal-003"}}'
    ```

=== "Output"
    ```bash
    true
    false
    ```

---

## Option 2: Using New Entities (Attributes Only)

In this option, you do not provide registered identifiers for the entities. Instead, you supply the attributes directly in the request. The server uses these runtime attributes exclusively for the authorization check.

=== "Python"
    ```python
    # Option 2: Using new entities (attributes provided at runtime).
    # Allowed action
    result1 = eunomia.check({
        "resource": {"uri": "it-desk-agent"},
        "principal": {"attributes": {"department": "it"}}
    })
    print("Allowed:", result1)  # Expected output: True

    result2 = eunomia.check({
        "resource": {"uri": "hr-agent"},
        "principal": {"attributes": {"department": "hr", "role": "manager"}}
    })
    print("Allowed:", result2)  # Expected output: True

    # Denied action
    result3 = eunomia.check({
        "resource": {"uri": "it-desk-agent"},
        "principal": {"attributes": {"department": "sales"}}
    })
    print("Allowed:", result3)  # Expected output: False

    result4 = eunomia.check({
        "resource": {"uri": "hr-agent"},
        "principal": {"attributes": {"department": "hr", "role": "analyst"}}
    })
    print("Allowed:", result4)  # Expected output: False
    ```

=== "Curl"
    ```bash
    # Option 2: Using new entities (attributes provided at runtime).
    # Allowed action
    curl -X POST 'http://localhost:8000/check' \
         -H "Content-Type: application/json" \
         -d '{"resource": {"uri": "it-desk-agent"}, "principal": {"attributes": {"department": "it"}}}'

    curl -X POST 'http://localhost:8000/check' \
         -H "Content-Type: application/json" \
         -d '{"resource": {"uri": "hr-agent"}, "principal": {"attributes": {"department": "hr", "role": "manager"}}}'

    # Denied action
    curl -X POST 'http://localhost:8000/check' \
         -H "Content-Type: application/json" \
         -d '{"resource": {"uri": "it-desk-agent"}, "principal": {"attributes": {"department": "sales"}}}'

    curl -X POST 'http://localhost:8000/check' \
         -H "Content-Type: application/json" \
         -d '{"resource": {"uri": "hr-agent"}, "principal": {"attributes": {"department": "hr", "role": "analyst"}}}'
    ```

=== "Output"
    ```bash
    true
    true
    false
    false
    ```

---

## Option 3: Using Identifiers and Attributes

In this option, you provide both the registered **`uri`** and additional attributes in the request. The server merges the registered attributes with the runtime attributes, and the resulting set is used for the authorization check.

=== "Python"
    ```python
    # Option 3: Using both identifiers and additional runtime attributes.
    # Allowed action: The registered principal is enriched with runtime attributes.
    result1 = eunomia.check({
        "resource": {"uri": "it-desk-agent", "attributes": {"current_location": "HQ"}},
        "principal": {"uri": "registered-principal-001", "attributes": {"department": "it"}}
    })
    print("Allowed:", result1)  # Expected output: True

    result2 = eunomia.check({
        "resource": {"uri": "hr-agent", "attributes": {"during_working_hours": "yes"}},
        "principal": {"uri": "registered-principal-002", "attributes": {"department": "hr", "role": "manager"}}
    })
    print("Allowed:", result2)  # Expected output: True

    # Denied action: Additional runtime attributes do not override the insufficient registered attributes.
    result3 = eunomia.check({
        "resource": {"uri": "it-desk-agent", "attributes": {"current_location": "Remote"}},
        "principal": {"uri": "registered-principal-003", "attributes": {"department": "sales"}}
    })
    print("Allowed:", result3)  # Expected output: False
    ```

=== "Curl"
    ```bash
    # Option 3: Using identifiers and additional runtime attributes.
    # Allowed action
    curl -X POST 'http://localhost:8000/check' \
        -H "Content-Type: application/json" \
        -d '{"resource": {"uri": "it-desk-agent", "attributes": {"current_location": "HQ"}}, "principal": {"uri": "registered-principal-001", "attributes": {"department": "it"}}}'

    curl -X POST 'http://localhost:8000/check' \
        -H "Content-Type: application/json" \
        -d '{"resource": {"uri": "hr-agent", "attributes": {"during_working_hours": "yes"}}, "principal": {"uri": "registered-principal-002", "attributes": {"department": "hr", "role": "manager"}}}'

    # Denied action
    curl -X POST 'http://localhost:8000/check' \
        -H "Content-Type: application/json" \
        -d '{"resource": {"uri": "it-desk-agent", "attributes": {"current_location": "Remote"}}, "principal": {"uri": "registered-principal-003", "attributes": {"department": "sales"}}}'
    ```

=== "Output"
    ```bash
    true
    true
    false
    ```
