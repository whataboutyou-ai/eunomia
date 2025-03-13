import asyncio
from typing import AsyncIterator, Iterator, List

from eunomia_sdk_python import EunomiaClient
from langchain.schema import Document
from langchain_core.document_loaders.base import BaseLoader


class EunomiaLoader:
    """A wrapper around LangChain loaders that sends documents to the Eunomia server.

    This class wraps any LangChain BaseLoader and intercepts the document loading
    process to send metadata to the Eunomia server. The Eunomia server assigns an
    identifier to each document, which can be used for policy configuration.

    Parameters
    ----------
    loader : BaseLoader
        The LangChain loader to wrap.
    server_host : str, optional
        The hostname of the Eunomia server.
    api_key : str, optional
        The API key to use for the Eunomia server, only required when the server is hosted on cloud.
    send_content : bool, default=False
        Whether to send the content of the documents to the Eunomia server.

    Methods
    -------
    load(eunomia_group=None) -> List[Document]
        Load the documents synchronously and register them with the Eunomia server.
    lazy_load(eunomia_group=None) -> Iterator[Document]
        Load the documents lazily synchronously and register them with the Eunomia server.
    aload(eunomia_group=None) -> List[Document]
        Load the documents asynchronously and register them with the Eunomia server.
    alazy_load(eunomia_group=None) -> AsyncIterator[Document]
        Load the documents lazily asynchronously and register them with the Eunomia server.

    Notes
    -----
    All loaded documents will be automatically sent to the Eunomia server which will
    assign an identifier to each document and store their metadata. The identifiers
    and metadata can then be used to configure policies in the Eunomia server.
    """

    def __init__(
        self,
        loader: BaseLoader,
        server_host: str | None = None,
        api_key: str | None = None,
        send_content: bool = False,
    ):
        self._loader = loader
        self._send_content = send_content
        self._client = EunomiaClient(server_host=server_host, api_key=api_key)

    def _get_request_payload(self, doc: Document):
        request_payload = {
            "metadata": doc.metadata,
            "content": doc.page_content if self._send_content is True else None,
        }
        return request_payload

    def _process_document_sync(
        self, doc: Document, eunomia_group: str | None = None
    ) -> Document:
        if not hasattr(doc, "metadata") or doc.metadata is None:
            doc.metadata = {}
        doc.metadata["eunomia_group"] = eunomia_group
        payload = self._get_request_payload(doc)
        response_data = self._client.register_resource(payload)
        doc.metadata["eunomia_id"] = response_data.get("eunomia_id")
        return doc

    async def _process_document_async(
        self, doc: Document, eunomia_group: str | None = None
    ) -> Document:
        if not hasattr(doc, "metadata") or doc.metadata is None:
            doc.metadata = {}
        doc.metadata["eunomia_group"] = eunomia_group
        payload = self._get_request_payload(doc)
        loop = asyncio.get_running_loop()
        payload = self._get_request_payload(doc)
        response_data = await loop.run_in_executor(
            None, lambda: self._client.register_resource(payload)
        )
        doc.metadata["eunomia_id"] = response_data.get("eunomia_id")
        return doc

    async def alazy_load(
        self, eunomia_group: str | None = None
    ) -> AsyncIterator[Document]:
        """Load documents lazily and asynchronously, registering them with the Eunomia server.

        Parameters
        ----------
        eunomia_group : str, optional
            An optional group identifier to assign to all documents. This will be
            stored in the document metadata as 'eunomia_group'.

        Yields
        ------
        Document
            Documents with Eunomia identifiers added to their metadata, yielded one by one.

        Examples
        --------
        >>> import asyncio
        >>> from langchain_community.document_loaders.csv_loader import CSVLoader
        >>>
        >>> async def process_docs():
        ...     loader = CSVLoader("data.csv")
        ...     wrapped_loader = EunomiaLoader(loader)
        ...     async for doc in wrapped_loader.alazy_load(eunomia_group="financial_data"):
        ...         await process_document(doc)
        >>>
        >>> asyncio.run(process_docs())
        """
        async for doc in self._loader.alazy_load():
            processed_doc = await self._process_document_async(doc, eunomia_group)
            yield processed_doc

    async def aload(self, eunomia_group: str | None = None) -> List[Document]:
        """Load documents asynchronously and register them with the Eunomia server.

        Parameters
        ----------
        eunomia_group : str, optional
            An optional group identifier to assign to all documents. This will be
            stored in the document metadata as 'eunomia_group'.

        Returns
        -------
        List[Document]
            The list of loaded documents with Eunomia identifiers added to their metadata.

        Examples
        --------
        >>> import asyncio
        >>> from langchain_community.document_loaders.csv_loader import CSVLoader
        >>> loader = CSVLoader("data.csv")
        >>> wrapped_loader = EunomiaLoader(loader)
        >>> docs = asyncio.run(wrapped_loader.aload(eunomia_group="financial_data"))
        """
        documents = await self._loader.aload()
        processed_docs = [
            await self._process_document_async(doc, eunomia_group) for doc in documents
        ]
        return processed_docs

    def lazy_load(self, eunomia_group: str | None = None) -> Iterator[Document]:
        """Load documents lazily and synchronously, registering them with the Eunomia server.

        Parameters
        ----------
        eunomia_group : str, optional
            An optional group identifier to assign to all documents. This will be
            stored in the document metadata as 'eunomia_group'.

        Yields
        ------
        Document
            Documents with Eunomia identifiers added to their metadata, yielded one by one.

        Examples
        --------
        >>> from langchain_community.document_loaders.csv_loader import CSVLoader
        >>> loader = CSVLoader("data.csv")
        >>> wrapped_loader = EunomiaLoader(loader)
        >>> for doc in wrapped_loader.lazy_load(eunomia_group="financial_data"):
        ...     process_document(doc)
        """
        for doc in self._loader.lazy_load():
            processed_doc = self._process_document_sync(doc, eunomia_group)
            yield processed_doc

    def load(self, eunomia_group: str | None = None) -> List[Document]:
        """Load documents synchronously and register them with the Eunomia server.

        Parameters
        ----------
        eunomia_group : str, optional
            An optional group identifier to assign to all documents. This will be
            stored in the document metadata as 'eunomia_group'.

        Returns
        -------
        List[Document]
            The list of loaded documents with Eunomia identifiers added to their metadata.

        Examples
        --------
        >>> from langchain_community.document_loaders.csv_loader import CSVLoader
        >>> loader = CSVLoader("data.csv")
        >>> wrapped_loader = EunomiaLoader(loader)
        >>> docs = wrapped_loader.load(eunomia_group="financial_data")
        """
        documents = self._loader.load()
        processed_docs = [
            self._process_document_sync(doc, eunomia_group) for doc in documents
        ]
        return processed_docs

    def __getattr__(self, name):
        # Delegate any attribute or method lookup to the underlying loader
        # if not explicitly defined in this wrapper.
        return getattr(self._loader, name)
