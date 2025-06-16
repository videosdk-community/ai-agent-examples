import asyncio
import aiohttp
from pathlib import Path
import sys
from videosdk.agents import Agent, AgentSession, RealTimePipeline, MCPServerStdio, MCPServerHTTP

# Import modules for Google Gemini Realtime
from videosdk.plugins.google import GeminiRealtime, GeminiLiveConfig

# # Import modules for OpenAI Realtime
# from videosdk.plugins.openai import OpenAIRealtime, OpenAIRealtimeConfig
# from openai.types.beta.realtime.session import  TurnDetection

# # Import modules for AWS NovaSonic Realtime
# from videosdk.plugins.aws import NovaSonicRealtime, NovaSonicConfig

##### Set your meeting ID ####
MEETING_ID = "your_generated_meeting_id"  # Replace with your actual meeting ID

class MyVoiceAgent(Agent):
    def __init__(self):
        # Define paths to your MCP servers
        mcp_script = Path(__file__).parent / "stdio.py"
        super().__init__(
            instructions="""You are a helpful assistant with access to real-time data. 
            You can provide current time information. 
            Always be conversational and helpful in your responses.""",
            mcp_servers=[
                # STDIO MCP Server (Local Python script for time)
                MCPServerStdio(
                    command=sys.executable,  # Use current Python interpreter
                    args=[str(mcp_script)],
                    client_session_timeout_seconds=30
                )#,
                # # HTTP MCP Server (External service example e.g Zapier)
                # MCPServerHTTP(
                #     url="https://your-mcp-service.com/api/mcp",
                #     client_session_timeout_seconds=30
                # )
            ]
        )

    async def on_enter(self) -> None:
        await self.session.say("Hi there! How can I help you today?")
    
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
        "name": "VideoSDK's MCP Agent", 
    }
    
    asyncio.run(main(context=make_context()))
