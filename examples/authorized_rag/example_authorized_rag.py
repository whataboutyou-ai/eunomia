from eunomia_core import schemas
from eunomia_sdk_langchain import EunomiaLoader
from eunomia_sdk_langchain.retriever import EunomiaRetriever
from eunomia_sdk_python import EunomiaClient
from langchain_community.document_loaders import HuggingFaceDatasetLoader
from langchain_community.retrievers import BM25Retriever

client = EunomiaClient()

# Load dataset from HuggingFace
dataset_name = "Dev523/Crime-Reports-Dataset"
page_content_column = "crimeaditionalinfo"
loader = HuggingFaceDatasetLoader(dataset_name, page_content_column)
eunomia_loader = EunomiaLoader(loader)
docs = eunomia_loader.load()

# Register different principals with varying access levels
analyst_financial_fraud = client.register_entity(
    type=schemas.EntityType.principal,
    attributes={"role": "Analyst", "department": "Financial Fraud"},
)

analyst_media_fraud = client.register_entity(
    type=schemas.EntityType.principal,
    attributes={"role": "Analyst", "department": "Media Related Crime"},
)

director = client.register_entity(
    type=schemas.EntityType.principal,
    attributes={"role": "Director", "department": "Central"},
)

# Create base retriever
bm25_retriever = BM25Retriever.from_documents(docs)

# Create role-specific retrievers with different permissions
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

# Test retrieval with different user roles
print(analyst_financial_fraud_retriever.invoke("Unauthorized transaction"))
print(analyst_media_fraud_retriever.invoke("Facebook group"))
print(director_retriever.invoke("Robbery"))
