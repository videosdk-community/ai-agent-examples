# Adding New Agents

## 🚀 How to Add New Agents

The Docker setup automatically detects and makes available any Python files that could be agents. Here's how it works:

### 📁 Supported Locations

The system automatically scans these locations for agents:

1. **Root directory** - Any `.py` file (except `__init__.py`)
2. **`basicAgents/` directory** - Any `.py` file in this folder
3. **Any other directory** - Any `.py` file in subdirectories (except `venv/`, `__pycache__/`)

### ✨ Adding a New Agent

Simply create a new Python file following the existing pattern:

```python
import asyncio
from videosdk.agents import Agent, AgentSession, RealTimePipeline

# Set your meeting ID
MEETING_ID = "your_generated_meeting_id"

class MyNewAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            Your agent instructions here...
            """,
        )

    async def on_enter(self) -> None:
        await self.session.say("Hello from your new agent!")
    
    async def on_exit(self) -> None:
        await self.session.say("Goodbye!")

async def main(context: dict):
    # Choose your model (OpenAI, Gemini, AWS, etc.)
    model = GeminiRealtime(
        model="gemini-2.0-flash-live-001",
        config=GeminiLiveConfig(
            voice="Leda",
            response_modalities=["AUDIO"]
        )
    )

    pipeline = RealTimePipeline(model=model)
    session = AgentSession(
        agent=MyNewAgent(),
        pipeline=pipeline,
        context=context
    )

    try:
        await session.start()
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await session.close()

if __name__ == "__main__":
    def make_context():
        return {
            "meetingId": MEETING_ID, 
            "name": "My New Agent", 
        }
    
    asyncio.run(main(context=make_context()))
```

### 🎯 File Naming Convention

- Use descriptive names: `translator.py`, `customer_service.py`, `interviewer.py`
- Avoid generic names like `agent.py`, `main.py`, `utils.py`
- The filename (without `.py`) becomes the command to run the agent

### 📦 Dependencies Management

**For Docker users:**
- Docker automatically finds and installs all `requirements.txt` files from any subdirectory
- No need to manually merge requirements - just add your folder-specific `requirements.txt`
- The system will install dependencies from:
  - Root `requirements.txt`
  - `mcp/requirements.txt`
  - `fuctionTools/requirements.txt`
  - Any other `requirements.txt` files you add

**For manual setup:**
- Add your dependencies to the main `requirements.txt` file
- Or install folder-specific requirements manually: `pip install -r folder/requirements.txt`

### 🔍 Auto-Detection Features

The system automatically:

1. **Scans all directories** for Python files
2. **Excludes system files** like `__init__.py`, `__pycache__/`, `venv/`
3. **Lists all available agents** when you run `./run.sh list`
4. **Validates agent names** before running
5. **Finds agents in any subdirectory** structure
6. **Installs all dependencies** from any `requirements.txt` files

### 📝 Example: Adding a Translator Agent

1. Create `basicAgents/translator.py` (as shown above)
2. The agent is automatically detected
3. Run it with: `./run.sh translator`

### 🐳 Docker Integration

When you add a new agent:

1. **No Dockerfile changes needed** - The auto-detection handles everything
2. **No script updates required** - The `run.sh` script automatically finds new agents
3. **Automatic dependency installation** - All `requirements.txt` files are automatically installed
4. **Works immediately** - Just rebuild the Docker image if needed:
   ```bash
   ./run.sh build
   ./run.sh your_new_agent
   ```

### 🧪 Testing New Agents

1. **List all agents**: `./run.sh list`
2. **Test your agent**: `./run.sh your_agent_name`
3. **Check for errors**: The system will tell you if the agent file is not found

### 📋 Best Practices

1. **Follow the existing pattern** - Use the same structure as other agents
2. **Include proper imports** - Add dependencies to your folder's `requirements.txt` if needed
3. **Add clear instructions** - Write detailed agent instructions
4. **Test thoroughly** - Make sure your agent works before committing
5. **Update documentation** - Add your agent to the README if it's a major addition

### 🔧 Troubleshooting

If your agent isn't detected:

1. **Check the filename** - Make sure it ends with `.py`
2. **Verify the location** - Put it in `basicAgents/` or root directory
3. **Check for syntax errors** - Python files with errors might not be detected
4. **Rebuild Docker image** - Run `./run.sh build` to ensure changes are included
5. **Check dependencies** - Ensure all required packages are in a `requirements.txt` file

The auto-detection system makes it super easy to add new agents without any configuration changes! 