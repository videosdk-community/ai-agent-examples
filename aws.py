from videosdk.agents import Agent, AgentSession, Pipeline, function_tool, JobContext, RoomOptions, WorkerJob
from videosdk.plugins.aws import NovaSonicRealtime, NovaSonicConfig

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler()])

class MyVoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
You are a helpful voice assistant. Respond to user queries with clear and concise answers. Use a friendly tone and provide relevant information based on the user's request.
    """,
        )

    async def on_enter(self) -> None:
        await self.session.say("Hello, how can I help you today?")

    async def on_exit(self) -> None:
        await self.session.say("Goodbye!")


async def start_session(context: JobContext):
    model = NovaSonicRealtime(
        model="amazon.nova-sonic-v1:0",
        config=NovaSonicConfig(
            voice="tiffany", #  "tiffany","matthew", "amy"
            temperature=0.7,
            top_p=0.9
        )
    )


    pipeline = Pipeline(llm=model)
    session = AgentSession(
        agent=MyVoiceAgent(),
        pipeline=pipeline,
    )

    await session.start(wait_for_participant=True, run_until_shutdown=True)

def make_context() -> JobContext:
    room_options = RoomOptions(
        name="AWS Realtime Agent",
        playground=True,
    )
    return JobContext(room_options=room_options)

if __name__ == "__main__":
    job = WorkerJob(entrypoint=start_session, jobctx=make_context)
    job.start()
