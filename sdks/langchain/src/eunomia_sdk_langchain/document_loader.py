import asyncio
from typing import AsyncIterator, Iterator, List

from eunomia_sdk_python import EunomiaClient
from langchain.schema import Document
from langchain_core.document_loaders.base import BaseLoader

# Example usage:
# Assuming `MyDocumentLoader` is a loader class from LangChain that implements
# these four methods and has already been instantiated with necessary parameters:
#
#   from my_loaders import MyDocumentLoader
#
#   my_loader = MyDocumentLoader(param1="value1", param2="value2")
#   server_url = "https://your-eunomia-server-endpoint.com/process"
#   wrapped_loader = EunomiaLoader(my_loader, server_url)
#
# You can then call any of the overridden methods:
#
#   docs_sync = wrapped_loader.load()
#   for doc in wrapped_loader.lazy_load():
#       pass
#
#   # For asynchronous methods, run them in an event loop:
#   import asyncio
#   asyncio.run(wrapped_loader.aload())


class EunomiaLoader:
    def __init__(
        self,
        loader: BaseLoader,
        eunomia_server_base_url: str,
        api_key: str | None = None,
        send_content: bool = False,
    ):
        """
        :param loader: The original document loader instance.
        :param api_url: The API endpoint to send document metadata.
        """
        self._loader = loader
        self._send_content = send_content
        self._client = EunomiaClient(
            api_key=api_key, server_host=eunomia_server_base_url
        )

    def _get_request_payload(self, doc: Document):
        request_payload = {
            "metadata": doc.metadata,
            "content": doc.page_content if self._send_content is True else None,
        }
        return request_payload

    def _process_document_sync(
        self, doc: Document, eunomia_group: str = None
    ) -> Document:
        if not hasattr(doc, "metadata") or doc.metadata is None:
            doc.metadata = {}
        doc.metadata["eunomia_group"] = eunomia_group
        payload = self._get_request_payload(doc)
        response_data = self._client.register_resource(payload)
        doc.metadata["eunomia_id"] = response_data.get("eunomia_id")
        return doc

    async def _process_document_async(
        self, doc: Document, eunomia_group: str = None
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

    async def alazy_load(self, eunomia_group: str = None) -> AsyncIterator[Document]:
        async for doc in self._loader.alazy_load():
            processed_doc = await self._process_document_async(doc, eunomia_group)
            yield processed_doc

    async def aload(self, eunomia_group: str = None) -> List[Document]:
        documents = await self._loader.aload()
        processed_docs = [
            await self._process_document_async(doc, eunomia_group) for doc in documents
        ]
        return processed_docs

    def lazy_load(self, eunomia_group: str = None) -> Iterator[Document]:
        for doc in self._loader.lazy_load():
            processed_doc = self._process_document_sync(doc, eunomia_group)
            yield processed_doc

    def load(self, eunomia_group: str = None) -> List[Document]:
        documents = self._loader.load()
        processed_docs = [
            self._process_document_sync(doc, eunomia_group) for doc in documents
        ]
        return processed_docs

    def __getattr__(self, name):
        """
        Delegate any attribute or method lookup to the underlying loader if not
        explicitly defined in this wrapper.
        """
        return getattr(self._loader, name)
