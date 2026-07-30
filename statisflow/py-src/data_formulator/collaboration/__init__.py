"""
StatisFLOW Collaboration Module
Live Collaboration Workspace with Role-Based Access
"""

from .workspace import CollaborationWorkspace
from .roles import RoleManager

__all__ = [
    "CollaborationWorkspace",
    "RoleManager"
]
