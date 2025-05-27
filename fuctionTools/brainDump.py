# --- Configuration for Google Service Account ---
# Configuration key file for Google Service Account
SERVICE_ACCOUNT_FILE = "service-account-key.json"

# The ID of the Google Document where brain dump entries will be saved.
GOOGLE_DOC_ID = "your-google-doc-id"  

# The ID of the VideoSDK meeting where this agent will be used.
MEETING_ID =  "your-meeting-id" 
# --- End of Configuration ---

import asyncio
import aiohttp
from datetime import datetime
import os
import dotenv
from videosdk.agents import Agent, AgentSession, RealTimePipeline, function_tool

# Import modules for Google Gemini Realtime
from videosdk.plugins.google import GeminiRealtime, GeminiLiveConfig
from videosdk.agents import RealTimePipeline

# # Import modules for OpenAI Realtime
# from videosdk.plugins.openai import OpenAIRealtime, OpenAIRealtimeConfig
# from openai.types.beta.realtime.session import  TurnDetection

# # Import modules for AWS NovaSonic Realtime
# from videosdk.plugins.aws import NovaSonicRealtime, NovaSonicConfig

# Google API Client libraries
from google.oauth2 import service_account # Import for service account
from googleapiclient.discovery import build as google_build_service
from googleapiclient.errors import HttpError as GoogleHttpError

# Path to the .env file
dotenv_path = "../.env"
# Load environment variables from the .env file
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)


class MyVoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "Your name is VideoSDK's Brain Dump Agent. You are a personal daily diary. "
                "Your primary role is to listen attentively as the user shares their thoughts, feelings, or daily events. "
                "Keep your own responses very minimal, using phrases like 'Go on.', 'I'm listening.', 'Tell me more.', or simple acknowledgements like 'Mm-hmm' or 'Okay' to encourage the user to continue speaking. "
                "Avoid interrupting the user or asking clarifying questions unless it's absolutely critical for understanding a tool's arguments (which is rare for this agent's primary function). "
                "Let the user speak freely and dump all their thoughts. "
                "When the user indicates they are finished (e.g., 'That's all for today', 'I'm done', 'Please save this now'), "
                "use the 'save_entry_to_google_doc' function. "
                "The 'entry_content' for this function should be a direct dump of everything the user has verbally shared during this session. "
                "Capture their raw thoughts, ramblings, and expressed feelings as faithfully as possible, like a raw, unfiltered entry in a personal diary. Do not summarize or heavily edit it. "
                "Confirm with the user after a successful save. If saving fails, inform them of the issue and the reason if available."
            ),
        )
        # Initialize credentials here if needed, or within the tool
        try:
            self.google_creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE,
                scopes=['https://www.googleapis.com/auth/documents']
            )
            print(f"### Successfully loaded service account credentials from {SERVICE_ACCOUNT_FILE}")
        except FileNotFoundError:
            self.google_creds = None
            print(f"### ERROR: Service account key file not found at {SERVICE_ACCOUNT_FILE}. Google Docs will not work.")
        except Exception as e:
            self.google_creds = None
            print(f"### ERROR: Failed to load service account credentials: {e}. Google Docs will not work.")


    async def on_enter(self) -> None:
        await self.session.say("Hello, I'm your Brain Dump assistant. Feel free to share your thoughts whenever you're ready. I'm here to listen.")
    
    async def on_exit(self) -> None:
        await self.session.say("Goodbye!")
        
    @function_tool
    async def save_entry_to_google_doc(self, entry_content: str) -> dict:
        """Saves the user's raw brain dump entry to a pre-configured Google Doc.
        This function should be called when the user indicates they are finished sharing their thoughts for the current session.
        The entry will be formatted with today's date as a heading and appended to the document.

        Args:
            entry_content: The direct, raw textual dump of everything the user has shared during the session. This should be as close to their spoken words as possible.
        """
        print(f"### Attempting to save brain dump entry (first 100 chars): {entry_content[:100]}...")
        document_id = self.session.context.get("google_doc_id")

        if not self.google_creds:
            error_message = "Google credentials not loaded. Cannot save to Google Docs."
            print(f"### {error_message}")
            await self.session.say(error_message)
            return {"status": "error", "message": error_message}

        if not document_id or document_id == "YOUR_GOOGLE_DOC_ID_HERE": # Ensure placeholder is checked
            error_message = "Google Doc ID is not configured or is still the placeholder. Cannot save entry."
            print(f"### {error_message}")
            await self.session.say(error_message)
            return {"status": "error", "message": error_message}

        try:
            service = google_build_service('docs', 'v1', credentials=self.google_creds)
            today_date_str = datetime.now().strftime("%Y-%m-%d %A")
            
            # Using endOfSegmentLocation: {} with insertText effectively appends.
            # A page break could be inserted for better separation if desired:
            # {'insertPageBreak': {'endOfSegmentLocation': {}}}
            # For now, a clear separator with date.
            content_to_insert_as_page = f"\n\n--- {today_date_str} ---\n\n{entry_content}\n\n"
            
            requests = [
                {
                    'insertText': {
                        'endOfSegmentLocation': {}, # Appends to the end of the document body
                        'text': content_to_insert_as_page
                    }
                }
            ]
            
            service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            success_message = "Your thoughts for today have been saved to your journal."
            print(f"### {success_message}")
            await self.session.say(success_message)
            return {"status": "success", "message": success_message}

        except GoogleHttpError as e:
            error_message = f"Google API Error: Failed to save entry. Status: {e.resp.status}, Reason: {e._get_reason()}"
            print(f"### {error_message}")
            await self.session.say("Sorry, there was an issue saving your thoughts to Google Docs.")
            return {"status": "error", "message": error_message}
        except Exception as e:
            error_message = f"An unexpected error occurred while saving to Google Docs: {str(e)}"
            print(f"### {error_message}")
            await self.session.say("Sorry, an unexpected error occurred while trying to save your thoughts.")
            return {"status": "error", "message": error_message}


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
        print("Brain Dump Agent started. Waiting for interaction...")
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await session.close()

if __name__ == "__main__":
    def make_context():
        return {
            "meetingId": MEETING_ID,
            "name": "Gemini Brain Dump Agent",
            "google_doc_id": GOOGLE_DOC_ID
        }
    
    print("Starting Brain Dump Agent...")

    asyncio.run(main(context=make_context()))