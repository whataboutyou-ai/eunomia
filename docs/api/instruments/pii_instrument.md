`PiiInstrument` is an instrument that identifies and edits PII (Personally Identifiable Information) entities in a text using [Presidio][presidio-github].

## Configuration

| Argument    | Type        | Description |
| ----------- | ----------- | ----------- |
| `entities`  | `list[str]` | List of PII entity types to identify and edit. Supported entities include:<br>- `PERSON`<br>- `EMAIL_ADDRESS`<br>- `PHONE_NUMBER`<br>- `CREDIT_CARD`<br>- `IP_ADDRESS`<br>- [more][presidio-entities] |
| `edit_mode` | `str`       | The editing strategy to apply to identified PII. Options include:<br>- `"redact"`: Remove PII completely<br>- `"replace"`: Replace PII with a placeholder string<br>- `"hash"`: Replace PII with a hash value<br>- `"mask"`: Replace characters with * while preserving length |
| `language`  | `str`       | Language of the text to analyze. Defaults to `"en"` (English) |

## Usage Example
```py title="examples/basic_pii.py"
--8<-- "examples/basic_pii.py"
```

[presidio-github]: https://github.com/microsoft/presidio
[presidio-entities]: https://microsoft.github.io/presidio/supported_entities/
