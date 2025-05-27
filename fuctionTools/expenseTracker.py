# --- Configuration for Google Service Account ---
# Set this environment variable or place the key file in the same directory
SERVICE_ACCOUNT_FILE = "service-account-key.json"

# The ID of the Google Spreadsheet where expenses will be logged.
GOOGLE_SHEET_ID = "your-google-sheet-id"  # Replace with your actual Google Sheet ID

# The name of the sheet within your Google Spreadsheet where expenses will be logged.
DEFAULT_SHEET_NAME = "Sheet1"

# The ID of the VideoSDK meeting where this agent will be used.
MEETING_ID =  "your-meeting-id" 
# --- End of Configuration ---

import asyncio
import aiohttp
import os
import json
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
from google.oauth2 import service_account
from googleapiclient.discovery import build as google_build_service
from googleapiclient.errors import HttpError as GoogleHttpError

# Path to the .env file
dotenv_path = "../.env"
# Load environment variables from the .env file
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

class FinanceAssistantAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "Your name is VideoSDK's Finance Assistant. You are here to help users track their expenses. "
                "Listen carefully for when a user mentions an expense they've made. "
                "When an expense is mentioned, try to identify the 'item' (what was purchased), the 'amount' spent, the 'category' (e.g., Food, Transport, Shopping, Utilities, Entertainment), and the 'date' of the expense. "
                "If the user does not specify a date, assume the expense occurred 'today'. Please try to provide the date in 'YYYY-MM-DD' format (e.g., '2023-10-27'). "
                "For the amount, try to extract just the numerical value. "
                "If the category is not explicitly mentioned by the user, you can ask 'What category would you like to put that under?' or make a reasonable guess based on the item (e.g., 'coffee' is likely 'Food'). "
                "Once you have the date, item, amount, and category, use the 'log_expense_to_google_sheet' function to record it. "
                "After attempting to log the expense, inform the user whether it was successful or if there was an error."
            ),
        )
        try:
            self.google_creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE,
                scopes=['https://www.googleapis.com/auth/spreadsheets'] # Scope for Google Sheets
            )
            print(f" Successfully loaded Google Service Account credentials from {SERVICE_ACCOUNT_FILE}")
        except FileNotFoundError:
            print(f" ERROR: Service account key file not found at {SERVICE_ACCOUNT_FILE}. Google Sheets integration will NOT work.")
        except Exception as e:
            print(f" ERROR: Failed to load service account credentials: {e}. Google Sheets integration will NOT work.")

    async def on_enter(self) -> None:
        await self.session.say("Hello, I'm your Finance Assistant. Tell me about any expenses you'd like to log.")

    async def on_exit(self) -> None:
        await self.session.say("Goodbye! Hope your finances are in order.")


    @function_tool
    async def log_expense_to_google_sheet(
        self,
        date_of_expense: str, # New argument for the date
        item: str,
        amount: str,
        category: str
    ) -> dict:
        """Logs a new expense to the configured Google Sheet.

        Args:
            date_of_expense: The date of the expense, preferably in YYYY-MM-DD format (e.g., "2023-10-27").
            item: The name or description of the expense item (e.g., "Coffee", "Train ticket").
            amount: The monetary value of the expense (e.g., "5.50", "25").
            category: The category of the expense (e.g., "Food", "Transport", "Groceries").
        """
        print(f" Attempting to log expense: Date='{date_of_expense}', Item='{item}', Amount='{amount}', Category='{category}'")

        if not self.google_creds:
            error_message = "Google credentials not loaded. Cannot log expense to Google Sheets."
            print(f" {error_message}")
            await self.session.say(error_message)
            return {"status": "error", "message": error_message}

        spreadsheet_id = self.session.context.get("google_sheet_id")
        sheet_name = self.session.context.get("google_sheet_name", DEFAULT_SHEET_NAME)

        if not spreadsheet_id or spreadsheet_id == "YOUR_GOOGLE_SHEET_ID_HERE":
            error_message = "Google Sheet ID is not configured or is still the placeholder. Cannot log expense."
            print(f" {error_message}")
            await self.session.say(error_message)
            return {"status": "error", "message": error_message}

        try:
            try:
                numeric_amount = float(str(amount).replace('$', '').replace('€', '').replace('£', '').strip())
            except ValueError:
                print(f"Warning: Could not convert amount '{amount}' to a number. Logging as string.")
                numeric_amount = amount # Log as string if conversion fails

            service = google_build_service('sheets', 'v4', credentials=self.google_creds)

            # Use the date_of_expense provided by the AI
            row_to_append = [date_of_expense, item, numeric_amount, category]

            body = {
                'values': [row_to_append]
            }

            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body
            ).execute()

            print(f"Expense logged successfully to Google Sheet. Result: {result}")
            success_message = f"Okay, I've logged {item} for {amount} on {date_of_expense} under {category}."
            await self.session.say(success_message)
            return {"status": "success", "message": success_message, "updates": result.get("updates")}

        except GoogleHttpError as e:
            error_detail = e._get_reason()
            try:
                error_json = json.loads(e.content)
                error_detail = error_json.get("error", {}).get("message", error_detail)
            except:
                pass
            error_message = f"Google API Error: Failed to log expense. {error_detail}"
            print(f" {error_message}")
            await self.session.say("Sorry, I encountered an error trying to log that to the Google Sheet.")
            return {"status": "error", "message": error_message}
        except Exception as e:
            error_message = f"An unexpected error occurred while logging to Google Sheets: {str(e)}"
            print(f" {error_message}")
            await self.session.say("Sorry, an unexpected error occurred while trying to log your expense.")
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
        agent=FinanceAssistantAgent(),
        pipeline=pipeline,
        context=context
    )

    try:
        await session.start()
        print("Agent started. Waiting for expense details...")
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("Shutting down Agent...")
    finally:
        await session.close()

if __name__ == "__main__":
    def make_context():
        return {
            "meetingId": MEETING_ID,
            "name": "Expense Tracker",
            "google_sheet_id": GOOGLE_SHEET_ID,
            "google_sheet_name": DEFAULT_SHEET_NAME
        }

    print("Starting Agent...")

    asyncio.run(main(context=make_context()))