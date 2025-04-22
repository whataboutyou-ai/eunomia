The **`POST /check-access`** endpoint verifies whether a principal is allowed to access a resource based on their attributes. The API evaluates the access rules using a combination of registered entity attributes and/or attributes provided at runtime. The endpoint returns a boolean value (`true` for allowed access, `false` for denied access).

You have three options when calling this API:

1. **Using Identifiers Only:**  
   Supply the registered identifiers of the principal and resource. The server will retrieve their attributes from the database.

2. **Using New Entities (Attributes Only):**  
   Do not provide registered identifiers. Instead, supply the attributes directly in the request. In this case, no lookup is performed; only the runtime attributes are used.

3. **Using Identifiers and Attributes:**  
   Provide both the registered identifiers and additional attributes. The server will merge the registered attributes with those given at runtime before performing the access check.

---

## Option 1: Using Identifiers Only

In this option, you provide only the **`uri`** for both the principal and resource. The server will fetch the corresponding attributes from the database.

=== "Python"
    ```python
    from eunomia_sdk_python import EunomiaClient

    eunomia = EunomiaClient()

    # Option 1: Using identifiers only.
    # Assume that the entities are already registered in the system.
    # Allowed access (the registered principal's attributes satisfy the policy)
    result1 = eunomia.check_access({
        "resource": {"uri": "it-desk-agent"},
        "principal": {"uri": "registered-principal-001"}
    })
    print("Access allowed:", result1)  # Expected output: True

    # Denied access (the registered principal's attributes do not meet the policy)
    result2 = eunomia.check_access({
        "resource": {"uri": "hr-agent"},
        "principal": {"uri": "registered-principal-003"}
    })
    print("Access allowed:", result2)  # Expected output: False
    ```

=== "Curl"
    ```bash
    # Option 1: Using identifiers only.
    # Allowed access
    curl -X POST 'http://localhost:8000/check-access' \
         -H "Content-Type: application/json" \
         -d '{"resource": {"uri": "it-desk-agent"}, "principal": {"uri": "registered-principal-001"}}'

    # Denied access
    curl -X POST 'http://localhost:8000/check-access' \
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

In this option, you do not provide registered identifiers for the entities. Instead, you supply the attributes directly in the request. The server uses these runtime attributes exclusively for the access check.

=== "Python"
    ```python
    # Option 2: Using new entities (attributes provided at runtime).
    # Allowed access
    result1 = eunomia.check_access({
        "resource": {"uri": "it-desk-agent"},
        "principal": {"attributes": {"department": "it"}}
    })
    print("Access allowed:", result1)  # Expected output: True

    result2 = eunomia.check_access({
        "resource": {"uri": "hr-agent"},
        "principal": {"attributes": {"department": "hr", "role": "manager"}}
    })
    print("Access allowed:", result2)  # Expected output: True

    # Denied access
    result3 = eunomia.check_access({
        "resource": {"uri": "it-desk-agent"},
        "principal": {"attributes": {"department": "sales"}}
    })
    print("Access allowed:", result3)  # Expected output: False

    result4 = eunomia.check_access({
        "resource": {"uri": "hr-agent"},
        "principal": {"attributes": {"department": "hr", "role": "analyst"}}
    })
    print("Access allowed:", result4)  # Expected output: False
    ```

=== "Curl"
    ```bash
    # Option 2: Using new entities (attributes provided at runtime).
    # Allowed access
    curl -X POST 'http://localhost:8000/check-access' \
         -H "Content-Type: application/json" \
         -d '{"resource": {"uri": "it-desk-agent"}, "principal": {"attributes": {"department": "it"}}}'

    curl -X POST 'http://localhost:8000/check-access' \
         -H "Content-Type: application/json" \
         -d '{"resource": {"uri": "hr-agent"}, "principal": {"attributes": {"department": "hr", "role": "manager"}}}'

    # Denied access
    curl -X POST 'http://localhost:8000/check-access' \
         -H "Content-Type: application/json" \
         -d '{"resource": {"uri": "it-desk-agent"}, "principal": {"attributes": {"department": "sales"}}}'

    curl -X POST 'http://localhost:8000/check-access' \
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

In this option, you provide both the registered **`uri`** and additional attributes in the request. The server merges the registered attributes with the runtime attributes, and the resulting set is used for the access check.

=== "Python"
    ```python
    # Option 3: Using both identifiers and additional runtime attributes.
    # Allowed access: The registered principal is enriched with runtime attributes.
    result1 = eunomia.check_access({
        "resource": {"uri": "it-desk-agent", "attributes": {"current_location": "HQ"}},
        "principal": {"uri": "registered-principal-001", "attributes": {"department": "it"}}
    })
    print("Access allowed:", result1)  # Expected output: True

    result2 = eunomia.check_access({
        "resource": {"uri": "hr-agent", "attributes": {"during_working_hours": "yes"}},
        "principal": {"uri": "registered-principal-002", "attributes": {"department": "hr", "role": "manager"}}
    })
    print("Access allowed:", result2)  # Expected output: True

    # Denied access: Additional runtime attributes do not override the insufficient registered attributes.
    result3 = eunomia.check_access({
        "resource": {"uri": "it-desk-agent", "attributes": {"current_location": "Remote"}},
        "principal": {"uri": "registered-principal-003", "attributes": {"department": "sales"}}
    })
    print("Access allowed:", result3)  # Expected output: False
    ```

=== "Curl"
    ```bash
    # Option 3: Using identifiers and additional runtime attributes.
    # Allowed access
    curl -X POST 'http://localhost:8000/check-access' \
        -H "Content-Type: application/json" \
        -d '{"resource": {"uri": "it-desk-agent", "attributes": {"current_location": "HQ"}}, "principal": {"uri": "registered-principal-001", "attributes": {"department": "it"}}}'

    curl -X POST 'http://localhost:8000/check-access' \
        -H "Content-Type: application/json" \
        -d '{"resource": {"uri": "hr-agent", "attributes": {"during_working_hours": "yes"}}, "principal": {"uri": "registered-principal-002", "attributes": {"department": "hr", "role": "manager"}}}'

    # Denied access
    curl -X POST 'http://localhost:8000/check-access' \
        -H "Content-Type: application/json" \
        -d '{"resource": {"uri": "it-desk-agent", "attributes": {"current_location": "Remote"}}, "principal": {"uri": "registered-principal-003", "attributes": {"department": "sales"}}}'
    ```

=== "Output"
    ```bash
    true
    true
    false
    ```