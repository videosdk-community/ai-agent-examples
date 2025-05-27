# PythonSDK

This folder demonstrates the core integration with the VideoSDK Python SDK for real-time audio/video meetings and event handling.

## Files
- **main.py**: Entry point for joining a VideoSDK meeting as a participant using environment variables for authentication. Handles meeting creation and joining.
- **meeting_events.py**: Implements `MyMeetingEventHandler` to handle meeting-level events (join, leave, participant join/leave, errors).
- **participant_events.py**: Implements `MyParticipantEventHandler` to handle participant-level events (stream enabled/disabled, media status, video quality).

## How to Use
1. Set your environment variables in `.env` (see `.env.sample`).
2. Run `main.py` to join a meeting as a participant:
   ```sh
   python main.py
   ```
3. The event handlers will print meeting and participant events to the console.

## Learn More
- [Python SDK Quick Start](https://docs.videosdk.live/python/guide/quick-start/audio-video)
- [AI Agents Docs](https://docs.videosdk.live/ai_agents/introduction)
