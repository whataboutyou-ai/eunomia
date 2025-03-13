# Eunomia SDK for LangChain

This package allows to streamline [LangChain's loaders][langchain-loaders-docs] resources and their metadata to the [Eunomia][eunomia-github] server for an easier policy configuration process.

## Installation

Install the `eunomia-sdk-langchain` package via pip:

```bash
pip install eunomia-sdk-langchain
```

## Usage

The `EunomiaLoader` class is a wrapper around any loader class from LangChain.

Assume you want to use the `CSVLoader`, you can do the following:

```python
from eunomia_sdk_langchain import EunomiaLoader
from langchain_community.document_loaders.csv_loader import CSVLoader

loader = CSVLoader(...)
wrapped_loader = EunomiaLoader(loader, server_url="http://localhost:8000")
```

You can then call any of the load methods:

```python
# Synchronous loading
docs = wrapped_loader.load()

# Synchronous lazy loading
docs = []
for doc in wrapped_loader.lazy_load():
    docs.append(doc)

# Asynchronous loading
import asyncio

asyncio.run(wrapped_loader.aload())

# Asynchronous lazy loading
docs = []
async for doc in wrapped_loader.alazy_load():
    docs.append(doc)
```

All loaded documents will be automatically sent to the Eunomia server which will assign an identifier to each document and store their metadata. The identifiers and metadata can then be used to configure policies in the Eunomia server.

## Documentation

For detailed usage, check out the SDK's [documentation][docs].

[eunomia-github]: https://github.com/whataboutyou-ai/eunomia
[docs]: https://whataboutyou-ai.github.io/eunomia/sdks/langchain/
[langchain-loaders-docs]: https://python.langchain.com/docs/concepts/document_loaders/
