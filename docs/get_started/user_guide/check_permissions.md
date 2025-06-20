The **`POST /check`** endpoint verifies whether a principal is allowed to perform an action on a resource based on their attributes. The API evaluates the authorization policies using a combination of fetched entity attributes and/or attributes provided at runtime. The endpoint returns a response object with a boolean value (`true` for allowed action, `false` for denied action).

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
    from eunomia_sdk import EunomiaClient

    eunomia = EunomiaClient()

    # Option 1: Using identifiers only.
    # Assume that the entities are already registered in the system.
    # Allowed action (the registered principal's attributes satisfy the policy)
    result1 = eunomia.check(
        principal_uri="registered-principal-001",
        resource_uri="it-desk-agent"
    )
    print("Allowed:", result1.allowed)  # Expected output: True

    # Denied action (the registered principal's attributes do not meet the policy)
    result2 = eunomia.check(
        principal_uri="registered-principal-003",
        resource_uri="hr-agent"
    )
    print("Allowed:", result2.allowed)  # Expected output: False
    ```

=== "Curl"
    ```bash
    # Option 1: Using identifiers only.
    # Allowed action
    curl -X POST 'http://localhost:8000/check' \
         -H "Content-Type: application/json" \
         -d '{"principal_uri": "registered-principal-001", "resource_uri": "it-desk-agent"}'

    # Denied action
    curl -X POST 'http://localhost:8000/check' \
         -H "Content-Type: application/json" \
         -d '{"principal_uri": "registered-principal-003", "resource_uri": "hr-agent"}'
    ```

=== "Output"
    ```bash
    {"allowed": true, "reason": "..."}
    {"allowed": false, "reason": "..."}
    ```

---

## Option 2: Using New Entities (Attributes Only)

In this option, you do not provide registered identifiers for the entities. Instead, you supply the attributes directly in the request. The server uses these runtime attributes exclusively for the authorization check.

=== "Python"
    ```python
    # Option 2: Using new entities (attributes provided at runtime).
    # Allowed action
    result1 = eunomia.check(
        resource_uri="it-desk-agent",
        principal_attributes={"department": "it"}
    )
    print("Allowed:", result1.allowed)  # Expected output: True

    result2 = eunomia.check(
        resource_uri="hr-agent",
        principal_attributes={"department": "hr", "role": "manager"}
    )
    print("Allowed:", result2.allowed)  # Expected output: True

    # Denied action
    result3 = eunomia.check(
        resource_uri="it-desk-agent",
        principal_attributes={"department": "sales"}
    )
    print("Allowed:", result3.allowed)  # Expected output: False

    result4 = eunomia.check(
        resource_uri="hr-agent",
        principal_attributes={"department": "hr", "role": "analyst"}
    )
    print("Allowed:", result4.allowed)  # Expected output: False
    ```

=== "Curl"
    ```bash
    # Option 2: Using new entities (attributes provided at runtime).
    # Allowed action
    curl -X POST 'http://localhost:8000/check' \
         -H "Content-Type: application/json" \
         -d '{"resource_uri": "it-desk-agent", "principal_attributes": {"department": "it"}}'

    curl -X POST 'http://localhost:8000/check' \
         -H "Content-Type: application/json" \
         -d '{"resource_uri": "hr-agent", "principal_attributes": {"department": "hr", "role": "manager"}}'

    # Denied action
    curl -X POST 'http://localhost:8000/check' \
         -H "Content-Type: application/json" \
         -d '{"resource_uri": "it-desk-agent", "principal_attributes": {"department": "sales"}}'

    curl -X POST 'http://localhost:8000/check' \
         -H "Content-Type: application/json" \
         -d '{"resource_uri": "hr-agent", "principal_attributes": {"department": "hr", "role": "analyst"}}'
    ```

=== "Output"
    ```bash
    {"allowed": true, "reason": "..."}
    {"allowed": true, "reason": "..."}
    {"allowed": false, "reason": "..."}
    {"allowed": false, "reason": "..."}
    ```

---

## Option 3: Using Identifiers and Attributes

In this option, you provide both the registered **`uri`** and additional attributes in the request. The server merges the registered attributes with the runtime attributes, and the resulting set is used for the authorization check.

=== "Python"
    ```python
    # Option 3: Using both identifiers and additional runtime attributes.
    # Allowed action: The registered principal is enriched with runtime attributes.
    result1 = eunomia.check(
        principal_uri="registered-principal-001",
        principal_attributes={"department": "it"}
        resource_uri="it-desk-agent",
        resource_attributes={"current_location": "HQ"},
    )
    print("Allowed:", result1.allowed)  # Expected output: True

    result2 = eunomia.check(
        principal_uri="registered-principal-002",
        principal_attributes={"department": "hr", "role": "manager"}
        resource_uri="hr-agent",
        resource_attributes={"during_working_hours": "yes"},
    )
    print("Allowed:", result2.allowed)  # Expected output: True

    # Denied action: Additional runtime attributes do not override the insufficient registered attributes.
    result3 = eunomia.check(
        resource_uri="it-desk-agent",
        resource_attributes={"current_location": "Remote"},
        principal_uri="registered-principal-003",
        principal_attributes={"department": "sales"}
    )
    print("Allowed:", result3.allowed)  # Expected output: False
    ```

=== "Curl"
    ```bash
    # Option 3: Using identifiers and additional runtime attributes.
    # Allowed action
    curl -X POST 'http://localhost:8000/check' \
        -H "Content-Type: application/json" \
        -d '{"principal_uri": "registered-principal-001", "principal_attributes": {"department": "it"}, "resource_uri": "it-desk-agent", "resource_attributes": {"current_location": "HQ"}}'

    curl -X POST 'http://localhost:8000/check' \
        -H "Content-Type: application/json" \
        -d '{"principal_uri": "registered-principal-002", "principal_attributes": {"department": "hr", "role": "manager"}, "resource_uri": "hr-agent", "resource_attributes": {"during_working_hours": "yes"}}'

    # Denied action
    curl -X POST 'http://localhost:8000/check' \
        -H "Content-Type: application/json" \
        -d '{"principal_uri": "registered-principal-003", "principal_attributes": {"department": "sales"}, "resource_uri": "it-desk-agent", "resource_attributes": {"current_location": "Remote"}}'
    ```

=== "Output"
    ```bash
    {"allowed": true, "reason": "..."}
    {"allowed": true, "reason": "..."}
    {"allowed": false, "reason": "..."}
    ```
