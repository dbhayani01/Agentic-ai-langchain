from collections.abc import AsyncGenerator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from app.agents.support_agent import SupportAgentFactory
from app.services.repository import ChatRepository
from app.services.retrieval_service import RetrievalService


class ChatService:
    def __init__(self, repository: ChatRepository) -> None:
        self.repository = repository
        self.retrieval = RetrievalService()
        self.agent_factory = SupportAgentFactory()
        self.agent_executor = self.agent_factory.build()

    async def _build_chat_history(self, session_id: str) -> list[BaseMessage]:
        history_rows = await self.repository.get_history(session_id)
        messages: list[BaseMessage] = []
        for item in history_rows:
            if item.role == "user":
                messages.append(HumanMessage(content=item.content))
            elif item.role == "assistant":
                messages.append(AIMessage(content=item.content))
        return messages

    async def handle_chat(self, session_id: str, message: str) -> str:
        context = await self.retrieval.retrieve_context(message)
        chat_history = await self._build_chat_history(session_id)

        result = await self.agent_executor.ainvoke(
            {"input": message, "context": context, "chat_history": chat_history}
        )
        answer = result.get("output", "Sorry, I couldn't generate a response.")

        await self.repository.add_message(session_id, "user", message)
        await self.repository.add_message(session_id, "assistant", answer)
        return answer

    async def stream_chat(self, session_id: str, message: str) -> AsyncGenerator[str, None]:
        context = await self.retrieval.retrieve_context(message)
        history = await self._build_chat_history(session_id)
        await self.repository.add_message(session_id, "user", message)

        history_text = "\n".join(
            f"{('User' if isinstance(msg, HumanMessage) else 'Assistant')}: {msg.content}" for msg in history[-6:]
        )
        prompt = (
            "You are an e-commerce support assistant.\n"
            f"Recent conversation:\n{history_text or 'None'}\n\n"
            f"RAG Context:\n{context}\n\nUser: {message}"
        )

        chunks: list[str] = []
        async for chunk in self.agent_factory.llm.astream([HumanMessage(content=prompt)]):
            text = getattr(chunk, "content", "") or ""
            if text:
                chunks.append(text)
                yield text

        await self.repository.add_message(session_id, "assistant", "".join(chunks))
