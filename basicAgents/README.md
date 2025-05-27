# Basic Agents

This folder contains ready-to-use AI agent scripts, each designed for a specific real-time conversational use case. All agents leverage VideoSDK’s AI Agent SDK and can join meetings as participants.

## API Key Setup
- Before running any agent, ensure you have set up your `.env` file with all required API keys:
  - `VIDEOSDK_AUTH_TOKEN` (from VideoSDK dashboard)
  - `OPENAI_API_KEY` (for OpenAI agents)
  - `GOOGLE_API_KEY` (for Gemini/Google agents)
  - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` (for AWS NovaSonic agents)

## Easily Switch LLM Models
- All agent scripts (e.g., `recruiter.py`, `tutor.py`, etc.) allow you to switch between OpenAI, Gemini, and AWS NovaSonic models.
- To change the model, simply comment or uncomment the relevant code block in the script. For example:
  - Use the Gemini section for Google Gemini
  - Uncomment the OpenAI or AWS section to use those providers
- This makes it easy to experiment with different LLMs for the same agent logic.

## Included Agents
- **recruiter.py**: Conducts screening interviews, gathers candidate info, and evaluates communication skills.
- **tutor.py**: Acts as a patient, interactive tutor for academic topics.
- **doctor.py**: Provides general medical guidance (not a substitute for real doctors).
- **storyteller.py**: Instantly crafts creative stories from user-provided keywords.
- **companion.py**: Friendly, empathetic AI for casual chat and emotional support.
- **celebrity.py**: Role-plays as famous personalities in real time.
- **confession.py**: Listens like a therapist or confessor, offering a safe, nonjudgmental space.

## How to Use
1. Set your `MEETING_ID` in the script or via environment variables.
2. Run the agent script:
   ```sh
   python recruiter.py
   ```
3. The agent will join your VideoSDK meeting and interact live.

## Customization
- Each agent’s behavior is defined by its `instructions` in the script.
- You can add new agents by copying a script and editing the instructions and logic.

---

For more, see the [AI Agents Docs](https://docs.videosdk.live/ai_agents/introduction).
