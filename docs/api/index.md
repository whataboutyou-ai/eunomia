---
title: API Documentation
---

Eunomia is a framework for data governance specifically designed for LLM-based applications.

It is designed to be modular and flexible, allowing users to tailor data governance strategies to diverse use cases while maintaining precision and efficiency.

## The Primitive Operations
There are two primitive operations in the framework, **identification** and **editing**. These operations are combined into a core component called an [`Instrument`](instruments/index.md). Each `Instrument` is a self-contained unit designed to handle specific data governance tasks.

An `Instrument` consists of:

- A specific **identification** operation: the operation that identifies certain text entities, such as PII (e.g., names, addresses, gender) or customized entities tailored to the use case, like client names, revenue figures, or user-specific data.
- A defined **editing** operation: the operation that transforms the identified entities based on the requirements. The content can be redacted (context-aware or not) or transformed into aggregated or extracted insights, such as a total sum of transactions or tool usage summaries.

To see all available instruments, please refer to [this section](instruments/index.md#available-instruments).

## Data Governance in Concert

While each `Instrument` operates independently, effective data governance often requires addressing multiple entities and tasks simultaneously. To achieve this, multiple instruments can be combined to work together, forming what we call an [`Orchestra`](orchestra.md).

The `Orchestra` coordinates the execution of multiple instruments, allowing users to tackle complex data governance challenges.
