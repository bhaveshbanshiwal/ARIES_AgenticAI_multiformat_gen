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

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomDocumentExecutor:
    """
    A custom A2A agent executor to replace OpenAIAgentExecutor.
    It bridges the A2A SDK gateway requests with LangChain's tool-calling logic.
    """
    def __init__(self, card: AgentCard, tools: list, api_key: str, system_prompt: str, model: str = "gpt-4o"):
        self.card = card
        
        # Initialize LangChain Gemini Chat Model
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.2)
        
        # Build the prompt template with a scratchpad for tool execution history
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the LangChain tool-calling agent
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        self.agent_executor = LangchainAgentExecutor(agent=agent, tools=tools, verbose=True)

    async def execute(self, context, queue, **kwargs):
        # 1. Safely extract the user's message using the official A2A helper
        try:
            user_text = context.get_user_input()
        except AttributeError:
            user_text = context.message.parts[0].text
            
        logger.info(f"Processing request: {user_text}")
        
        # 2. Run the LangChain agent asynchronously
        result = await self.agent_executor.ainvoke({"input": user_text})
        raw_output = result["output"]
        
        # Ensure output is a string (Gemini/LangChain sometimes returns a list of blocks)
        if isinstance(raw_output, list):
            text_blocks = []
            for block in raw_output:
                if isinstance(block, dict) and "text" in block:
                    text_blocks.append(block["text"])
                elif isinstance(block, str):
                    text_blocks.append(block)
            output_text = "\n".join(text_blocks)
        else:
            output_text = str(raw_output)
        
        # 3. Create the response message using A2A utilities
        from a2a.utils import new_agent_text_message
        
        # Extract task tracking IDs so the client knows what this response belongs to
        task = getattr(context, 'current_task', None)
        task_id = getattr(task, 'id', 't-1')
        ctx_id = getattr(task, 'contextId', getattr(task, 'context_id', 'ctx-1'))
        
        if not task and hasattr(context, 'message'):
            ctx_id = getattr(context.message, 'contextId', getattr(context.message, 'context_id', ctx_id))
            
        response_msg = new_agent_text_message(output_text, ctx_id, task_id)
        
        # 4. Push the response back into the A2A event queue
        if hasattr(queue, 'enqueue_event'):
            await queue.enqueue_event(response_msg)
        elif hasattr(queue, 'put'):
            await queue.put(response_msg)
            
        # 5. Mark the task as officially completed
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
    

    # 1. Define the Agent's Skillset for the Registry
    skill = AgentSkill(
        id="generate-document",
        name="Generate Document",
        description="Determine format, plan content, and generate a PPTX, DOCX, or XLSX file.",
        tags=["document", "pptx", "docx", "xlsx", "presentation", "spreadsheet"],
        examples=[
            "Create a 10-slide pitch deck for a fintech startup",
            "Write a competitive analysis report as a DOCX with a bar chart",
            "Build a sales performance tracker for Q1 as an XLSX"
        ],
    )

    # 2. Define the Agent Card
    agent_card = AgentCard(
        name="Document Creator Agent",
        description="Autonomously plans and generates formatted documents (PPTX, DOCX, XLSX) with embedded charts.",
        url="http://a2a-document-generator:5000/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    # 3. Retrieve tools and prompt from openai_agent.py
    agent_data = create_agent()

    # 4. Initialize our Custom Executor
    agent_executor = CustomDocumentExecutor(
        card=agent_card,
        tools=agent_data["tools"],
        api_key=api_key,
        system_prompt=agent_data["system_prompt"],
        model="gpt-4o",
    )

    # 5. Bind the Executor to the A2A Request Handler
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, 
        task_store=InMemoryTaskStore()
    )

    # 6. Start the Starlette Server
    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, 
        http_handler=request_handler
    )

    # ADD THESE LINES TO ALLOW CORS PREFLIGHT REQUESTS
    middleware = [
        Middleware(
            CORSMiddleware, 
            allow_origins=['*'], # Allows all domains
            allow_methods=['*'], # Allows all methods (GET, POST, OPTIONS, etc.)
            allow_headers=['*']  # Allows all headers
        )
    ]
    
    # Pass the middleware into the Starlette app
    app = Starlette(routes=a2a_app.routes(), middleware=middleware)
    
    logger.info(f"Starting Document Creator Agent on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()