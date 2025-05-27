import asyncio
import os
import requests
from videosdk import MeetingConfig, VideoSDK
from meeting_events import MyMeetingEventHandler
import dotenv

# Path to the .env file
dotenv_path = "../.env"
# Load environment variables from the .env file
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

VIDEOSDK_TOKEN = os.getenv("VIDEOSDK_AUTH_TOKEN")
NAME = "VideoSDK Python"


# API call to create a meeting
def create_meeting(token):
    url = "https://api.videosdk.live/v2/rooms"
    headers = {
        "authorization": token,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json={})
    response_data = response.json()
    room_id = response_data.get("roomId")
    return room_id

# Example usage
MEETING_ID = create_meeting(VIDEOSDK_TOKEN)
print("Meeting ID:", MEETING_ID)

loop = asyncio.get_event_loop()

def main():

    meeting_config = MeetingConfig(
        meeting_id=MEETING_ID, name=NAME, mic_enabled=True, webcam_enabled=True, token=VIDEOSDK_TOKEN)

    meeting = VideoSDK.init_meeting(**meeting_config)

    meeting.add_event_listener(MyMeetingEventHandler())

    print("joining into meeting...")

    meeting.join()

    print("joined successfully")


if __name__ == '__main__':
    main()
    loop.run_forever()
