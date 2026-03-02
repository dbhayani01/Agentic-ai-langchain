from collections.abc import AsyncGenerator

from langchain_core.messages import HumanMessage

from app.agents.support_agent import SupportAgentFactory
from app.services.repository import ChatRepository
from app.services.retrieval_service import RetrievalService


class ChatService:
    def __init__(self, repository: ChatRepository) -> None:
        self.repository = repository
        self.retrieval = RetrievalService()
        self.agent_executor = SupportAgentFactory().build()

    async def handle_chat(self, session_id: str, message: str) -> str:
        context = await self.retrieval.retrieve_context(message)
        result = await self.agent_executor.ainvoke({"input": message, "context": context})
        answer = result.get("output", "Sorry, I couldn't generate a response.")
        await self.repository.add_message(session_id, "user", message)
        await self.repository.add_message(session_id, "assistant", answer)
        return answer

    async def stream_chat(self, session_id: str, message: str) -> AsyncGenerator[str, None]:
        context = await self.retrieval.retrieve_context(message)
        await self.repository.add_message(session_id, "user", message)

        chunks: list[str] = []
        prompt = (
            "You are an e-commerce support assistant. Use this context when useful:\n"
            f"{context}\nUser: {message}"
        )
        async for chunk in self.agent_executor.agent.llm.astream([HumanMessage(content=prompt)]):
            text = getattr(chunk, "content", "") or ""
            if text:
                chunks.append(text)
                yield text

        await self.repository.add_message(session_id, "assistant", "".join(chunks))
