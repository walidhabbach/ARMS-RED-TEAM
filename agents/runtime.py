"""Shared Agno agent factory; imports Agno lazily for offline testability."""
from config.llm import get_model


def build_agent(name: str, role: str, instructions: str):
    """Create an Agno Agent only when an LLM run is requested."""
    from agno.agent import Agent

    return Agent(
        name=name,
        role=role,
        model=get_model(),
        instructions=instructions,
        markdown=False,
    )


def run_text(agent, prompt: str) -> str:
    """Run an Agno agent and normalize its response to plain text."""
    result = agent.run(prompt)
    content = getattr(result, "content", result)
    if isinstance(content, str):
        return content
    if hasattr(content, "model_dump"):
        return content.model_dump_json(indent=2)
    return str(content)
