# VideoSDK AI Voice Agent

This project demonstrates how to build an AI-powered voice agent using the [VideoSDK Agents SDK](https://docs.videosdk.live). The agent can join a VideoSDK meeting and perform various roles.

---

## 🚀 Features

- 🎙 Real-time voice interaction in VideoSDK meetings.
- 👤 Configurable agent personas.
- 🎯 Server-side Voice Activity Detection (VAD) for natural turn-taking.
- 🛠 Easily extendable with new prompts and behaviors.

---

## 📋 Prerequisites

- Python 3.11+
- `pip` (Python package installer)
- [VideoSDK Account](https://videosdk.live/) (for API Key/Secret and meetings)
- [OpenAI Account](https://openai.com/product) (for API Key)

---

## ⚙️ Setup Instructions

### 1. Clone the Repository (Optional)

```bash
git clone <your-repository-url>
cd <repository-name>
```

Or ensure you have `agent.py`, `prompts.py`, and `requirements.txt` in your working directory.

### 2. Create and Activate a Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Tokens

Navigate to `agent.py` and set variables:

```agent.py
api_key="<YOUR_OPENAI_API_KEY>"
```

Replace the placeholders with your actual API keys.

---

## 🔧 Configuration

### 1. Select a Use Case

In `agent.py`, set the `usecase` variable:

```python
usecase = "Companion"  # Change to "Doctor", "Tutor", etc.
```

Use cases are defined in `prompts.py`.

### 2. Meeting Configuration

Edit the `make_context` function in `agent.py`:

```python
def make_context():
    return {
        "meetingId": "your-actual-meeting-id",  # Replace with actual ID
        "name": "VideoSDK's AI Agent",
        "videosdk_auth": "your-auth-token",
    }
```

---

## ▶️ Running the Agent

1. Activate your virtual environment.
2. Ensure the variables are properly set.
3. Run:

```bash
python agent.py
```

You should see logs like:

```
Agent ... has entered the meeting
```

---

## ➕ Adding New Use Cases

### 1. Define the Prompt

Edit `prompts.py`:

```python
PROMPTS = {
    "YourNewUseCaseName": '''
    You are an AI [role description].
    - Your primary goal is to [goal].
    - Behave in [manner].
    - Specific instruction 1.
    - Specific instruction 2.
    ''',
}
```

### 2. Select the New Use Case

In `agent.py`:

```python
usecase = "YourNewUseCaseName"
```

---

```python
return {
    "meetingId": "...",
    "name": "Agent",
    "videosdk_auth": "your_pregenerated_auth_token"
}
```

---

## 📁 Project Files

- `prompting.py`: Main agent runner script.
- `prompts.py`: Defines prompts per use case.
- `requirements.txt`: Lists Python dependencies.

---

Happy hacking! 🎉
