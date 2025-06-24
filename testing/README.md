<!--BEGIN_BANNER_IMAGE-->
<p align="center">
  <img src="https://raw.githubusercontent.com/videosdk-live/agents/main/.github/banner.png" alt="VideoSDK AI Agents Banner" style="width:100%;">
</p>
<!--END_BANNER_IMAGE-->

# VideoSDK AI Agents
The Easiest way to Build a Enterprise Grade AI Voice Agents.

![PyPI - Version](https://img.shields.io/pypi/v/videosdk-agents)
[![PyPI Downloads](https://static.pepy.tech/badge/videosdk-agents/month)](https://pepy.tech/projects/videosdk-agents)
[![Twitter Follow](https://img.shields.io/twitter/follow/video_sdk)](https://x.com/video_sdk)
[![YouTube](https://img.shields.io/badge/YouTube-VideoSDK-red)](https://www.youtube.com/c/VideoSDK)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-VideoSDK-blue)](https://www.linkedin.com/company/video-sdk/)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA)](https://discord.com/invite/f2WsNDN9S5)

## Overview

The AI Agent SDK is a Python framework built on top of the VideoSDK Python SDK that enables AI-powered agents to join VideoSDK rooms as participants. This SDK serves as a real-time bridge between AI models (like OpenAI and Gemini) and your users, facilitating seamless voice and media interactions.

## Features

- **🎤 Real-time Voice & Media**: Agents can listen, speak, and interact live in meetings.
- **📞 SIP & Telephony Integration**: Seamlessly connect agents to phone systems via SIP for call handling, routing, and PSTN access.
- **🤖 Multi-Model Support**: Integrate with OpenAI, Gemini, AWS NovaSonic, and more.
- **🧩 Cascading Pipeline**: Integrates with different providers of STT, LLM and TTS seamlessly.
- **🧠 Conversational Flow**: Manages turn detection and VAD for smooth interactions.
- **🛠️ Function Tools**: Extend agent capabilities with event scheduling, expense tracking, and more.
- **🌐 MCP Integration**: Connect agents to external data sources and tools using Model Context Protocol.
- **🔗 A2A Protocol**: Enable agent-to-agent interactions for complex workflows.

> \[!IMPORTANT]
>
> **Star VideoSDK Repositories** ⭐️
>
> Get instant notifications for new releases and updates. Your support helps us grow and improve VideoSDK!

## Introduction

### ⚙️ System Components
- **🖥️ Your Backend:** Hosts the Worker and Agent Job that powers the AI agents
- **☁️ VideoSDK Cloud:** Manages the meeting rooms where agents and users interact in real time
- **📱 Client SDK:** Applications on user devices (web, mobile, or SIP) that connect to VideoSDK meetings

### 🔄 Process Flow
1. **📝 Register:** Your backend worker registers with the VideoSDK Cloud
2. **📲 Initiate to join Room:** The user initiates joining a VideoSDK Room via the Client SDK on their device
3. **📡 Notify worker for Agent to join Room:** The VideoSDK Cloud notifies your backend worker to have an Agent join the room.
4. **🤖 Agent joins the room:** The Agent connects to the VideoSDK Room and can interact with the user.

## 🚀 Before You Begin

Before you begin, ensure you have:

- A VideoSDK authentication token (generate from [app.videosdk.live](https://app.videosdk.live))
- - A VideoSDK meeting ID (you can generate one using the [Create Room API](https://docs.videosdk.live/api-reference/realtime-communication/create-room) or through the VideoSDK dashboard)
- Python 3.12 or higher
- Third-Party API Keys:
- - API keys for the services you intend to use (e.g., OpenAI for LLM/STT/TTS, ElevenLabs for TTS, Google for Gemini etc.).

## Installation

- Create and activate a virtual environment with Python 3.12 or higher.
    <details>
    <summary><strong>💻 macOS / Linux</strong></summary>
    
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    </details> 
    <details> 
    <summary><strong>🪟 Windows</strong></summary>
    
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
    </details>
    
- Install the core VideoSDK AI Agent package 
  ```bash
  pip install videosdk-agents
  ```
- Install Optional Plugins. Plugins help integrate different providers for Realtime, STT, LLM, TTS, and more. Install what your use case needs:
  ```bash
  # Example: Install the Turn Detector plugin
  pip install videosdk-plugins-turn-detector
  ```
  👉 Supported plugins (Realtime, LLM, STT, TTS, VAD) are listed in the [Supported Libraries](#supported-libraries-and-plugins) section below.


## 🏁 Getting Started: Your First Agent

Now that you've installed the necessary packages, you're ready to build!

- For detailed guides, tutorials, and API references, check out our official [VideoSDK AI Agents Documentation](https://docs.videosdk.live/ai_agents/introduction).
- To see the framework in action, explore the code in the [Examples](examples/) directory. It is a great place to quickstart.


## Architecture

This architecture shows how AI voice agents connect to VideoSDK meetings. The system links your backend with VideoSDK's platform, allowing AI assistants to interact with users in real-time.
![VideoSDK AI Agents High Level Architecture](https://strapi.videosdk.live/uploads/architecture_2_3fba73f24a.svg)

## Supported Libraries and Plugins

The framework supports integration with various AI models and tools, including:

| **Provider** | **Real-time** | **Speech-to-Text (STT)** | **Language Models (LLM)** | **Text-to-Speech (TTS)** | **Voice Activity Detection (VAD)** |
|--------------|:-------------:|:-------------------------:|:--------------------------:|:-------------------------:|:----------------------------------:|
| **OpenAI** | [OpenAIRealtime](https://docs.videosdk.live/ai_agents/plugins/realtime/openai) | [OpenAISTT](https://docs.videosdk.live/ai_agents/plugins/stt/openai) | [OpenAILLM](https://docs.videosdk.live/ai_agents/plugins/llm/openai) | [OpenAITTS](https://docs.videosdk.live/ai_agents/plugins/tts/openai) | ✖️ |
| **Google** | [GeminiRealtime](https://docs.videosdk.live/ai_agents/plugins/realtime/google-live-api) | [GoogleSTT](https://docs.videosdk.live/ai_agents/plugins/stt/google) | [GoogleLLM](https://docs.videosdk.live/ai_agents/plugins/llm/google) | [GoogleTTS](https://docs.videosdk.live/ai_agents/plugins/tts/google) | ✖️ |
| **AWS** | [AWSNovaSonic](https://docs.videosdk.live/ai_agents/plugins/realtime/aws-nova-sonic) | ✖️ | ✖️ | ✖️ | ✖️ |
| **Sarvam** | ✖️ | [SarvamSTT](https://docs.videosdk.live/ai_agents/plugins/stt/sarvam-ai) | [SarvamLLM](https://docs.videosdk.live/ai_agents/plugins/llm/sarvam-ai) | [SarvamTTS](https://docs.videosdk.live/ai_agents/plugins/tts/sarvam-ai) | ✖️ |
| **Deepgram** | ✖️ | [DeepgramSTT](https://docs.videosdk.live/ai_agents/plugins/stt/deepgram) | ✖️ | ✖️ | ✖️ |
| **ElevenLabs** | ✖️ | ✖️ | ✖️ | [ElevenLabsTTS](https://docs.videosdk.live/ai_agents/plugins/tts/elevenlabs) | ✖️ |
| **Silero VAD** | ✖️ | ✖️ | ✖️ | ✖️ | [SileroVAD](https://docs.videosdk.live/ai_agents/plugins/vad/silero) |

## Examples

Explore the following examples to see the framework in action:

<table>
  <tr>
    <td width="50%">
      <h3>🎙️ <a href="examples/openai.py">Basic Voice Agent</a></h3>
      <p>Simple voice assistant with different LLM options.</p>
    </td>
    <td width="50%">
      <h3>👩‍💼 <a href="examples/recruiter.py">Recruiter</a></h3>
      <p>Conducts screening interviews, evaluates communication skills.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>👨‍🏫 <a href="examples/tutor.py">Tutor</a></h3>
      <p>Helps students understand academic concepts.</p>
    </td>
    <td width="50%">
      <h3>👨‍⚕️ <a href="examples/doctor.py">Doctor</a></h3>
      <p>Provides general medical guidance (not medical advice).</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>📚 <a href="examples/storyteller.py">Storyteller</a></h3>
      <p>Creates stories from user keywords in real-time.</p>
    </td>
    <td width="50%">
      <!-- Empty cell for symmetry, add more examples if needed -->
    </td>
  </tr>
</table>


## Contributing

The Agents framework is under active development in a rapidly evolving field. We welcome and appreciate contributions of any kind, be it feedback, bugfixes, features, new plugins and tools, or better documentation. You can file issues under this repo, open a PR, or chat with us in VideoSDK's [Discord community](https://discord.com/invite/f2WsNDN9S5).


When contributing, consider developing new plugins or enhancing existing ones to expand the framework's capabilities. Your contributions can help integrate more AI models and tools, making the framework even more versatile.

We love our contributors! Here's how you can contribute:

- [Open an issue](https://github.com/videosdk-live/agents/issues) if you believe you've encountered a bug.
- Follow the [documentation guide](https://docs.videosdk.live/ai_agents/introduction) to get your local dev environment set up.
- Make a [pull request](https://github.com/videosdk-live/agents/pull) to add new features/make quality-of-life improvements/fix bugs.

<a href="https://github.com/videosdk-live/agents/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=videosdk-live/agents" />
</a>

## Repo Activity

![Agents repo activity – generated by Axiom]https://repobeats.axiom.co/api/embed/6ac4c94a89ea20e2e10032b932a128b6d8442e66.svg "Repobeats analytics image"
