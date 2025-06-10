# Eunomia extension for LangChain

This package provides an extension of [Eunomia][eunomia-github] for [LangChain][langchain-website], allowing you to:

- Register documents loaded by any [LangChain's loader][langchain-loaders-docs] to the Eunomia server
- Enforce authorization policies on documents retrieved by any [LangChain retriever][langchain-retriever-docs]

## Installation

Install the `eunomia-langchain` package via pip:

```bash
pip install eunomia-langchain
```

## Usage

### Document Loader

The `EunomiaLoader` class is a wrapper around any loader class from LangChain that sends documents to the Eunomia server.

```python
from eunomia_langchain import EunomiaLoader
from langchain_community.document_loaders.csv_loader import CSVLoader

# Create a document loader
loader = CSVLoader("data.csv")

# Wrap the loader with Eunomia
wrapped_loader = EunomiaLoader(loader)

# Load documents and register them with the Eunomia server
docs = wrapped_loader.load(additional_metadata={"group": "financials"})
```

All loaded documents will be automatically sent to the Eunomia server which will assign an identifier to each document and store their metadata. The identifiers and metadata can then be used to configure or reference policies in the Eunomia server.

### Document Retriever

The `EunomiaRetriever` class wraps any LangChain retriever and filters allowed documents using the Eunomia server.

```python
from eunomia_core import schemas
from eunomia_langchain import EunomiaRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

# Create a retriever with some documents
retriever = BM25Retriever.from_documents([
    Document(page_content="foo", metadata={"confidentiality": "public"}),
    Document(page_content="bar", metadata={"confidentiality": "public"}),
    Document(page_content="foo bar", metadata={"confidentiality": "private"}),
])

# Wrap the retriever with Eunomia
wrapped_retriever = EunomiaRetriever(
    retriever=retriever,
    principal=schemas.PrincipalCheck(uri="test-uri"),
)

# Only documents the principal has access to will be returned
docs = wrapped_retriever.invoke("foo")
```

## Documentation

For detailed usage, check out the SDK's [documentation][docs].

[eunomia-github]: https://github.com/whataboutyou-ai/eunomia
[docs]: https://whataboutyou-ai.github.io/eunomia/api/extensions/langchain/
[langchain-website]: https://www.langchain.com/
[langchain-loaders-docs]: https://python.langchain.com/docs/concepts/document_loaders/
[langchain-retriever-docs]: https://python.langchain.com/docs/concepts/retrievers/
