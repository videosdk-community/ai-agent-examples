import asyncio
import os
import logging
import functools
from contextlib import asynccontextmanager, suppress
from typing import Optional, Dict, Any, Type, Callable
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
import uvicorn
from pyngrok import ngrok
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Dial
import httpx

# VideoSDK imports
from videosdk.agents import JobContext, RoomOptions, WorkerJob, AgentSession, CascadingPipeline, Agent

# Local imports
from agents.customer_agent import SIPCustomerServiceAgent
from agents.loan_agent import SIPLoanSpecialistAgent
from session_manager import create_pipeline, create_session

# Load environment variables
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Also set verbose logging for VideoSDK agents
logging.getLogger("videosdk").setLevel(LOG_LEVEL)
logging.getLogger("agents").setLevel(LOG_LEVEL)

logger.info(f"🔧 Logging configured at level: {LOG_LEVEL}")

# Check required environment variables
def check_environment():
    """Check if all required environment variables are set."""
    required_vars = {
        "VIDEOSDK_AUTH_TOKEN": "VideoSDK authentication token",
        "VIDEOSDK_SIP_USERNAME": "VideoSDK SIP username", 
        "VIDEOSDK_SIP_PASSWORD": "VideoSDK SIP password",
        "GOOGLE_API_KEY": "Google API key for Gemini realtime model", 
        "OPENAI_API_KEY": "OpenAI API key for text processing",
        "TWILIO_ACCOUNT_SID": "Twilio account SID",
        "TWILIO_AUTH_TOKEN": "Twilio auth token",
        "TWILIO_PHONE_NUMBER": "Twilio phone number"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  ❌ {var}: {description}")
    
    if missing_vars:
        logger.error("❌ Missing required environment variables:")
        for var in missing_vars:
            logger.error(var)
        logger.error("Please set these in your .env file before running.")
        return False
    else:
        logger.info("✅ All required environment variables are set")
        return True

# Check environment at startup
if not check_environment():
    exit(1)

# Global state for managing active sessions
active_sessions: Dict[str, Dict[str, Any]] = {}

# Configuration
HUMAN_SUPPORT_NUMBER = os.getenv("HUMAN_SUPPORT_NUMBER", "+918200367305")

def on_pubsub_message(message):
    """Handle pubsub messages."""
    logger.info(f"Pubsub message received: {message}")

# Removed DefaultConversationFlow - using SIPConversationFlow from session_manager instead

async def _agent_entrypoint(ctx: JobContext):
    """
    The main entrypoint for a single call.
    This function creates and runs BOTH the customer and specialist agents
    for the duration of a single SIP call, ensuring they can communicate via A2A.
    This follows the pattern from the working examples/a2a/main.py.
    """
    room_id = ctx.room_options.room_id
    call_id = getattr(ctx, 'call_id', 'N/A')
    logger.info(f"[{room_id}] 📞 Starting agent entrypoint for call {call_id}")

    specialist_session: Optional[AgentSession] = None
    customer_session: Optional[AgentSession] = None
    specialist_task: Optional[asyncio.Task] = None
    
    # Create an event to track when the participant leaves
    participant_left_event = asyncio.Event()

    # Handler for participant left events
    def on_participant_left(participant_id):
        logger.info(f"[{room_id}] 👤 Participant {participant_id} left. Setting event to end call.")
        participant_left_event.set()

    try:
        # 1. Create Specialist Agent
        logger.info(f"[{room_id}] 🏦 Creating Loan Specialist Agent...")
        specialist_agent = SIPLoanSpecialistAgent()
        specialist_pipeline = create_specialist_pipeline()
        specialist_session = create_session(specialist_agent, specialist_pipeline)
        logger.info(f"[{room_id}] ✅ Specialist agent created.")

        # 2. Create Customer Agent
        logger.info(f"[{room_id}] 👤 Creating Customer Service Agent...")
        customer_agent = SIPCustomerServiceAgent(ctx=ctx)
        customer_pipeline = create_customer_pipeline()
        customer_session = create_session(customer_agent, customer_pipeline)
        logger.info(f"[{room_id}] ✅ Customer agent created.")

        # 3. Start Specialist Agent in the background
        logger.info(f"[{room_id}] 🚀 Starting specialist agent session in background...")
        specialist_task = asyncio.create_task(specialist_session.start())
        # Give a moment for it to start and register for A2A
        await asyncio.sleep(1)
        logger.info(f"[{room_id}] ✅ Specialist agent session started.")

        # 4. Connect to the room and start the Customer Agent
        logger.info(f"[{room_id}] 🔗 Connecting to VideoSDK room...")
        await ctx.connect()
        
        # Register for participant_left events
        if hasattr(ctx.room, 'meeting') and hasattr(ctx.room.meeting, 'on'):
            ctx.room.meeting.on('participant-left', on_participant_left)
            logger.info(f"[{room_id}] 📡 Registered for participant-left events")
        
        logger.info(f"[{room_id}] 🚀 Starting customer agent session...")
        await customer_session.start()
        logger.info(f"[{room_id}] ✅ Customer agent session started.")

        # 5. Wait for the call to proceed
        logger.info(f"[{room_id}] 🎧 Agents are running. Waiting for participant...")
        participant_id = await ctx.room.wait_for_participant()
        logger.info(f"[{room_id}] 👤 Participant {participant_id} joined.")
        
        await customer_agent.greet_user()
        logger.info(f"[{room_id}] 👋 User greeted.")
        
        # Keep the process alive until the call ends (participant leaves or timeout)
        logger.info(f"[{room_id}] ⏱️ Waiting for call to end...")
        try:
            # Add a long timeout as safety net (4 hours max call)
            await asyncio.wait_for(participant_left_event.wait(), timeout=14400)
            logger.info(f"[{room_id}] 📞 Call ended naturally.")
        except asyncio.TimeoutError:
            logger.info(f"[{room_id}] ⏰ Maximum call time reached, ending call.")

    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info(f"[{room_id}] 🛑 Entrypoint cancelled.")
    except Exception as e:
        logger.error(f"[{room_id}] 💥 EXCEPTION in agent job: {e}", exc_info=True)
    finally:
        logger.info(f"[{room_id}] 🧼 Cleaning up resources for call {call_id}...")
        
        # Gracefully shut down the specialist task
        if specialist_task and not specialist_task.done():
            specialist_task.cancel()
            with suppress(asyncio.CancelledError):
                await specialist_task
                logger.info(f"[{room_id}] ✅ Specialist task cancelled.")

        # Close sessions
        if specialist_session:
            await specialist_session.close()
            logger.info(f"[{room_id}] ✅ Specialist session closed.")
        if customer_session:
            await customer_session.close()
            logger.info(f"[{room_id}] ✅ Customer session closed.")

        # Shutdown the connection context
        await ctx.shutdown()
        logger.info(f"[{room_id}] ✅ Context shut down.")
        
        # Properly clean up room (fix for warning about un-awaited coroutine)
        if hasattr(ctx, 'room') and ctx.room:
            try:
                # First leave the meeting if possible
                if hasattr(ctx.room, 'leave'):
                    ctx.room.leave()
                # Then properly await the cleanup coroutine
                if hasattr(ctx.room, 'cleanup'):
                    await ctx.room.cleanup()
                logger.info(f"[{room_id}] ✅ Room cleanup complete.")
            except Exception as e:
                logger.error(f"[{room_id}] ❌ Error during room cleanup: {e}")
        
        # Clean up from active sessions registry
        if call_id in active_sessions:
            active_sessions.pop(call_id, None)
            logger.info(f"[{room_id}] ✅ Removed from active sessions.")

def _make_context(room_id: str, room_name: str, call_id: Optional[str] = None, caller_number: Optional[str] = None) -> JobContext:
    """Create context for agent job (following SIP plugin pattern)."""
    ctx = JobContext(room_options=RoomOptions(room_id=room_id, name=room_name, playground=True))
    if call_id:
        ctx.call_id = call_id
    if caller_number:
        ctx.caller_number = caller_number
    return ctx

def launch_agent_job(
    room_id: str,
    agent_config: Optional[Dict[str, Any]] = None,
    call_id: Optional[str] = None,
    caller_number: Optional[str] = None,
) -> WorkerJob:
    """Creates and starts a WorkerJob for a single call, running both agents."""
    logger.info(f"🏭 Launching agent job for room {room_id}, call {call_id}")
    
    if agent_config is None:
        agent_config = {}
    
    logger.info(f"🏗️  Creating context factory partial for room {room_id}")
    context_factory_partial = functools.partial(
        _make_context,
        room_id=room_id,
        room_name=agent_config.get("room_name", "AI Call"),
        call_id=call_id,
        caller_number=caller_number
    )
    
    logger.info(f"⚡ Creating WorkerJob with entrypoint: _agent_entrypoint")
    job = WorkerJob(entrypoint=_agent_entrypoint, jobctx=context_factory_partial)
    
    logger.info(f"🚀 Starting WorkerJob...")
    job.start()
    
    logger.info(f"✅ WorkerJob started successfully for room {room_id}")
    return job

class VideoSDKMeeting:
    """Service for managing VideoSDK rooms."""
    
    def __init__(self, auth_token: str):
        self.auth_token = auth_token
        self.base_url = "https://api.videosdk.live/v2"

    async def create_room(self) -> str:
        """Create a new VideoSDK room."""
        url = f"{self.base_url}/rooms"
        headers = {"Authorization": self.auth_token}
        payload = {}
        
        region = os.getenv("VIDEOSDK_REGION")
        if region:
            payload["geoFence"] = region
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                room_id = response.json().get("roomId")
                if not room_id:
                    raise ValueError("roomId not found in response")
                return room_id
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error creating room: {e.response.status_code} - {e.response.text}")
                raise Exception("Failed to create VideoSDK room")

    def get_sip_endpoint(self, room_id: str) -> str:
        """Get SIP endpoint for a room."""
        return f"sip:{room_id}@sip.videosdk.live"

    def get_sip_credentials(self) -> Dict[str, str]:
        """Get SIP credentials."""
        username = os.getenv("VIDEOSDK_SIP_USERNAME")
        password = os.getenv("VIDEOSDK_SIP_PASSWORD")
        if not username or not password:
            raise ValueError("VIDEOSDK_SIP_USERNAME and VIDEOSDK_SIP_PASSWORD must be set")
        return {"username": username, "password": password}

class TwilioManager:
    """Direct Twilio integration without the plugin."""
    
    def __init__(self):
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.videosdk = VideoSDKMeeting(os.getenv("VIDEOSDK_AUTH_TOKEN"))
        self.base_url = None

    def set_base_url(self, base_url: str):
        """Set the base URL for webhooks."""
        self.base_url = base_url
        logger.info(f"Base URL set: {self.base_url}")

    async def make_call(self, to_number: str) -> Dict[str, Any]:
        """Make an outgoing call."""
        try:
            logger.info(f"Creating VideoSDK room for call to {to_number}")
            room_id = await self.videosdk.create_room()
            logger.info(f"VideoSDK room created: {room_id}")
            
            webhook_url = f"{self.base_url}/sip/answer/{room_id}"
            logger.info(f"Making Twilio call to {to_number} with webhook {webhook_url}")
            
            call = self.client.calls.create(
                to=to_number,
                from_=self.from_number,
                url=webhook_url
            )
            
            logger.info(f"Twilio call created - SID: {call.sid}, Status: {call.status}")
            
            return {
                "sid": call.sid,
                "status": call.status,
                "room_id": room_id
            }
        except Exception as e:
            logger.error(f"Error making call: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}

    def handle_incoming_call(self, webhook_data: Dict[str, Any], room_id: str) -> tuple:
        """Handle incoming call and return TwiML response."""
        try:
            sip_endpoint = self.videosdk.get_sip_endpoint(room_id)
            sip_creds = self.videosdk.get_sip_credentials()
            
            response = VoiceResponse()
            response.say("Please wait while we connect you to our customer service.", voice='alice')
            dial = Dial(answer_on_bridge=True)
            dial.sip(sip_endpoint, username=sip_creds["username"], password=sip_creds["password"])
            response.append(dial)
            
            xml_response = str(response)
            logger.info(f"Responding with TwiML: {xml_response}")
            return xml_response, 200, {"Content-Type": "application/xml"}
            
        except Exception as e:
            logger.error(f"Error handling incoming call: {e}", exc_info=True)
            return "An error occurred", 500, {"Content-Type": "text/plain"}

    def get_sip_response_for_room(self, room_id: str) -> tuple:
        """Generate SIP response for a room."""
        try:
            logger.info(f"Generating SIP response for room: {room_id}")
            sip_endpoint = self.videosdk.get_sip_endpoint(room_id)
            sip_creds = self.videosdk.get_sip_credentials()
            
            logger.info(f"SIP endpoint: {sip_endpoint}")
            logger.info(f"SIP credentials: username={sip_creds['username']}")
            
            response = VoiceResponse()
            dial = Dial(answer_on_bridge=True)
            dial.sip(sip_endpoint, username=sip_creds["username"], password=sip_creds["password"])
            response.append(dial)
            
            twiml_response = str(response)
            logger.info(f"Generated TwiML response: {twiml_response}")
            
            return twiml_response, 200, {"Content-Type": "application/xml"}
        except ValueError as e:
            if "VIDEOSDK_SIP" in str(e):
                logger.error(f"SIP credentials not configured: {e}")
                return "SIP configuration error", 500, {"Content-Type": "text/plain"}
            raise
        except Exception as e:
            logger.error(f"Error generating SIP response for room {room_id}: {e}", exc_info=True)
            return "An error occurred", 500, {"Content-Type": "text/plain"}

# Initialize Twilio manager
twilio_manager = TwilioManager()

# Module-level pipeline factory functions (needed for pickling)
def create_customer_pipeline():
    """Create customer pipeline at module level for pickling."""
    return create_pipeline("customer")

def create_specialist_pipeline():
    """Create specialist pipeline at module level for pickling."""
    return create_pipeline("specialist")

def start_customer_agent_for_call(call_id: str, room_id: str, caller_number: str = None) -> Dict[str, Any]:
    """Start a customer agent for a specific call using the SIP plugin pattern."""
    logger.info(f"🎯 Starting customer agent for call {call_id} in room {room_id}")
    
    try:
        # Configure agent for the call
        agent_config = {
            "room_name": "Customer Service Call",
            "enable_pubsub": False,
            "caller_number": caller_number,
            "call_id": call_id
        }
        logger.info(f"⚙️  Agent config: {agent_config}")

        # Launch agent job using the working SIP plugin pattern
        logger.info(f"🚀 Launching agent job with launch_agent_job...")
        customer_job = launch_agent_job(
            room_id=room_id,
            agent_config=agent_config,
            call_id=call_id,
            caller_number=caller_number
        )
        logger.info(f"✅ Agent job launched successfully for room {room_id}")

        # Store session information
        active_sessions[call_id] = {
            "room_id": room_id,
            "caller_number": caller_number,
            "job": customer_job,
            "status": "active"
        }
        logger.info(f"💾 Stored session info for call {call_id}")

        return {
            "status": "success",
            "call_id": call_id,
            "room_id": room_id,
            "message": "Customer agent started with A2A capabilities"
        }

    except Exception as e:
        logger.error(f"❌ Failed to start customer agent for call {call_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "call_id": call_id,
            "error": str(e)
        }

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for FastAPI app startup and shutdown."""
    port = int(os.getenv("PORT", 8000))
    
    try:
        # Setup ngrok tunnel (following sip_agent_example.py pattern)
        ngrok.kill()
        ngrok_auth_token = os.getenv("NGROK_AUTHTOKEN")
        if ngrok_auth_token:
            ngrok.set_auth_token(ngrok_auth_token)
        tunnel = ngrok.connect(port, "http")
        twilio_manager.set_base_url(tunnel.public_url)
        logger.info(f"Ngrok tunnel created: {tunnel.public_url}")
    except Exception as e:
        logger.error(f"Failed to start ngrok tunnel: {e}")
        # Continue without failing - outgoing calls will still work

    try:
        logger.info("✅ Services started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start services: {e}", exc_info=True)
        raise  # Re-raise to prevent app from starting with broken services

    yield

    try:
        # Cleanup
        ngrok.kill()
        logger.info("Ngrok tunnel closed")
    except Exception as e:
        logger.error(f"Error closing ngrok tunnel: {e}")

    try:
        logger.info("✅ Cleanup complete")
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")

# Create FastAPI app
app = FastAPI(title="SIP A2A Example", lifespan=lifespan)

@app.post("/call/make")
async def make_call(to_number: str):
    """Make an outgoing call with A2A capabilities."""
    if not twilio_manager.base_url:
        return {"status": "error", "message": "Service not ready (no base URL)."}

    logger.info(f"📞 Making outgoing call to {to_number}")

    try:
        # Make the call using direct Twilio integration
        call_details = await twilio_manager.make_call(to_number)
        
        call_id = call_details.get("sid")
        room_id = call_details.get("room_id") # Get the REAL room_id

        if call_id and room_id and call_details.get("status") != "failed":
            # Start our A2A-enabled customer agent in the correct room
            logger.info(f"📞 Call created successfully, starting customer agent in room {room_id}...")
            result = start_customer_agent_for_call(call_id, room_id, None)
            call_details.update(result)
        else:
            logger.error(f"❌ Call creation failed: {call_details}")

        return {"status": "success", "details": call_details}

    except Exception as e:
        logger.error(f"❌ Error making call: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@app.post("/sip/answer/{room_id}")
async def answer_webhook(room_id: str):
    """Handle SIP answer webhook."""
    logger.info(f"📞 Answering call for room: {room_id}")
    body, status_code, headers = twilio_manager.get_sip_response_for_room(room_id)
    return Response(content=body, status_code=status_code, media_type=headers.get("Content-Type"))

@app.post("/webhook/incoming")
async def incoming_webhook(request: Request):
    """Handle incoming call webhook with A2A setup."""
    if not twilio_manager.base_url:
        # Respond with a temporary error, but don't drop the call
        response = VoiceResponse()
        response.say("We are currently experiencing technical difficulties. Please call back later.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    try:
        content_type = request.headers.get("Content-Type", "")
        if "x-www-form-urlencoded" in content_type:
            webhook_data = dict(await request.form())
        else:
            webhook_data = await request.json()

        logger.info(f"📞 Received incoming webhook: {webhook_data}")

        # Extract call information
        caller_number = webhook_data.get("From", "Unknown")
        call_id = webhook_data.get("CallSid")

        if not call_id:
            logger.error("❌ No CallSid found in webhook data")
            return Response(content="Error: Missing CallSid", status_code=400)

        logger.info(f"📞 Incoming call from {caller_number} with CallSid: {call_id}")

        # Create a REAL room for this call
        logger.info(f"🏗️  Creating VideoSDK room for incoming call...")
        room_id = await twilio_manager.videosdk.create_room()
        logger.info(f"✅ VideoSDK room created: {room_id}")
        
        # Start our A2A-enabled customer agent for this call in the correct room
        logger.info(f"🚀 Starting customer agent for incoming call in room {room_id}...")
        result = start_customer_agent_for_call(call_id, room_id, caller_number)
        
        if result.get("status") == "error":
            logger.error(f"❌ Failed to start agent for incoming call: {result.get('error')}")
            # Still proceed with basic TwiML response to avoid dropping the call
        else:
            logger.info(f"✅ Customer agent started for incoming call")

        # Handle the call with direct Twilio integration
        logger.info(f"📞 Generating TwiML response for room: {room_id}")
        body, status_code, headers = twilio_manager.handle_incoming_call(webhook_data, room_id)

        return Response(content=body, status_code=status_code, media_type=headers.get("Content-Type"))

    except Exception as e:
        logger.error(f"❌ Error in incoming webhook: {e}", exc_info=True)
        # Return basic error response to avoid dropping the call
        return Response(content="Error processing request", status_code=500)

@app.get("/sessions")
async def get_sessions():
    """Get information about active sessions."""
    a2a_sessions = {
        "active_calls": len(active_sessions),
        "call_details": {
            call_id: {
                "room_id": details["room_id"],
                "caller_number": details["caller_number"],
                "status": details["status"]
            }
            for call_id, details in active_sessions.items()
        }
    }

    return {
        "a2a_sessions": a2a_sessions,
        "specialist_agent_running": False # No longer tracking specialist agent globally
    }

# @app.get("/test/voice", tags=["Testing"])
# async def test_voice_endpoint():
#     """Test endpoint to verify voice synthesis is working."""
#     try:
#         # Create a test pipeline
#         from session_manager import create_pipeline
#         pipeline = create_pipeline("customer")
        
#         # Check if the model has audio_track property
#         if not hasattr(pipeline.model, 'audio_track'):
#             return {"status": "error", "message": "Model does not have audio_track property"}
            
#         # Check audio_track configuration
#         audio_track_status = "Not configured"
#         if pipeline.model.audio_track:
#             audio_track_status = "Configured"
            
#         # Check response_modalities
#         response_modalities = getattr(pipeline.model.config, 'response_modalities', ["unknown"])
        
#         return {
#             "status": "success",
#             "pipeline_type": pipeline.__class__.__name__,
#             "model_type": pipeline.model.__class__.__name__,
#             "audio_track": audio_track_status,
#             "response_modalities": response_modalities,
#             "message": "Voice synthesis test completed"
#         }
#     except Exception as e:
#         logger.error(f"Error testing voice synthesis: {e}", exc_info=True)
#         return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "SIP A2A Example - Agent-to-Agent Communication over SIP",
        "features": [
            "SIP call handling",
            "Agent-to-Agent communication", 
            "Real-time audio processing",
            "Specialist query routing",
            "Call management"
        ],
        "endpoints": {
            "make_call": "/call/make",
            "incoming_webhook": "/webhook/incoming",
            "sessions": "/sessions",
            "test_voice": "/test/voice"
        },
        "status": {
            "specialist_agent_running": False, # No longer tracking specialist agent globally
            "active_calls": len(active_sessions)
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting SIP A2A Example server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 