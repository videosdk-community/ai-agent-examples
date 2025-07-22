import logging
from videosdk.agents import Agent, AgentCard, A2AMessage

logger = logging.getLogger(__name__)

class SIPLoanSpecialistAgent(Agent):
    """Loan specialist agent that handles loan-related queries via A2A"""
    
    def __init__(self):
        """Initialize the loan specialist agent"""
        super().__init__(
            agent_id="sip_loan_specialist_1",
            instructions=(
                "You are a specialized loan expert at a bank. "
                "Provide detailed, helpful information about loans including interest rates, terms, and requirements. "
                "Give complete answers with specific details when possible. "
                "You can discuss personal loans, car loans, home loans, and business loans. "
                "Provide helpful guidance and next steps for loan applications. "
                "Be friendly and professional in your responses."
                "And make sure all of this will cover within 5-7 lines and short and understandable response"
            )
        )
        # Initialize tracking attributes for A2A communication
        self._current_call_id = None
        self._current_requesting_agent = None
        logger.info("SIPLoanSpecialistAgent initialized")

    async def handle_specialist_query(self, message: A2AMessage) -> None:
        """Handle query from customer agent"""
        query = message.content.get("query")
        call_id = message.content.get("call_id", "unknown")
        from_agent = message.from_agent
        
        if query:
            logger.info(f"LoanAgent received query for call {call_id}: '{query}' from {from_agent}")
            # Process the query with our LLM
            await self.session.pipeline.send_text_message(query)
            logger.info(f"Sent query to LoanAgent's LLM for processing")
            
            # Store the call_id and requesting_agent for use in model_response handler
            self._current_call_id = call_id
            self._current_requesting_agent = from_agent

    async def handle_model_response(self, message: A2AMessage) -> None:
        """Handle response from LLM and forward back to customer agent"""
        response = message.content.get("response")
        requesting_agent = getattr(self, '_current_requesting_agent', None)
        call_id = getattr(self, '_current_call_id', None)
        
        if response and requesting_agent:
            # Log the first 50 chars of the response to avoid log spam
            logger.info(f"LoanAgent got LLM response: '{response[:50]}...'")
            
            # Send the response back to the requesting agent
            await self.a2a.send_message(
                to_agent=requesting_agent,
                message_type="specialist_response",
                content={
                    "response": response,  # Send the full response
                    "call_id": call_id     # Include the call_id in the response
                }
            )
            
            logger.info(f"Sent response back to agent {requesting_agent}")
            
            # Clear the current request tracking
            self._current_call_id = None
            self._current_requesting_agent = None

    async def greet_user(self) -> None:
        """Greet user - specialist agent doesn't need to greet as it's background"""
        logger.info("Loan specialist agent ready (no greeting needed - background agent)")

    async def on_enter(self) -> None:
        """Called when the agent session starts"""
        logger.info(f"🎯 SIPLoanSpecialistAgent entering session")
        try:
            await self.register_a2a(AgentCard(
                id="sip_loan_specialist_1",
                name="Loan Specialist Agent",
                domain="loan",
                capabilities=["loan_consultation", "loan_information", "interest_rates"],
                description="Handles loan queries via A2A"
            ))
            logger.info("✅ Loan specialist agent registered for A2A communication")
            
            self.a2a.on_message("specialist_query", self.handle_specialist_query)
            self.a2a.on_message("model_response", self.handle_model_response)
            logger.info("✅ Registered A2A message handlers for loan specialist")
        except Exception as e:
            logger.error(f"❌ Error in LoanSpecialistAgent on_enter: {e}", exc_info=True)

    async def on_exit(self) -> None:
        """Called when the agent session ends"""
        logger.info(f"SIP Loan specialist agent ending session")
        await self.unregister_a2a() 