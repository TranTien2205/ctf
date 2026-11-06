"""Team orchestration: lead agent + role workers over a shared blackboard."""
from .board import Board
from .leads import Lead, LeadQueue

__all__ = ["Board", "Lead", "LeadQueue"]
