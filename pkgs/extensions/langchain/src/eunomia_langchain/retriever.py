import asyncio

from eunomia_core import schemas
from eunomia_sdk import EunomiaClient
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever


class EunomiaRetriever(BaseRetriever):
    """
    A wrapper around LangChain retrievers that filters allowed documents using the Eunomia server.

    This class wraps any LangChain retriever and intercepts the document retrieval
    process to filter allowed documents using the Eunomia server.

    Parameters
    ----------
    retriever : BaseRetriever
        The LangChain retriever to wrap.
    principal : schemas.PrincipalCheck
        The principal to use for the Eunomia server. Defined either with its identifier (uri), attributes or both.
    endpoint : str, optional
        The base URL endpoint of the Eunomia server.
    api_key : str, optional
        The API key to use for the Eunomia server, only required when the server is hosted on cloud.

    Examples
    --------
    >>> from eunomia_core import schemas
    >>> from eunomia_langchain.retriever import EunomiaRetriever
    >>> from langchain_community.retrievers import BM25Retriever
    >>> from langchain_core.documents import Document
    >>> retriever = BM25Retriever.from_documents(
    ...     [
    ...         Document(page_content="foo", metadata={"confidentiality": "public"}),
    ...         Document(page_content="bar", metadata={"confidentiality": "public"}),
    ...         Document(page_content="foo bar", metadata={"confidentiality": "private"}),
    ...     ]
    ... )
    >>> wrapped_retriever = EunomiaRetriever(
    ...     retriever=retriever,
    ...     principal=schemas.PrincipalCheck(uri="test-uri"),
    ... )
    >>> docs = wrapped_retriever.invoke("foo")
    """

    def __init__(
        self,
        retriever: BaseRetriever,
        principal: schemas.PrincipalCheck,
        endpoint: str | None = None,
        api_key: str | None = None,
    ):
        super().__init__()
        self._retriever = retriever
        self._principal = principal
        self._client = EunomiaClient(endpoint=endpoint, api_key=api_key)

    def _check_docs_access(self, docs: list[Document]) -> list[Document]:
        return [
            doc
            for doc in docs
            if self._client.check(
                resource_uri=doc.metadata.pop("eunomia_uri", None),
                resource_attributes=doc.metadata,
                principal_uri=self._principal.uri,
                principal_attributes=self._principal.attributes,
            ).allowed
        ]

    def _get_relevant_documents(self, query: str) -> list[Document]:
        docs = self._retriever.invoke(query)
        return self._check_docs_access(docs)

    async def _acheck_doc_access(
        self, doc: Document
    ) -> tuple[Document, schemas.CheckResponse]:
        return (
            doc,
            await asyncio.to_thread(
                self._client.check,
                resource_uri=doc.metadata.pop("eunomia_uri", None),
                resource_attributes=doc.metadata,
                principal_uri=self._principal.uri,
                principal_attributes=self._principal.attributes,
            ),
        )

    async def _acheck_docs_access(self, docs: list[Document]) -> list[Document]:
        results = await asyncio.gather(*[self._acheck_doc_access(doc) for doc in docs])
        return [doc for doc, response in results if response.allowed]

    async def _aget_relevant_documents(self, query: str) -> list[Document]:
        docs = await self._retriever.ainvoke(query)
        return await self._acheck_docs_access(docs)
