from videosdk.agents import Agent, AgentSession, Pipeline, function_tool, JobContext, RoomOptions, WorkerJob

# Import modules for Google Gemini Realtime
from videosdk.plugins.google import GeminiRealtime, GeminiLiveConfig

# # Import modules for OpenAI Realtime
# from videosdk.plugins.openai import OpenAIRealtime, OpenAIRealtimeConfig
# from openai.types.beta.realtime.session import  TurnDetection

# # Import modules for AWS NovaSonic Realtime
# from videosdk.plugins.aws import NovaSonicRealtime, NovaSonicConfig

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler()])

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
    - After the story, invite the user to give more keywords for another tale if they'd like.

    Your goal is to entertain, surprise, and delight the listener through instant storytelling magic.
    """,
    )

    async def on_enter(self) -> None:
        await self.session.say("Hello! Give me 3 to 5 words, and I'll spin them into a story just for you.")

    async def on_exit(self) -> None:
        await self.session.say("Goodbye!")


async def start_session(context: JobContext):
    model = GeminiRealtime(
        model="gemini-3.1-flash-live-preview",
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


    pipeline = Pipeline(llm=model)
    session = AgentSession(
        agent=MyVoiceAgent(),
        pipeline=pipeline,
    )

    await session.start(wait_for_participant=True, run_until_shutdown=True)

def make_context() -> JobContext:
    room_options = RoomOptions(
        name="Storyteller Agent",
        playground=True,
    )
    return JobContext(room_options=room_options)

if __name__ == "__main__":
    job = WorkerJob(entrypoint=start_session, jobctx=make_context)
    job.start()
