from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import get_settings
from app.tools.support_tools import faq_retriever, order_status_checker, product_search


class SupportAgentFactory:
    def __init__(self) -> None:
        settings = get_settings()
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key or "EMPTY",
            base_url=settings.llm_base_url,
            temperature=0,
            streaming=True,
        )
        self.tools = [order_status_checker, product_search, faq_retriever]
        self.system_prompt = (
            "You are a concise and helpful e-commerce support assistant. "
            "Detect user intent, use tools when needed, and ground responses in provided context."
        )

    def build(self):
        return create_agent(model=self.llm, tools=self.tools, system_prompt=self.system_prompt)

    async def ainvoke(self, message: str, context: str, chat_history: list[BaseMessage]) -> str:
        agent = self.build()
        messages: list[BaseMessage] = [SystemMessage(content=self.system_prompt), *chat_history]
        messages.append(HumanMessage(content=f"RAG Context:\n{context}\n\nUser Question: {message}"))

        result = await agent.ainvoke({"messages": messages})
        output_messages = result.get("messages", [])
        for item in reversed(output_messages):
            if isinstance(item, AIMessage):
                return item.content if isinstance(item.content, str) else str(item.content)
        return "Sorry, I couldn't generate a response."
