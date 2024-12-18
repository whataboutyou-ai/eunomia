`FinancialsInstrument` is an instrument that extracts financial information from a text using a [fine-tuned BERT model][financial-ner-model].

## Configuration

| Argument    | Type        | Description |
| ----------- | ----------- | ----------- |
| `entities`  | `list[str]` | List of financial entity types to identify and edit. More information on supported entities can be found on the [model page][financial-ner-model] |
| `edit_mode` | `str`       | The editing strategy to apply to identified financial entities. Options include:<br>- `"redact"`: Remove financial entities completely<br>- `"replace"`: Replace financial entities with a placeholder string<br>- `"hash"`: Replace financial entities with a hash value<br>- `"mask"`: Replace characters with * while preserving length |

## Usage Example
```py title="examples/financial_ner.py"
--8<-- "examples/financial_ner.py"
```

[financial-ner-model]: https://huggingface.co/whataboutyou-ai/financial_bert
