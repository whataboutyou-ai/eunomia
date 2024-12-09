from eunomia.instrument import Instrument


class Orchestra:
    """
    A class that orchestrates the execution of multiple instruments on an input text.
    """

    def __init__(self, instruments: list[Instrument] = []) -> None:
        self._instruments = instruments

    def add_instrument(self, instrument: Instrument) -> None:
        """Add an instrument to the orchestra."""
        self._instruments.append(instrument)

    def run(self, text: str, **kwargs) -> str:
        """Run the orchestra in sequence on an input text."""
        for instrument in self._instruments:
            text = instrument.run(text, **kwargs)
        return text
