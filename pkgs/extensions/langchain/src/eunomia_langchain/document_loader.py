import asyncio
from typing import AsyncIterator, Iterator, List

from eunomia_core import enums
from eunomia_sdk import EunomiaClient
from langchain.schema import Document
from langchain_core.document_loaders.base import BaseLoader


class EunomiaLoader:
    """
    A wrapper around LangChain loaders that sends documents to the Eunomia server.

    This class wraps any LangChain document loader and intercepts the document loading
    process to send their metadata as attributes to the Eunomia server. The Eunomia server
    assigns an identifier to each document, which can be used for checking access permissions
    by retrieving the associated document attributes at runtime.

    Parameters
    ----------
    loader : BaseLoader
        The LangChain loader to wrap.
    endpoint : str, optional
        The base URL endpoint of the Eunomia server.
    api_key : str, optional
        The API key to use for the Eunomia server, only required when the server is hosted on cloud.

    Notes
    -----
    The user can add additional metadata to the documents to be sent to the
    Eunomia server with respect to the ones obtained from the loader.
    """

    def __init__(
        self,
        loader: BaseLoader,
        endpoint: str | None = None,
        api_key: str | None = None,
    ):
        self._loader = loader
        self._client = EunomiaClient(endpoint=endpoint, api_key=api_key)

    def _process_document_sync(
        self, doc: Document, additional_metadata: dict = {}
    ) -> Document:
        if not hasattr(doc, "metadata") or doc.metadata is None:
            doc.metadata = {}
        doc.metadata.update(additional_metadata)

        response_data = self._client.register_entity(
            type=enums.EntityType.resource, attributes=doc.metadata
        )
        doc.metadata["eunomia_uri"] = response_data.uri
        return doc

    async def _process_document_async(
        self, doc: Document, additional_metadata: dict = {}
    ) -> Document:
        if not hasattr(doc, "metadata") or doc.metadata is None:
            doc.metadata = {}
        doc.metadata.update(additional_metadata)

        loop = asyncio.get_running_loop()
        response_data = await loop.run_in_executor(
            None,
            lambda: self._client.register_entity(
                type=enums.EntityType.resource, attributes=doc.metadata
            ),
        )
        doc.metadata["eunomia_uri"] = response_data.uri
        return doc

    async def alazy_load(
        self, additional_metadata: dict = {}
    ) -> AsyncIterator[Document]:
        """Load documents lazily and asynchronously, registering them with the Eunomia server.

        Parameters
        ----------
        additional_metadata : dict, optional
            Additional metadata to be sent to the Eunomia server.

        Yields
        ------
        Document
            Documents with Eunomia identifiers added to their metadata as 'eunomia_uri',
            yielded one by one.

        Examples
        --------
        >>> import asyncio
        >>> from langchain_community.document_loaders.csv_loader import CSVLoader
        >>>
        >>> async def process_docs():
        ...     loader = CSVLoader("data.csv")
        ...     wrapped_loader = EunomiaLoader(loader)
        ...     async for doc in wrapped_loader.alazy_load(additional_metadata={"group": "financials"}):
        ...         await process_document(doc)
        >>>
        >>> asyncio.run(process_docs())
        """
        async for doc in self._loader.alazy_load():
            processed_doc = await self._process_document_async(doc, additional_metadata)
            yield processed_doc

    async def aload(self, additional_metadata: dict = {}) -> List[Document]:
        """Load documents asynchronously and register them with the Eunomia server.

        Parameters
        ----------
        additional_metadata : dict, optional
            Additional metadata to be sent to the Eunomia server.

        Returns
        -------
        List[Document]
            The list of loaded documents with Eunomia identifiers added to their metadata
            as 'eunomia_uri'.

        Examples
        --------
        >>> import asyncio
        >>> from langchain_community.document_loaders.csv_loader import CSVLoader
        >>> loader = CSVLoader("data.csv")
        >>> wrapped_loader = EunomiaLoader(loader)
        >>> docs = asyncio.run(wrapped_loader.aload(additional_metadata={"group": "financials"}))
        """
        documents = await self._loader.aload()
        processed_docs = [
            await self._process_document_async(doc, additional_metadata)
            for doc in documents
        ]
        return processed_docs

    def lazy_load(self, additional_metadata: dict = {}) -> Iterator[Document]:
        """Load documents lazily and synchronously, registering them with the Eunomia server.

        Parameters
        ----------
        additional_metadata : dict, optional
            Additional metadata to be sent to the Eunomia server.

        Yields
        ------
        Document
            Documents with Eunomia identifiers added to their metadata as 'eunomia_uri',
            yielded one by one.

        Examples
        --------
        >>> from langchain_community.document_loaders.csv_loader import CSVLoader
        >>> loader = CSVLoader("data.csv")
        >>> wrapped_loader = EunomiaLoader(loader)
        >>> for doc in wrapped_loader.lazy_load(additional_metadata={"group": "financials"}):
        ...     process_document(doc)
        """
        for doc in self._loader.lazy_load():
            processed_doc = self._process_document_sync(doc, additional_metadata)
            yield processed_doc

    def load(self, additional_metadata: dict = {}) -> List[Document]:
        """Load documents synchronously and register them with the Eunomia server.

        Parameters
        ----------
        additional_metadata : dict, optional
            Additional metadata to be sent to the Eunomia server.

        Returns
        -------
        List[Document]
            The list of loaded documents with Eunomia identifiers added to their metadata
            as 'eunomia_uri'.

        Examples
        --------
        >>> from langchain_community.document_loaders.csv_loader import CSVLoader
        >>> loader = CSVLoader("data.csv")
        >>> wrapped_loader = EunomiaLoader(loader)
        >>> docs = wrapped_loader.load(additional_metadata={"group": "financials"})
        """
        documents = self._loader.load()
        processed_docs = [
            self._process_document_sync(doc, additional_metadata) for doc in documents
        ]
        return processed_docs

    def __getattr__(self, name):
        # Delegate any attribute or method lookup to the underlying loader
        # if not explicitly defined in this wrapper.
        return getattr(self._loader, name)
