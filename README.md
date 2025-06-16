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
  - **Simply run the provided script:**
    ```sh
    cd PythonSDK
    python main.py
    ```
    This will print a new meeting ID in your terminal, ready to use with any agent!

---

## 🐳 Quick Start with Docker (Recommended)

The easiest way to get started is using Docker! No need to install Python or manage dependencies.

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed on your system

### Setup & Run

1. **Clone the repository:**
   ```sh
   git clone https://github.com/videosdk-community/ai-agent-examples.git
   cd ai-agent-examples
   ```

2. **Set up your environment:**
   ```sh
   cp env.sample .env
   # Edit .env with your API keys
   ```

3. **Run any agent with one command:**
   ```sh
   # List all available agents
   ./run.sh list
   
   # Run a specific agent
   ./run.sh celebrity
   ./run.sh aws
   ./run.sh openai
   ./run.sh recruiter
   ./run.sh mcp
   ```

### Alternative Docker Commands

If you prefer using Docker directly:

```sh
# Build the image
docker build -t ai-agent-examples .

# Run any agent
docker run --rm -it --env-file .env ai-agent-examples celebrity
docker run --rm -it --env-file .env ai-agent-examples aws
docker run --rm -it --env-file .env ai-agent-examples openai
docker run --rm -it --env-file .env ai-agent-examples mcp

# List available agents
docker run --rm ai-agent-examples list
```

### Using Docker Compose

```sh
# Build and run with docker-compose
docker-compose build
docker-compose run --rm ai-agent celebrity
docker-compose run --rm ai-agent aws
docker-compose run --rm ai-agent mcp
```

### 🔧 Automatic Dependency Management

Docker automatically installs dependencies from all `requirements.txt` files in the repository:
- Main `requirements.txt` (core dependencies)
- `mcp/requirements.txt` (MCP-specific packages)
- `fuctionTools/requirements.txt` (function tools dependencies)
- Any other `requirements.txt` files you add to subdirectories

No need to manually merge requirements - just add your folder-specific dependencies!

---

## 🌟 Manual Setup (Alternative)

If you prefer to run without Docker:

1. **Clone the repository:**
   ```sh
   git clone https://github.com/videosdk-community/ai-agent-examples.git
   cd ai-agent-examples
   ```
2. **Create your environment file and set up all API keys:**
   ```sh
   cp env.sample .env
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
5. **Update the meeting ID in any agent script** (e.g., `basicAgents/recruiter.py`)
6. **Run your chosen agent:**
   ```sh
   python "basicAgents/recruiter.py"
   # Or try openai.py, gemini.py, aws.py, mcp/mcp.py, etc.
   ```
7. **Join the same meeting from a VideoSDK client app** (Web, Mobile, etc.) to interact with your agent in real time.

---

## Key Features of VideoSDK AI Agents

- 🎤 **Real-time Voice & Media**: Agents can listen, speak, and interact live in meetings.
- 🤖 **Multi-Model Support**: Integrate with OpenAI, Gemini, AWS NovaSonic, and more.
- 🧩 **Pluggable Agent Types**: Includes recruiter, tutor, doctor, storyteller, and more.
- 🛠️ **Function Tools**: Extend agent capabilities with event scheduling, expense tracking, and more (see `fuctionTools/`).
- 🔌 **Easy Integration**: Built on VideoSDK's robust Python SDK.
- 🏗️ **Extensible**: Add your own agents and tools easily.
- 🐳 **Docker Ready**: Run any agent with just one command using Docker.
- 🌐 **MCP Integration**: Connect agents to external data sources and tools using Model Context Protocol.

---

## Example Agents

| Agent Type | Description | File | Docker Command |
|------------|-------------|------|----------------|
| 🎙️ **Basic Voice Agent** | Simple voice assistant with different LLM options | [openai.py](openai.py), [gemini.py](gemini.py), [aws.py](aws.py) | `./run.sh openai` / `./run.sh gemini` / `./run.sh aws` |
| 👩‍💼 **Recruiter** | Conducts screening interviews, evaluates communication skills | [recruiter.py](basicAgents/recruiter.py) | `./run.sh recruiter` |
| 👨‍🏫 **Tutor** | Helps students understand academic concepts | [tutor.py](basicAgents/tutor.py) | `./run.sh tutor` |
| 👨‍⚕️ **Doctor** | Provides general medical guidance (not medical advice) | [doctor.py](basicAgents/doctor.py) | `./run.sh doctor` |
| 📚 **Storyteller** | Creates stories from user keywords in real-time | [storyteller.py](basicAgents/storyteller.py) | `./run.sh storyteller` |
| 👯 **Companion** | Friendly, empathetic AI for casual chat | [companion.py](basicAgents/companion.py) | `./run.sh companion` |
| 🌟 **Celebrity** | Role-plays as famous personalities | [celebrity.py](basicAgents/celebrity.py) | `./run.sh celebrity` |
| 🧘 **Confession** | Nonjudgmental listener for reflection | [confession.py](basicAgents/confession.py) | `./run.sh confession` |
| 🌐 **MCP Agent** | Connects to external data sources and tools using Model Context Protocol | [mcp.py](mcp/mcp.py) | `./run.sh mcp` |
| 🛠️ **Agents with Function Tools** | Agents that can schedule events, track expenses, or take notes using [fuctionTools](fuctionTools/) | See [fuctionTools/README.md](fuctionTools/README.md) | Manual setup required |

---

## Folder Structure & Use Cases

- **basicAgents**: Ready-to-use AI agents for recruiter, tutor, doctor, storyteller, companion, celebrity, and more. Each agent is a Python script you can run directly.
- **pythonSDK**: Core VideoSDK Python integration, including meeting and participant event handlers. Start here to understand the SDK basics and generate meeting IDs.
- **fuctionTools**: Utility tools for agents, such as brain dump, event scheduler, and expense tracker. Integrate these with your agents for advanced workflows.
- **mcp**: Model Context Protocol agents that connect to external data sources and tools. Includes example MCP servers and integration patterns.
- **aws.py, openai.py, gemini.py**: Example scripts for running a basic agent with AWS, OpenAI, or Gemini models.

---

## Why Choose VideoSDK AI Agents?

- **Production-Ready**: Built on a scalable, real-time platform trusted by thousands of developers.
- **Flexible**: Mix and match LLMs, agent types, and tools for your unique use case.
- **Docker-First**: Easy deployment and testing with containerized environments.

---

## Documentation & Resources
- [AI Agents Docs](https://docs.videosdk.live/ai_agents/introduction)
- [Python SDK Quick Start](https://docs.videosdk.live/python/guide/quick-start/audio-video)
- [VideoSDK Dashboard](https://app.videosdk.live/)
- [Community Discord](https://discord.gg/Gpmj6eCq5u)

---

## Contributing
Pull requests and new agent ideas are welcome!

