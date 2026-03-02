from langchain.agents import create_openai_tools_agent
from langchain.agents.agent import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from app.core.config import get_settings
from app.tools.support_tools import faq_retriever, order_status_checker, product_search


class SupportAgentFactory:
    def __init__(self) -> None:
        settings = get_settings()
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key or "EMPTY",
            base_url=settings.openai_base_url,
            temperature=0,
            streaming=True,
        )
        self.tools = [order_status_checker, product_search, faq_retriever]
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def build(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a concise and helpful e-commerce support assistant. "
                    "Detect user intent, use tools when needed, and ground responses in provided context.",
                ),
                MessagesPlaceholder("chat_history"),
                ("human", "RAG Context:\n{context}\n\nUser Question: {input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, memory=self.memory, verbose=False)
