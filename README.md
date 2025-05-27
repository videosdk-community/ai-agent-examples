# AI Agent Examples

![VideoSDK AI Agents High Level Architecture](https://cdn.videosdk.live/website-resources/docs-resources/ai_agents_high_level_diagram_compressed.png)

## Build Real-Time Conversational AI Agents with VideoSDK (Python)

**AI Agent Examples** is your all-in-one Python starter kit for building, customizing, and deploying real-time AI voice agents using [VideoSDK](https://videosdk.live/). Leverage the power of OpenAI, Gemini, AWS NovaSonic, and more to create interactive, intelligent assistants for meetings, support, education, and beyond.

---

## 🚀 Before You Begin

To get started, make sure you have:

- **A VideoSDK authentication token**
  - Sign up or log in at [VideoSDK Dashboard](https://app.videosdk.live/)
  - Go to **API Keys** and generate a new token
  - Copy the token and add it to your `.env` file as `VIDEOSDK_AUTH_TOKEN`
- **API keys for LLM providers and Google integrations**
  - **OpenAI:** Add your OpenAI API key as `OPENAI_API_KEY` in `.env`
  - **Google:** Add your Google API key as `GOOGLE_API_KEY` in `.env` (required for Gemini and Google function tools)
  - **AWS:** Add your AWS credentials as `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION` in `.env` (for AWS NovaSonic agents)
- **A VideoSDK meeting ID**
  - You can generate a meeting ID using the [Create Room API](https://docs.videosdk.live/api-reference/rooms/create-room) or directly from the dashboard
  - **Or, simply run the provided script:**
    ```sh
    cd PythonSDK
    python main.py
    ```
    This will print a new meeting ID in your terminal, ready to use with any agent!

---

## Key Features of VideoSDK AI Agents

- 🎤 **Real-time Voice & Media**: Agents can listen, speak, and interact live in meetings.
- 🤖 **Multi-Model Support**: Integrate with OpenAI, Gemini, AWS NovaSonic, and more.
- 🧩 **Pluggable Agent Types**: Includes recruiter, tutor, doctor, storyteller, and more.
- 🛠️ **Function Tools**: Extend agent capabilities with event scheduling, expense tracking, and more (see `fuctionTools/`).
- 🔌 **Easy Integration**: Built on VideoSDK's robust Python SDK.
- 🏗️ **Extensible**: Add your own agents and tools easily.

---

## 🌟 Quick Start Guide

1. **Clone the repository:**
   ```sh
   git clone https://github.com/<your-username>/ai-agent-examples.git
   cd ai-agent-examples
   ```
2. **Create your environment file and set up all API keys:**
   ```sh
   cp .env.sample .env
   ```
3. **Set up a Python environment and install dependencies:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Generate a meeting ID:**
   ```sh
   cd PythonSDK
   python main.py
   # Copy the printed meeting ID
   ```
5. **Update the meeting ID in any agent script** (e.g., `Basic Agents/recruiter.py`)
6. **Run your chosen agent:**
   ```sh
   python "basicAgents/recruiter.py"
   # Or try openai.py, gemini.py, aws.py, etc.
   ```
7. **Join the same meeting from a VideoSDK client app** (Web, Mobile, etc.) to interact with your agent in real time.

---

## Example Agents

| Agent Type | Description | File |
|------------|-------------|------|
| 🎙️ **Basic Voice Agent** | Simple voice assistant with different LLM options | [openai.py](openai.py), [gemini.py](gemini.py), [aws.py](aws.py) |
| 👩‍💼 **Recruiter** | Conducts screening interviews, evaluates communication skills | [recruiter.py](Basic%20Agents/recruiter.py) |
| 👨‍🏫 **Tutor** | Helps students understand academic concepts | [tutor.py](Basic%20Agents/tutor.py) |
| 👨‍⚕️ **Doctor** | Provides general medical guidance (not medical advice) | [doctor.py](Basic%20Agents/doctor.py) |
| 📚 **Storyteller** | Creates stories from user keywords in real-time | [storyteller.py](Basic%20Agents/storyteller.py) |
| 👯 **Companion** | Friendly, empathetic AI for casual chat | [companion.py](Basic%20Agents/companion.py) |
| 🌟 **Celebrity** | Role-plays as famous personalities | [celebrity.py](Basic%20Agents/celebrity.py) |
| 🧘 **Confession** | Nonjudgmental listener for reflection | [confession.py](Basic%20Agents/confession.py) |
| 🛠️ **Agents with Function Tools** | Agents that can schedule events, track expenses, or take notes using [fuctionTools/](fuctionTools/) | See [fuctionTools/README.md](fuctionTools/README.md) |

---

## Folder Structure & Use Cases

- **basicAgents/**: Ready-to-use AI agents for recruiter, tutor, doctor, storyteller, companion, celebrity, and more. Each agent is a Python script you can run directly.
- **pythonSDK/**: Core VideoSDK Python integration, including meeting and participant event handlers. Start here to understand the SDK basics and generate meeting IDs.
- **fuctionTools/**: Utility tools for agents, such as brain dump, event scheduler, and expense tracker. Integrate these with your agents for advanced workflows.
- **aws.py, openai.py, gemini.py**: Example scripts for running a basic agent with AWS, OpenAI, or Gemini models.

---

## Why Choose VideoSDK AI Agents?

- **Production-Ready**: Built on a scalable, real-time platform trusted by thousands of developers.
- **Flexible**: Mix and match LLMs, agent types, and tools for your unique use case.

---

## Documentation & Resources
- [AI Agents Docs](https://docs.videosdk.live/ai_agents/introduction)
- [Python SDK Quick Start](https://docs.videosdk.live/python/guide/quick-start/audio-video)
- [VideoSDK Dashboard](https://app.videosdk.live/)
- [Community Discord](https://discord.gg/Gpmj6eCq5u)

---

## Contributing
Pull requests and new agent ideas are welcome!

