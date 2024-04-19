import os

from langchain_google_community import VertexAISearchRetriever
from langchain_google_vertexai import ChatVertexAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from ..config import Config


project_id = Config.GOOGLE_CLOUD_PROJECT
search_engine_id = Config.AI_SEARCH_ENGINE_ID
model_name = Config.MODEL_NAME
data_store_id = Config.GCP_SEARCH_DATASTORE_ID

if not data_store_id:
    raise ValueError(
        "No value provided in env variable 'GCP_SEARCH_DATASTORE_ID'. "
        "A  data store is required to run this application."
    )

# Set LLM and embeddings
model = ChatVertexAI(model_name=model_name, temperature=0.0)

# Create Vertex AI retriever
retriever = VertexAISearchRetriever(
    project_id=project_id, data_store_id=data_store_id
)

# RAG prompt
template = """Answer the question based only on the following context:
{context}
Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# RAG
chain = (
    RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
    | prompt
    | model
    | StrOutputParser()
)


# Add typing for input
class Question(BaseModel):
    __root__: str


chain = chain.with_types(input_type=Question)
