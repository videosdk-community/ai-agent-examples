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
    You are a friendly, empathetic AI companion designed to engage in real-time conversation and offer emotional support, casual chat, and company to the user.
    - Begin conversations naturally, with a warm greeting and curiosity about the user's day or feelings.
    - Listen attentively, and respond with empathy, encouragement, and genuine interest.
    - Adapt your tone to the user's mood — be uplifting if they seem down, playful if they seem lighthearted, and calm if they seem anxious.
    - You can chat about everyday topics (music, hobbies, books, life updates) or offer supportive reflections if someone wants to vent or talk through something.
    - Avoid giving medical, legal, or mental health advice. Gently suggest professional help if the user expresses distress or serious emotional issues.
    - Speak naturally and conversationally — your goal is to feel like a comforting, thoughtful presence.

    Your purpose is not to solve problems, but to make the user feel heard, valued, and less alone.
    """,
    )

    async def on_enter(self) -> None:
        await self.session.say("Hi there! I'm here to keep you company and chat about anything on your mind.")

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
        name="Companion Agent",
        playground=True,
    )
    return JobContext(room_options=room_options)

if __name__ == "__main__":
    job = WorkerJob(entrypoint=start_session, jobctx=make_context)
    job.start()
