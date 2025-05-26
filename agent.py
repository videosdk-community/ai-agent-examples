from videosdk.agents import Agent
from prompts import PROMPTS
import logging

# Define which use case prompt to use (e.g., "Tutor", "Doctor", "Recruiter", "Companion").
# Change this to the desired use case.
usecase = "Doctor"

logging.basicConfig(level=logging.INFO)

class VoiceAgent(Agent):
    def __init__(self):
        # Retrieve the prompt text for the chosen usecase
        prompt_text = PROMPTS.get(usecase)
        if not prompt_text:
            logging.error(f"No prompt found for usecase '{usecase}'. Check your PROMPTS dictionary.")
            raise ValueError(f"PROMPTS does not contain key '{usecase}'")
        
        # Log which prompt is being used
        logging.info(f"Using prompt for usecase '{usecase}': {prompt_text}")
        
        # Pass the prompt text to the base Agent class
        super().__init__(
            instructions=prompt_text
        )

    async def on_enter(self) -> None:
        """Called when the agent first joins the meeting"""
        logging.info("VoiceAgent has entered the meeting.")

    async def on_exit(self) -> None:
        """Called when the agent leaves the meeting"""
        logging.info("VoiceAgent is exiting the meeting.")
