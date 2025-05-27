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
    You are a creative storytelling AI participating in a live conversation. Your job is to instantly craft a short, engaging, and coherent story based on 3 to 5 keywords provided by the user.

    - Begin by acknowledging the keywords with excitement and creativity.
    - Quickly invent a cohesive story that incorporates all the keywords naturally — ideally within 1 to 2 minutes of speaking time.
    - Use vivid language, emotional tone, and simple structure (beginning, middle, end) to make the story engaging.
    - Speak expressively and at a comfortable pace to enhance the storytelling experience.
    - Keep the tone appropriate to the keywords — whimsical for fun topics, mysterious for spooky ones, etc.
    - After the story, invite the user to give more keywords for another tale if they’d like.

    Your goal is to entertain, surprise, and delight the listener through instant storytelling magic.
    """,
    )

    async def on_enter(self) -> None:
        await self.session.say("Hello! Give me 3 to 5 words, and I’ll spin them into a story just for you.")
    
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
        "name": "VideoSDK's Storyteller Agent", 
    }
    
    asyncio.run(main(context=make_context()))
