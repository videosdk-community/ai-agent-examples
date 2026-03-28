# --- Configuration for Google Service Account ---
# Set this environment variable or place the key file in the same directory
SERVICE_ACCOUNT_FILE = "service-account-key.json"

# The ID of the Google Spreadsheet where expenses will be logged.
GOOGLE_CALENDER_ID = "your-google-calender-id"
# --- End of Configuration ---

import os
import dotenv
from datetime import datetime
from videosdk.agents import Agent, AgentSession, Pipeline, function_tool, JobContext, RoomOptions, WorkerJob

# Import modules for Google Gemini Realtime
from videosdk.plugins.google import GeminiRealtime, GeminiLiveConfig

# # Import modules for OpenAI Realtime
# from videosdk.plugins.openai import OpenAIRealtime, OpenAIRealtimeConfig
# from openai.types.beta.realtime.session import  TurnDetection

# # Import modules for AWS NovaSonic Realtime
# from videosdk.plugins.aws import NovaSonicRealtime, NovaSonicConfig

# Google API Client libraries
from google.oauth2 import service_account
from googleapiclient.discovery import build as google_build_service
from googleapiclient.errors import HttpError as GoogleHttpError

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler()])

# Path to the .env file
dotenv_path = "../.env"
# Load environment variables from the .env file
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

class MyCalendarAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are VideoSDK's Calendar Agent, designed to help users schedule events on their Google Calendar. "
                "When a user wants to create an event, gather the event title (summary), start time, and end time. "
                "Optionally, ask for a description, location, and the event's timezone (e.g., 'America/New_York'). "
                "Ensure times are in ISO 8601 format (e.g., '2025-06-15T09:00:00-07:00' or '2025-06-15T16:00:00Z') before calling the tool. "
                "Use the 'add_calendar_event' function. Confirm success or inform about failures."
            )
        )

        # Attempt to load Google service account credentials for Calendar API
        try:
            self.google_creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE,
                scopes=['https://www.googleapis.com/auth/calendar.events']
            )
            print(f"Successfully loaded Google Calendar credentials from {SERVICE_ACCOUNT_FILE}")
        except FileNotFoundError:
            self.google_creds = None
            print(f"ERROR: Service account key file not found at {SERVICE_ACCOUNT_FILE}. Calendar functionality will not work.")
        except Exception as e:
            self.google_creds = None
            print(f"ERROR: Failed to load Google Calendar credentials: {e}. Calendar functionality will not work.")

    async def on_enter(self) -> None:
        await self.session.say("Hello, I'm your Calendar Agent. How can I help with your schedule?")

    async def on_exit(self) -> None:
        await self.session.say("Goodbye!")

    @function_tool
    async def add_calendar_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: str = None,
        location: str = None,
        timezone: str = "UTC"
    ) -> dict:
        """
        Adds an event to Google Calendar. Requires event summary, ISO 8601 start and end times.
        Optional: description, location, timezone (IANA format, e.g., 'America/New_York').
        """
        print(f"Tool 'add_calendar_event' called with summary='{summary}', start_time='{start_time}', end_time='{end_time}'")

        if not self.google_creds:
            error_message = "Google Calendar service is not available due to credential issues."
            print(f"{error_message}")
            return {"status": "error", "message": error_message}

        # Use the module-level constant for the target calendar ID
        target_calendar_id = GOOGLE_CALENDER_ID
        if not target_calendar_id or target_calendar_id == "your-google-calender-id":
            target_calendar_id = "primary"
            print("WARNING: No Google Calendar ID provided. Defaulting to 'primary' calendar.")

        event_body = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {"dateTime": start_time, "timeZone": timezone},
            "end": {"dateTime": end_time, "timeZone": timezone},
            "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 30}]},
        }

        try:
            service = google_build_service("calendar", "v3", credentials=self.google_creds, cache_discovery=False)
            print(f"Creating event on calendar '{target_calendar_id}': {summary}")
            created_event = (
                service.events()
                .insert(calendarId=target_calendar_id, body=event_body)
                .execute()
            )
            event_link = created_event.get("htmlLink", "N/A")
            success_message = f"Okay, I've scheduled '{summary}' for you."
            print(f"Event created successfully. Link: {event_link}")
            return {"status": "success", "message": success_message, "event_link": event_link}

        except GoogleHttpError as e:
            reason = e._get_reason() if hasattr(e, "_get_reason") else "Unknown Google API error"
            status_code = e.resp.status if hasattr(e, "resp") else "N/A"
            error_message = (
                f"Failed to schedule event due to a Google API error: {reason} (Status: {status_code})."
            )
            print(f"ERROR: GoogleHttpError - {error_message} - Details: {e}")
            return {"status": "error", "message": error_message}

        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            print(f"ERROR: Unexpected error in add_calendar_event - {error_message}")
            return {"status": "error", "message": error_message}


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
        agent=MyCalendarAgent(),
        pipeline=pipeline,
    )

    await session.start(wait_for_participant=True, run_until_shutdown=True)

def make_context() -> JobContext:
    room_options = RoomOptions(
        name="Event Scheduler Agent",
        playground=True,
    )
    return JobContext(room_options=room_options)

if __name__ == "__main__":
    print(" Initializing Calendar Agent...")
    job = WorkerJob(entrypoint=start_session, jobctx=make_context)
    job.start()
