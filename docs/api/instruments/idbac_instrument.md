`IdbacInstrument` is an instrument that implements an ID-based access control (IDBAC) on input documents. IDBAC allows to specify a set of instruments that will be run only on those documents that are associated to different IDs than the one of the user.

## Configuration

| Argument      | Type               | Description |
| ------------- | ------------------ | ----------- |
| `instruments` | `list[Instrument]` | The instruments to apply to the IDBAC |

## Usage Example
```py title="examples/id_based_pii.py"
--8<-- "examples/id_based_pii.py"
```
