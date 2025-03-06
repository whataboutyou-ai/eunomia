import uuid
import requests
from langchain_core.document_loaders.base import BaseLoader
import asyncio
from typing import AsyncIterator, Iterator, List
from langchain.schema import Document

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
    def __init__(self, loader: BaseLoader, eunomia_server_base_url: str):
        """
        :param loader: The original document loader instance.
        :param api_url: The API endpoint to send document metadata.
        """
        self.loader = loader
        self.eunomia_server_api_url = f"{eunomia_server_base_url}/register_resource/"

    def process_document(self, doc: Document) -> Document:
        unique_id = str(uuid.uuid4())
        if not hasattr(doc, "metadata") or doc.metadata is None:
            doc.metadata = {}
        doc.metadata["eunomia_id"] = unique_id
        return doc

    def send_api_sync(self, doc: Document):
        payload = {
            "eunomia_id": doc.metadata["eunomia_id"],
            "metadata": doc.metadata,
            "content": doc.page_content,
        }
        response = requests.post(self.eunomia_server_api_url, json=payload)
        print(f"Document {doc.metadata['eunomia_id']} processed, status code: {response.status_code}")

    async def send_api_async(self, doc: Document):
        loop = asyncio.get_running_loop()
        payload = {
            "eunomia_id": doc.metadata["eunomia_id"],
            "metadata": doc.metadata,
            "content": doc.page_content,
        }
        await loop.run_in_executor(None, lambda: requests.post(self.eunomia_server_api_url, json=payload))

    async def alazy_load(self) -> AsyncIterator[Document]:
        async for doc in self.loader.alazy_load():
            processed_doc = self.process_document(doc)
            await self.send_api_async(processed_doc)
            yield processed_doc

    async def aload(self) -> List[Document]:
        documents = await self.loader.aload()
        processed_docs = [self.process_document(doc) for doc in documents]
        await asyncio.gather(*[self.send_api_async(doc) for doc in processed_docs])
        return processed_docs

    def lazy_load(self) -> Iterator[Document]:
        for doc in self.loader.lazy_load():
            processed_doc = self.process_document(doc)
            self.send_api_sync(processed_doc)
            yield processed_doc

    def load(self) -> List[Document]:
        documents = self.loader.load()
        processed_docs = [self.process_document(doc) for doc in documents]
        for doc in processed_docs:
            self.send_api_sync(doc)
        return processed_docs

    def __getattr__(self, name):
        """
        Delegate any attribute or method lookup to the underlying loader if not
        explicitly defined in this wrapper.
        """
        return getattr(self.loader, name)


