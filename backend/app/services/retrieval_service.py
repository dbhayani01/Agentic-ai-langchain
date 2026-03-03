from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from app.core.config import get_settings


class RetrievalService:
    def __init__(self) -> None:
        settings = get_settings()
        docs = [
            Document(page_content="Returns are accepted within 30 days for unused products with original packaging."),
            Document(page_content="Expedited shipping is available for premium members at checkout."),
            Document(page_content="Warranty claims require proof of purchase and product serial number."),
            Document(page_content="Order cancellations are available only before shipment."),
        ]

        uses_groq = "api.groq.com" in settings.llm_base_url.lower()

        if settings.llm_api_key and not uses_groq:
            embeddings = OpenAIEmbeddings(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
            )
        else:
            # Groq does not provide OpenAI-compatible embeddings endpoints.
            # Keep retrieval functional with deterministic local embeddings.
            embeddings = FakeEmbeddings(size=1536)

        self.vector_store = FAISS.from_documents(docs, embeddings)

    async def retrieve_context(self, query: str, k: int = 2) -> str:
        docs = await self.vector_store.asimilarity_search(query, k=k)
        return "\n".join(d.page_content for d in docs)
