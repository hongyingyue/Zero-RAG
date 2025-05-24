from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain.schema import SystemMessage
from app.configs.settings import get_settings
from app.services.rag_service import RAGService

settings = get_settings()

class RAGTool(BaseTool):
    name = "rag_search"
    description = "Search for relevant information in the knowledge base"
    
    def __init__(self, rag_service: RAGService):
        super().__init__()
        self.rag_service = rag_service
    
    def _run(self, query: str) -> str:
        docs = self.rag_service.retrieve(query)
        return "\n\n".join(doc.page_content for doc in docs)

class AgentService:
    def __init__(self, rag_service: RAGService):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize tools
        self.tools = [RAGTool(rag_service)]
        
        # Create the agent
        self.agent = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a helpful AI assistant with access to a knowledge base.
            Use the tools available to you to find relevant information and provide accurate responses.
            Always be honest about what you know and don't know."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            max_iterations=settings.MAX_ITERATIONS,
            verbose=True
        )
    
    async def run(self, query: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Run the agent with a query and optional chat history."""
        chat_history = chat_history or []
        return await self.agent.ainvoke({
            "input": query,
            "chat_history": chat_history
        }) 