[LangChain][langchain-website] is a popular framework for building applications with LLMs.

Eunomia provides two LangChain integrations that allow to:

- register documents loaded by any [LangChain's loader][langchain-loaders-docs] to the Eunomia server
- enforce authorization policies on documents retrieved by any [LangChain retriever][langchain-retriever-docs]

These integrations help the configuration and enforcement of authorization policies on LLM applications that leverage LangChain.

## Installation

Install the `eunomia-sdk-langchain` package via pip:

```bash
pip install eunomia-sdk-langchain
```

## SDK Docs

::: eunomia_sdk_langchain.document_loader.EunomiaLoader

::: eunomia_sdk_langchain.retriever.EunomiaRetriever

[langchain-website]: https://www.langchain.com/
[langchain-loaders-docs]: https://python.langchain.com/docs/concepts/document_loaders/
[langchain-retriever-docs]: https://python.langchain.com/docs/concepts/retrievers/
