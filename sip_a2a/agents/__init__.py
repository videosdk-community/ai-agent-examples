"""
SIP A2A Agents Package

This package contains agent implementations for the SIP A2A example,
demonstrating Agent-to-Agent communication over SIP calls.
"""

from .customer_agent import SIPCustomerServiceAgent
from .loan_agent import SIPLoanSpecialistAgent

__all__ = [
    "SIPCustomerServiceAgent",
    "SIPLoanSpecialistAgent",
] 