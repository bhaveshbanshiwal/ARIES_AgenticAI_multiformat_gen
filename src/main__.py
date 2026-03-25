import logging
import os
import click
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from dotenv import load_dotenv
from starlette.applications import Starlette

from openai_agent import create_agent
# Assuming OpenAIAgentExecutor is available in your a2a setup context
from openai_agent_executor import OpenAIAgentExecutor

load_dotenv()
logging.basicConfig(level=logging.INFO)

@click.command()
@click.option("--host", "host", default="0.0.0.0")
@click.option("--port", "port", default=10010)
def main(host: str, port: int):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable must be set")

    skill = AgentSkill(
        id="generate-document",
        name="Generate Document",
        description="Determine format, plan content, and generate a PPTX or DOCX file.",
        tags=["document", "pptx", "docx", "presentation"],
        examples=[
            "Create a 10-slide pitch deck for a fintech startup",
            "Write a competitive analysis report as a DOCX with a bar chart"
        ],
    )

    agent_card = AgentCard(
        name="Document Creator Agent",
        description="Autonomously plans and generates formatted documents (PPTX, DOCX) with embedded charts.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    agent_data = create_agent()

    agent_executor = OpenAIAgentExecutor(
        card=agent_card,
        tools=agent_data["tools"],
        api_key=api_key,
        system_prompt=agent_data["system_prompt"],
        model="gpt-4o",
    )

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )
    
    app = Starlette(routes=a2a_app.routes())
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()