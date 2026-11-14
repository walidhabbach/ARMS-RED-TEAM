"""Small connectivity test for the configured Agno model provider."""
from agno.agent import Agent
from config.llm import get_model


def main():
    agent = Agent(
        name="ARMS-LLM-Connectivity-Test",
        model=get_model(),
        instructions="Answer briefly. You are testing model connectivity, not analyzing real banking data.",
        markdown=False,
    )
    response = agent.run("Reply with exactly: ARMS LLM connection successful.")
    print(response.content)


if __name__ == "__main__":
    main()
