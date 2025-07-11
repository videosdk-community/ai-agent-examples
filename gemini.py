import asyncio
import aiohttp
from videosdk.agents import Agent, AgentSession, RealTimePipeline, function_tool, ConversationFlow, ChatRole
from typing import AsyncIterator
from videosdk.plugins.google import GeminiRealtime, GeminiLiveConfig
from videosdk.agents import RealTimePipeline

##### Set your meeting ID ####
MEETING_ID = "577t-awrs-bptv"  # Replace with your actual meeting ID

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

class MyConversationFlow(ConversationFlow):
    def __init__(self, agent, stt=None, llm=None, tts=None):
        super().__init__(agent, stt, llm, tts)

    async def run(self, transcript: str) -> AsyncIterator[str]:
        """Main conversation loop: handle a user turn."""
        await self.on_turn_start(transcript)

        processed_transcript = transcript.lower().strip()
        self.agent.chat_context.add_message(role=ChatRole.USER, content=processed_transcript)
        
        async for response_chunk in self.process_with_llm():
            yield response_chunk

        await self.on_turn_end()

    async def on_turn_start(self, transcript: str) -> None:
        """Called at the start of a user turn."""
        self.is_turn_active = True

    async def on_turn_end(self) -> None:
        """Called at the end of a user turn."""
        self.is_turn_active = False

async def main(context: dict):
    model = GeminiRealtime(
        model="gemini-2.0-flash-live-001",
        config=GeminiLiveConfig(
            voice="Leda", # Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, and Zephyr.
            response_modalities=["AUDIO"]
        )
    )


    pipeline = RealTimePipeline(model=model)
    session = AgentSession(
        agent=MyVoiceAgent(),
        pipeline=pipeline,
        conversation_flow=MyConversationFlow(MyVoiceAgent()),
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
        "name": "Gemini Agent", 
    }
    
    asyncio.run(main(context=make_context()))
