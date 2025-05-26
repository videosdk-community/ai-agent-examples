import asyncio
import aiohttp
from videosdk.agents import Agent, AgentSession, RealTimePipeline, function_tool
from videosdk.plugins.openai import OpenAIRealtime, OpenAIRealtimeConfig
from openai.types.beta.realtime.session import  TurnDetection
from prompts import PROMPTS 

usecase = "Companion"  # Change this to the desired use case



class MyVoiceAgent(Agent):
    def __init__(self):
        prompt_text = PROMPTS.get(usecase, "")
        super().__init__(
            instructions=prompt_text
        )

    async def on_enter(self) -> None:
        await self.session.say("Hello, how can I help you today?")
    
    async def on_exit(self) -> None:
        await self.session.say("Goodbye!")


async def main(context: dict):
    model = OpenAIRealtime(
    model="gpt-4o-realtime-preview",
    # When OPENAI_API_KEY is set in .env - DON'T pass api_key parameter
    api_key="Your-Openai-api-key",
    config=OpenAIRealtimeConfig(
        voice="alloy", # alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, and verse
        modalities=["text", "audio"],
        turn_detection=TurnDetection(
            type="server_vad",
            threshold=0.5,
            prefix_padding_ms=300,
            silence_duration_ms=200,
        ),
        tool_choice="auto"
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
        return {"meetingId": "your-meeting-d", "name": "VideoSDK's Agent", "videosdk_auth": "your-auth-token"}
    
    asyncio.run(main(context=make_context()))
