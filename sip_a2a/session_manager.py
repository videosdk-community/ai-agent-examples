import os
import logging
from videosdk.agents import AgentSession, Pipeline
from videosdk.plugins.openai import OpenAILLM
from videosdk.plugins.google import GeminiRealtime, GeminiLiveConfig

logger = logging.getLogger(__name__)

def create_pipeline(agent_type: str):
    """
    Create appropriate pipeline based on agent type.

    Args:
        agent_type: Either "customer" for real-time audio or "specialist" for text processing

    Returns:
        Pipeline instance configured for the agent type
    """
    logger.info(f"Creating pipeline for agent_type: {agent_type}")

    if agent_type == "customer":
        # Customer agent uses pipeline for voice calls
        logger.info("Creating Pipeline for customer agent")

        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required for customer agent")

        logger.info("Initializing GeminiRealtime model...")
        model = GeminiRealtime(
            api_key=google_api_key,
            model="gemini-3.1-flash-live-preview",
            config=GeminiLiveConfig(
                voice="Leda",  # Choose appropriate voice
                response_modalities=["AUDIO"]  # Audio responses for voice calls
            )
        )
        logger.info("GeminiRealtime model initialized")

        pipeline = Pipeline(llm=model)
        logger.info("Pipeline created successfully")
        return pipeline

    elif agent_type == "specialist":
        # Specialist agent uses pipeline for text processing
        logger.info("Creating Pipeline for specialist agent")

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for specialist agent")

        logger.info("Initializing OpenAI LLM...")
        llm = OpenAILLM(api_key=openai_api_key)
        logger.info("OpenAI LLM initialized")

        pipeline = Pipeline(llm=llm)
        logger.info("Pipeline created successfully")
        return pipeline

    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

def create_session(agent, pipeline) -> AgentSession:
    """
    Create an agent session with appropriate configuration.

    Args:
        agent: Agent instance
        pipeline: Pipeline instance

    Returns:
        Configured AgentSession
    """
    session = AgentSession(
        agent=agent,
        pipeline=pipeline,
    )

    logger.info(f"Created session for agent {agent.id}")
    return session

# Alternative configurations for different scenarios

def create_customer_realtime_pipeline():
    """Create a pipeline specifically for customer service."""
    return Pipeline(
        llm=GeminiRealtime(
            api_key=os.getenv("GOOGLE_API_KEY"),
            model="gemini-3.1-flash-live-preview",
            config=GeminiLiveConfig(
                voice="Leda",
                response_modalities=["AUDIO"],
                # Additional configuration for better phone call handling
            )
        )
    )

def create_specialist_text_pipeline():
    """Create a text-only pipeline for specialist agents."""
    return Pipeline(
        llm=OpenAILLM(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o",  # Use appropriate model for loan expertise
        )
    )

# Example of mixed pipeline configuration if needed
def create_hybrid_customer_pipeline():
    """
    Create a hybrid pipeline that can handle both voice and text.
    This could be useful for agents that need to handle both modalities.
    """
    # This is for future extensibility - combining capabilities
    # For now, we use separate pipelines for clarity
    pass
