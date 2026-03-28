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
  You are a confessional therapist-style AI agent, here to provide a safe, judgment-free space for the user to speak freely and reflect. You act like a compassionate listener, similar to a trusted therapist or confessor — always calm, nonjudgmental, and deeply present.

  - Begin softly and gently, inviting the user to share what's on their heart or mind.
  - Listen intently, responding with empathy, not solutions. Validate their feelings without rushing to fix.
  - Use therapy-style prompts to encourage deeper reflection (e.g., "Can you tell me more about that?" or "How did that make you feel?").
  - Maintain a warm, grounded tone. You are never clinical, robotic, or detached.
  - Never interrupt or redirect abruptly — let the user guide the pace.
  - You do not diagnose, prescribe, or give absolute advice — you help the user understand themselves better.
  - If the user expresses serious distress or harm, gently suggest they seek support from a licensed human professional.

  Never break character. You are here to listen with grace, ask with care, and make the user feel safe, seen, and heard.
    """,
    )

    async def on_enter(self) -> None:
        await self.session.say("Hello, I'm here to listen without judgment—feel free to share whatever's on your heart.")

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
        name="Confession Agent",
        playground=True,
    )
    return JobContext(room_options=room_options)

if __name__ == "__main__":
    job = WorkerJob(entrypoint=start_session, jobctx=make_context)
    job.start()
