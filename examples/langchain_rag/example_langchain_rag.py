from eunomia_core import schemas
from eunomia_sdk_langchain import EunomiaLoader
from eunomia_sdk_langchain.retriever import EunomiaRetriever
from eunomia_sdk_python import EunomiaClient
from langchain_community.document_loaders import HuggingFaceDatasetLoader
from langchain_community.retrievers import BM25Retriever

client = EunomiaClient()

## LOAD RESOURCES
dataset_name = "Dev523/Crime-Reports-Dataset"
page_content_column = "crimeaditionalinfo"
loader = HuggingFaceDatasetLoader(dataset_name, page_content_column)
eunomia_loader = EunomiaLoader(loader)
docs = eunomia_loader.load()

## DEFINE PRINCIPALS
analyst_financial_fraud = client.register_entity(
    type=schemas.EntityType.principal,
    attributes={"role": "Analyst - Financial Fraud", "department": "Financial Fraud"},
)

analyst_media_fraud = client.register_entity(
    type=schemas.EntityType.principal,
    attributes={
        "role": "Analyst - Media Related Fraud",
        "department": "Media Related Crime",
    },
)

director = client.register_entity(
    type=schemas.EntityType.principal,
    attributes={"role": "Director", "department": "Central"},
)


## DEFINE RETRIEVER
bm25_retriever = BM25Retriever.from_documents(docs)

analyst_financial_fraud_retriever = EunomiaRetriever(
    retriever=bm25_retriever,
    principal=schemas.PrincipalAccess(uri=analyst_financial_fraud.uri),
)

analyst_media_fraud_retriever = EunomiaRetriever(
    retriever=bm25_retriever,
    principal=schemas.PrincipalAccess(uri=analyst_media_fraud.uri),
)

director_retriever = EunomiaRetriever(
    retriever=bm25_retriever,
    principal=schemas.PrincipalAccess(uri=director.uri),
)


## RETRIEVE INFO WITH PERMISSIONS
print(analyst_financial_fraud_retriever.invoke("unauthorized transaction"))
print(analyst_media_fraud_retriever.invoke("facebook group"))
print(analyst_media_fraud_retriever.invoke("robbery"))
