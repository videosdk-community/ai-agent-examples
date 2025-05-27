# fuctionTools

This folder contains utility tools and function integrations that can be used by AI agents to extend their capabilities.

## Included Tools
- **brainDump.py**: Tool for capturing and storing free-form notes or ideas during a session.
- **eventScheduler.py**: Allows agents to schedule events or reminders for users.
- **expenseTracker.py**: Tracks expenses and manages simple financial records.

## How to Use
- These tools are designed to be imported and used within agent scripts.
- You can extend or modify them to add more functionality as needed.

## Requirements
- See `requirements.txt` in this folder for any additional dependencies.

## Google Cloud Service Account Setup (for Google Drive/Calendar integration)

To use tools that interact with Google services (like `eventScheduler.py` or a potential Google Drive/Sheets integration for `brainDump.py` or `expenseTracker.py`), you'll need to set up a Google Cloud service account:

1.  **Create a Google Cloud Project:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project or select an existing one.

2.  **Enable APIs:**
    *   In your project, navigate to "APIs & Services" > "Library".
    *   Search for and enable the following APIs:
        *   Google Drive API
        *   Google Calendar API
        *   Google Sheets API (if you plan to use it)

3.  **Create a Service Account:**
    *   Go to "APIs & Services" > "Credentials".
    *   Click "Create Credentials" and select "Service account".
    *   Fill in the service account details (name, ID, description).
    *   Grant appropriate roles. For basic Drive/Calendar/Sheets access, "Editor" might be sufficient for testing, but for production, use more granular permissions.
        *   For Calendar: `Google Calendar API User` or similar.
        *   For Drive/Sheets: `Google Drive API User` or `Google Sheets API User`.
    *   Click "Done".

4.  **Generate a JSON Key:**
    *   Find your newly created service account in the "Credentials" list.
    *   Click on the service account email.
    *   Go to the "KEYS" tab.
    *   Click "ADD KEY" and select "Create new key".
    *   Choose "JSON" as the key type and click "CREATE".
    *   A JSON file will be downloaded. **Rename this file to `service-account-key.json` and save it in this `fuctionTools/` folder.**
    *   **Important:** This JSON file contains sensitive credentials. Ensure it's listed in your `.gitignore` if you haven't already, to prevent committing it to your repository.

5.  **Share Google Resources with the Service Account:**
    *   **Google Drive (for Docs/Sheets):**
        *   Open the Google Doc or Sheet you want the agent to access.
        *   Click the "Share" button.
        *   Add the service account's email address (e.g., `your-service-account-name@your-project-id.iam.gserviceaccount.com`) and give it "Editor" (or appropriate) permissions.
    *   **Google Calendar:**
        *   Go to your Google Calendar settings.
        *   Under "Settings for my calendars", select the calendar you want to share.
        *   Click on "Share with specific people or groups".
        *   Add the service account's email address and choose the appropriate permission level (e.g., "Make changes to events").

## Finding IDs

*   **Google Doc/Sheet ID:**
    *   Open the Google Doc or Sheet in your browser.
    *   The ID is part of the URL. For example, in `https://docs.google.com/document/d/THIS_IS_THE_ID/edit`, `THIS_IS_THE_ID` is the Document ID.
    *   Similarly for Sheets: `https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit#gid=0`.
*   **Google Calendar ID:**
    *   For your primary calendar, the ID is usually your email address.
    *   For other calendars:
        *   Go to Google Calendar settings.
        *   Under "Settings for my calendars", select the calendar.
        *   The "Calendar ID" is listed under "Integrate calendar".

These IDs will be needed by the agent tools to interact with the correct Google Drive files or Calendars.

---

For more on extending agents with tools, see the [AI Agents Docs](https://docs.videosdk.live/ai_agents/introduction).
