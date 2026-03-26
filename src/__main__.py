import logging
import os
import click
import uvicorn
from dotenv import load_dotenv
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from starlette.applications import Starlette
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from openai_agent import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import AgentExecutor as LangchainAgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomDocumentExecutor:
    def __init__(self, card: AgentCard, tools: list, api_key: str, system_prompt: str, model: str = "gpt-4o"):
        self.card = card
        self.chat_histories = {} 
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.2)
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        self.agent_executor = LangchainAgentExecutor(agent=agent, tools=tools, verbose=True)

    async def execute(self, context, queue, **kwargs):
        try:
            user_text = context.get_user_input()
        except AttributeError:
            user_text = context.message.parts[0].text
            
        # session history created or retreived
        session_id = getattr(context.message, 'session_id', 'default_session')
        if session_id not in self.chat_histories:
            self.chat_histories[session_id] = []
            
        current_history = self.chat_histories[session_id]
        logger.info(f"Processing request for session {session_id}: {user_text}")
        
        # Pass the history to the agent
        result = await self.agent_executor.ainvoke({
            "input": user_text,
            "chat_history": current_history
        })
        raw_output = result["output"]
        
        if isinstance(raw_output, list):
            text_blocks = [b["text"] if isinstance(b, dict) and "text" in b else str(b) for b in raw_output]
            output_text = "\n".join(text_blocks)
        else:
            output_text = str(raw_output)
            
        # conversation memory
        self.chat_histories[session_id].append(HumanMessage(content=user_text))
        self.chat_histories[session_id].append(AIMessage(content=output_text))
        
        # keep last 20 messages
        if len(self.chat_histories[session_id]) > 20:
            self.chat_histories[session_id] = self.chat_histories[session_id][-20:]
        
        # Standard A2A response handling
        from a2a.utils import new_agent_text_message
        
        task = getattr(context, 'current_task', None)
        task_id = getattr(task, 'id', 't-1')
        ctx_id = getattr(task, 'contextId', getattr(task, 'context_id', 'ctx-1'))
        
        if not task and hasattr(context, 'message'):
            ctx_id = getattr(context.message, 'contextId', getattr(context.message, 'context_id', ctx_id))
            
        response_msg = new_agent_text_message(output_text, ctx_id, task_id)
        
        if hasattr(queue, 'enqueue_event'):
            await queue.enqueue_event(response_msg)
        elif hasattr(queue, 'put'):
            await queue.put(response_msg)
            
        try:
            from a2a.server.tasks import TaskUpdater
            updater = TaskUpdater(queue, task_id, ctx_id)
            await updater.complete()
        except Exception as e:
            logger.debug(f"Task completion note: {e}")

@click.command()
@click.option("--host", "host", default="0.0.0.0")
@click.option("--port", "port", default=10010)
def main(host: str, port: int):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable must be set")
    
    skill = AgentSkill(
        id="generate-document",
        name="Generate Document",
        description="Determine format, plan content, and generate or edit a PPTX, DOCX, or XLSX file.",
        tags=["document", "pptx", "docx", "xlsx", "presentation", "spreadsheet"],
        examples=[
            "Create a 10-slide pitch deck for a fintech startup",
            "Change slide 3 to focus more on AI in the PPTX",
            "Add a new column for 'Q2 Projections' to the sales tracker XLSX"
        ],
    )

    agent_card = AgentCard(
        name="Document Creator Agent",
        description="Autonomously plans, generates, and edits formatted documents (PPTX, DOCX, XLSX) with embedded charts.",
        url="http://a2a-document-generator:5000/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True, chat_agent=True), # Note: Set chat_agent to True
        skills=[skill],
    )

    agent_data = create_agent()

    agent_executor = CustomDocumentExecutor(
        card=agent_card,
        tools=agent_data["tools"],
        api_key=api_key,
        system_prompt=agent_data["system_prompt"],
        model="gpt-4o",
    )

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, 
        task_store=InMemoryTaskStore()
    )

    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, 
        http_handler=request_handler
    )

    middleware = [
        Middleware(
            CORSMiddleware, 
            allow_origins=['*'], 
            allow_methods=['*'], 
            allow_headers=['*']  
        )
    ]
    
    app = Starlette(routes=a2a_app.routes(), middleware=middleware)
    
    logger.info(f"Starting Document Creator Agent on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()