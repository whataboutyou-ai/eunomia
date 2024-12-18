`Orchestra` is a class that orchestrates the execution of multiple instruments on an input text.

## Configuration

| Argument      | Type               | Description                        |
| ------------- | ------------------ | ---------------------------------- |
| `instruments` | `list[Instrument]` | The instruments to run on the text |

## Methods

### `add_instrument(instrument: Instrument) -> None`
Adds an instrument to the orchestra.

### `run(text: str, **kwargs) -> str`
Run the orchestra in sequence on an input text.
