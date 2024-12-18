`RbacInstrument` is an instrument that implements a role-based access control (RBAC) on input documents. RBAC allows to specify different instruments for each role, creating an orchestra for each role.

## Configuration

| Argument      | Type               | Description |
| ------------- | ------------------ | ----------- |
| `role`        | `str`              | The role to apply the RBAC to |
| `instruments` | `list[Instrument]` | The instruments to apply to the role |

## Usage Example
```py title="examples/role_based_pii.py"
--8<-- "examples/role_based_pii.py"
```
