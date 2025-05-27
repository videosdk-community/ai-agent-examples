import asyncio
import aiohttp
from videosdk.agents import Agent, AgentSession, RealTimePipeline, function_tool

# Import modules for Google Gemini Realtime
from videosdk.plugins.google import GeminiRealtime, GeminiLiveConfig
from videosdk.agents import RealTimePipeline

# # Import modules for OpenAI Realtime
# from videosdk.plugins.openai import OpenAIRealtime, OpenAIRealtimeConfig
# from openai.types.beta.realtime.session import  TurnDetection

# # Import modules for AWS NovaSonic Realtime
# from videosdk.plugins.aws import NovaSonicRealtime, NovaSonicConfig

##### Set your meeting ID ####
MEETING_ID = "your_generated_meeting_id"  # Replace with your actual meeting ID

class MyVoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
    You are an AI recruiter participating in a live conversation with job candidates. Your role is to conduct initial screening interviews, assess communication skills, and gather relevant information about the candidate’s experience, skills, and career goals.
    - Start with a friendly greeting and introduce yourself as part of the recruitment team.
    - Ask open-ended questions about the candidate’s background, recent roles, key skills, and what they’re looking for.
    - Evaluate soft skills, communication clarity, and cultural fit through conversation.
    - Be professional, encouraging, and neutral — do not express personal opinions or make promises about hiring.
    - If needed, explain the role, company, and next steps in the hiring process.
    - Politely wrap up the conversation with a summary of what you’ve learned and thank the candidate.

    You are not responsible for making hiring decisions — your job is to gather clear, structured candidate information and leave them with a positive experience.
    """,
    )

    async def on_enter(self) -> None:
        await self.session.say("Hi! I'm your AI recruiter—ready to learn more about you. Can you start by telling me a bit about your background.")
    
    async def on_exit(self) -> None:
        await self.session.say("Goodbye!")


async def main(context: dict):
    model = GeminiRealtime(
        model="gemini-2.0-flash-live-001",
        config=GeminiLiveConfig(
            voice="Leda", # Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, and Zephyr.
            response_modalities=["AUDIO"]
        )
    )

# # Uncomment the following lines to use OpenAI Realtime
#     model = OpenAIRealtime(
#     model="gpt-4o-realtime-preview",
#     config=OpenAIRealtimeConfig(
#         voice="alloy", # alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, and verse
#         modalities=["text", "audio"],
#         turn_detection=TurnDetection(
#             type="server_vad",
#             threshold=0.5,
#             prefix_padding_ms=300,
#             silence_duration_ms=200,
#             ),
#         tool_choice="auto"
#         )
#     )

# # Uncomment the following lines to use AWS NovaSonic Realtime
#     model = NovaSonicRealtime(
#         model="amazon.nova-sonic-v1:0",
#         config=NovaSonicConfig(
#             voice="tiffany", #  "tiffany","matthew", "amy"
#             temperature=0.7,
#             top_p=0.9
#         )
#     )


    pipeline = RealTimePipeline(model=model)
    session = AgentSession(
        agent=MyVoiceAgent(),
        pipeline=pipeline,
        context=context
    )

    try:
        await session.start()
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await session.close()

if __name__ == "__main__":
    def make_context():
        return {
        "meetingId": MEETING_ID, 
        "name": "VideoSDK's Recruiter Agent", 
    }
    
    asyncio.run(main(context=make_context()))
