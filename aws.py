import asyncio
import aiohttp
from videosdk.agents import Agent, AgentSession, RealTimePipeline, function_tool
from videosdk.plugins.aws import NovaSonicRealtime, NovaSonicConfig

##### Set your meeting ID ####
MEETING_ID = "your_generated_meeting_id"  # Replace with your actual meeting ID

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


async def main(context: dict):
    model = NovaSonicRealtime(
        model="amazon.nova-sonic-v1:0",
        config=NovaSonicConfig(
            voice="tiffany", #  "tiffany","matthew", "amy"
            temperature=0.7,
            top_p=0.9
        )
    )


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
        "name": "AWS Agent", 
    }
    
    asyncio.run(main(context=make_context()))
