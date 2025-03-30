# Authorized RAG

This example shows how to create a Retrieval-Augmented Generation (RAG) system with role-based access control, where different users can only access information relevant to their role.

The example uses [LangChain][langchain-github] for loading and retrieving documents. The loader uses [Hugging Face Datasets][huggingface-github] to load the documents from a remote dataset and [Eunomia][eunomia-github] to store their associated attributes. The retriever uses the [BM25][bm25-github] algorithm to retrieve documents from the document store and [Eunomia][eunomia-github] to enforce access control.

The example demonstrates how Eunomia streamlines the process of creating an authorized RAG system by leveraging LangChain integrations.

## Setup

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the Eunomia server using the `allow_category.rego` policy, with:

```bash
eunomia server
```

Check the [Eunomia documentation][eunomia-docs] if you need more information on how to run the server.

## Running

Run the example script:

```bash
python example_authorized_rag.py
```

The script will:

1. Load a crime reports dataset from Hugging Face, automatically streaming the attributes of the dataset into Eunomia
2. Register three different principal roles (financial fraud analyst, media fraud analyst, and director)
3. Create retrievers with different permission levels for each role
4. Demonstrate how each role retrieves different information based on their permissions

## How It Works

The example creates different retrievers with role-based access control:

- Financial fraud analysts can access financial crime information
- Media fraud analysts can access media-related crime information
- Directors have access to all crime information

By enforcing access at the retrieval level, the system ensures that sensitive information is only provided to authorized users.

[eunomia-github]: https://github.com/whataboutyou-ai/eunomia
[langchain-github]: https://github.com/langchain-ai/langchain
[huggingface-github]: https://github.com/huggingface/datasets
[bm25-github]: https://github.com/dorianbrown/rank_bm25
[eunomia-docs]: https://whataboutyou-ai.github.io/eunomia/
