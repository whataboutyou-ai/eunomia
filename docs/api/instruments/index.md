---
title: Instruments
---

An instrument is a class that performs a specific task on a text.

All instruments are subclasses of the abstract class `Instrument` and implement the `run` method that takes a text and returns a processed text.

Multiple instruments can be combined in an [`Orchestra`](../orchestra.md), allowing to accommodate the needs of different use cases.

## Available Instruments

| Instrument             | Description                                      | Jump to                                                 |
| ---------------------- | ------------------------------------------------ | ------------------------------------------------------- |
| `PiiInstrument`        | Identify and edit PII from text                  | [:material-arrow-right: Page](pii_instrument.md)        |
| `FinancialsInstrument` | Identify and edit financial data from text       | [:material-arrow-right: Page](financials_instrument.md) |
| `RbacInstrument`       | Apply instruments with Role-Based Access Control | [:material-arrow-right: Page](rbac_instrument.md)       |
| `IdbacInstrument`      | Apply instruments with ID-Based Access Control   | [:material-arrow-right: Page](idbac_instrument.md)      |
