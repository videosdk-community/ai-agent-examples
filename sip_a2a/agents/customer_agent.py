import asyncio
import logging
from typing import Dict, Any, Optional
from videosdk.agents import Agent, AgentCard, A2AMessage, function_tool

logger = logging.getLogger(__name__)

class SIPCustomerServiceAgent(Agent):
    """A SIP-enabled customer service agent that handles voice calls and forwards specialist queries via A2A."""
    
    def __init__(self, ctx: Optional[Any] = None):
        super().__init__(
            agent_id="sip_customer_service_1",
            instructions=(
                "You are a helpful bank customer service agent handling a phone call. "
                "Be friendly, professional, and speak naturally as if on the phone. "
                "For general banking queries (account balances, transactions, basic services), answer directly. "
                "For ANY loan-related queries, questions, or follow-ups, ALWAYS use the forward_to_specialist function "
                "with domain set to 'loan'. This includes initial loan questions AND all follow-up questions about loans. "
                "Do NOT attempt to answer loan questions yourself - always forward them to the specialist. "
                "After forwarding a loan query, tell the customer you're checking with our loan specialist. "
                "When you receive responses from specialists, immediately relay them naturally to the customer. "
                "Keep responses conversational and appropriate for a phone call."
            )
        )
        self.ctx = ctx
        self.call_id = None
        self.caller_number = None
        self.greeting_message = "Hello! Thank you for calling our bank. How can I assist you today?"
        
        # Extract call information from context (following SIP plugin pattern)
        if ctx and hasattr(ctx, 'caller_number'):
            self.caller_number = ctx.caller_number
        if ctx and hasattr(ctx, 'call_id'):
            self.call_id = ctx.call_id
            
        logger.info(f"SIPCustomerServiceAgent created with call_id={self.call_id}, caller={self.caller_number}")

    @function_tool
    async def forward_to_specialist(self, query: str, domain: str) -> Dict[str, Any]:
        """Forward a query to a specialist agent in the specified domain"""
        logger.info(f"Forwarding query to domain '{domain}': '{query}' for call {self.call_id}")
        
        specialists = self.a2a.registry.find_agents_by_domain(domain)
        id_of_target_agent = specialists[0] if specialists else None
        
        if not id_of_target_agent:
            logger.error(f"No specialist found for domain {domain}")
            return {"error": f"No specialist found for domain {domain}"}

        logger.info(f"Found specialist: {id_of_target_agent}")
        
        await self.a2a.send_message(
            to_agent=id_of_target_agent,
            message_type="specialist_query",
            content={
                "query": query,
                "call_id": self.call_id  # Include call_id in the message
            }
        )
        
        return {
            "status": "forwarded",
            "specialist": id_of_target_agent,
            "message": "Let me get that information for you from our loan specialist..."
        }

    @function_tool
    async def end_call(self) -> str:
        """End the current call gracefully"""
        logger.info(f"Gracefully ending call_id: {self.call_id}")
        await self.session.say("Thank you for calling. Have a great day!")
        await asyncio.sleep(1.5)
        await self.session.leave()
        return "Call ended gracefully"

    @function_tool
    async def transfer_to_human(self) -> Dict[str, Any]:
        """Transfer the current call to a human support agent"""
        logger.info(f"Transferring call {self.call_id} to human support")
        # This would integrate with your SIP provider's transfer functionality
        await self.session.say("Let me transfer you to one of our human representatives. Please hold.")
        return {
            "status": "transfer_initiated",
            "message": "Transferring to human support...",
            "call_id": self.call_id
        }

    async def handle_specialist_response(self, message: A2AMessage) -> None:
        """Handle responses from the specialist agent"""
        response = message.content.get("response")
        call_id = message.content.get("call_id")
        
        if response:
            logger.info(f"Got specialist response for call {call_id}: {response[:50]}...")
            
            # Check if this response is for our call
            if call_id != self.call_id:
                logger.warning(f"Received response for different call: {call_id} vs {self.call_id}")
                # Still process it since we're the customer agent
            
            try:
                # Use session.say directly - this is the most reliable method for SIP calls
                # It will properly route through the TTS system to generate audio
                logger.info(f"Relaying specialist response to caller via session.say...")
                await self.session.say(response)
                logger.info(f"Successfully relayed specialist response via session.say")
            except Exception as e:
                logger.error(f"Error relaying specialist response: {e}", exc_info=True)
                # Try alternative methods as fallback
                try:
                    logger.info("Trying fallback method: pipeline.send_message")
                    await self.session.pipeline.send_message(response)
                    logger.info("Successfully relayed via pipeline.send_message")
                except Exception as e2:
                    logger.error(f"Fallback also failed: {e2}", exc_info=True)

    async def greet_user(self) -> None:
        """Greet the user when they join the call (called from on_enter when session is ready)"""
        logger.info(f"💬 Greeting user for call_id: {self.call_id}")
        
        try:
            # Use session.say() method for audio output (following a2a pattern)
            await self.session.say(self.greeting_message)
            logger.info(f"✅ User greeted successfully: {self.greeting_message}")
            
        except Exception as e:
            logger.error(f"❌ Error greeting user for call_id {self.call_id}: {e}", exc_info=True)

    async def on_enter(self) -> None:
        """Called when the agent session starts"""
        logger.info(f"🎯 SIPCustomerServiceAgent entering session for call_id: {self.call_id}")
        
        try:
            # Register for A2A communication
            logger.info(f"📋 Registering for A2A communication...")
            await self.register_a2a(AgentCard(
                id="sip_customer_service_1",
                name="SIP Customer Service Agent",
                domain="customer_service",
                capabilities=["query_handling", "specialist_coordination", "call_management"],
                description="Handles customer phone calls and coordinates with specialists"
            ))
            logger.info("✅ Registered for A2A communication")
            
            # Set up message handler for specialist responses
            self.a2a.on_message("specialist_response", self.handle_specialist_response)
            logger.info("✅ Registered A2A message handlers")
            
            # Greet the user (session is now properly available)
            await self.greet_user()
            
        except Exception as e:
            logger.error(f"❌ Error in on_enter for call_id {self.call_id}: {e}", exc_info=True)

    async def on_exit(self) -> None:
        """Called when the agent session ends"""
        logger.info(f"SIP Customer agent ending session for call_id: {self.call_id}")
        await self.unregister_a2a() 