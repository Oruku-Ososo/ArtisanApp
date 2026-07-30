"""
WebSocket Module - Enhancements #29-35
#29: Real-time Verse Streaming
#30: Live Search Suggestions
#31: Collaborative Reading Rooms
#32: Real-time Notifications
#33: Live Prayer Requests
#34: Synchronized Study Groups
#35: Real-time Analytics Dashboard
"""
from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Set, Any
import json
from datetime import datetime

class ConnectionManager:
    """Enhancement #29-35: WebSocket Connection Manager"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, Set[str]] = {}  # room_id -> set of user_ids
        self.room_messages: Dict[str, List[Dict]] = {}  # room_id -> messages
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
    
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user"""
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass  # Connection might be closed
    
    async def broadcast_to_room(self, room_id: str, message: dict):
        """Broadcast message to room members"""
        if room_id not in self.rooms:
            return
        
        for user_id in self.rooms[room_id]:
            await self.send_personal_message(message, user_id)
    
    def join_room(self, user_id: str, room_id: str):
        """User joins a room"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
            self.room_messages[room_id] = []
        self.rooms[room_id].add(user_id)
    
    def leave_room(self, user_id: str, room_id: str):
        """User leaves a room"""
        if room_id in self.rooms and user_id in self.rooms[room_id]:
            self.rooms[room_id].remove(user_id)
    
    def add_room_message(self, room_id: str, user_id: str, content: str):
        """Add message to room history"""
        if room_id in self.room_messages:
            message = {
                "user_id": user_id,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.room_messages[room_id].append(message)
            # Keep last 100 messages
            self.room_messages[room_id] = self.room_messages[room_id][-100:]
    
    def get_room_history(self, room_id: str) -> List[Dict]:
        """Get room message history"""
        return self.room_messages.get(room_id, [])

class VerseStreamer:
    """Enhancement #29: Real-time Verse Streaming"""
    
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
    
    async def stream_verse(self, verse_data: dict, target_users: List[str] = None):
        """Stream verse to users"""
        message = {
            "type": "verse_stream",
            "data": verse_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if target_users:
            for user_id in target_users:
                await self.manager.send_personal_message(message, user_id)
        else:
            await self.manager.broadcast(message)

class SearchSuggester:
    """Enhancement #30: Live Search Suggestions"""
    
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
        self.suggestion_cache = {}
    
    async def suggest(self, query: str, user_id: str, suggestions: List[str]):
        """Send search suggestions to user"""
        message = {
            "type": "search_suggestions",
            "query": query,
            "suggestions": suggestions[:5],  # Top 5
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.send_personal_message(message, user_id)

class CollaborativeReading:
    """Enhancement #31: Collaborative Reading Rooms"""
    
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
        self.active_readings: Dict[str, Dict] = {}  # room_id -> current location
    
    def start_reading(self, room_id: str, book: str, chapter: int, verse: int):
        """Start collaborative reading session"""
        self.active_readings[room_id] = {
            "book": book,
            "chapter": chapter,
            "verse": verse,
            "started_at": datetime.utcnow().isoformat(),
            "participants": len(self.manager.rooms.get(room_id, set()))
        }
    
    async def navigate(self, room_id: str, book: str, chapter: int, verse: int):
        """Navigate to new location and notify room"""
        if room_id in self.active_readings:
            self.active_readings[room_id].update({
                "book": book,
                "chapter": chapter,
                "verse": verse
            })
        
        message = {
            "type": "reading_navigation",
            "location": f"{book} {chapter}:{verse}",
            "book": book,
            "chapter": chapter,
            "verse": verse,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast_to_room(room_id, message)

class NotificationService:
    """Enhancement #32: Real-time Notifications"""
    
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
    
    async def send_notification(self, user_id: str, title: str, message: str, notification_type: str = "info"):
        """Send notification to user"""
        payload = {
            "type": "notification",
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.send_personal_message(payload, user_id)
    
    async def broadcast_notification(self, title: str, message: str, notification_type: str = "info"):
        """Broadcast notification to all users"""
        payload = {
            "type": "notification",
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast(payload)

class PrayerRequestBoard:
    """Enhancement #33: Live Prayer Requests"""
    
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
        self.requests: List[Dict] = []
    
    async def submit_request(self, user_id: str, content: str, is_anonymous: bool = False):
        """Submit prayer request"""
        request = {
            "id": len(self.requests) + 1,
            "user_id": "anonymous" if is_anonymous else user_id,
            "content": content,
            "created_at": datetime.utcnow().isoformat(),
            "prayers": 0
        }
        self.requests.append(request)
        
        # Notify all users
        message = {
            "type": "new_prayer_request",
            "request": request
        }
        await self.manager.broadcast(message)
    
    async def add_prayer(self, request_id: int, user_id: str):
        """Add prayer to request"""
        for request in self.requests:
            if request["id"] == request_id:
                request["prayers"] += 1
                message = {
                    "type": "prayer_added",
                    "request_id": request_id,
                    "total_prayers": request["prayers"]
                }
                await self.manager.broadcast(message)
                break
    
    def get_requests(self, limit: int = 20) -> List[Dict]:
        """Get recent prayer requests"""
        return sorted(self.requests, key=lambda x: x["prayers"], reverse=True)[:limit]

class StudyGroupSync:
    """Enhancement #34: Synchronized Study Groups"""
    
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
        self.groups: Dict[str, Dict] = {}
    
    def create_group(self, group_id: str, leader_id: str, topic: str):
        """Create study group"""
        self.groups[group_id] = {
            "leader_id": leader_id,
            "topic": topic,
            "members": [leader_id],
            "current_passage": None,
            "notes": [],
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def sync_passage(self, group_id: str, passage_ref: str):
        """Sync passage across group"""
        if group_id in self.groups:
            self.groups[group_id]["current_passage"] = passage_ref
            
            message = {
                "type": "study_sync",
                "group_id": group_id,
                "passage": passage_ref,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for member_id in self.groups[group_id]["members"]:
                await self.manager.send_personal_message(message, member_id)
    
    async def add_note(self, group_id: str, user_id: str, note: str):
        """Add study note"""
        if group_id in self.groups:
            note_entry = {
                "user_id": user_id,
                "note": note,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.groups[group_id]["notes"].append(note_entry)
            
            message = {
                "type": "study_note",
                "group_id": group_id,
                "note": note_entry
            }
            await self.manager.broadcast_to_room(group_id, message)

class RealtimeAnalytics:
    """Enhancement #35: Real-time Analytics Dashboard"""
    
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
        self.stats = {
            "active_users": 0,
            "verses_read": 0,
            "searches": 0,
            "prayers": 0
        }
    
    def increment_stat(self, stat_name: str, value: int = 1):
        """Increment statistic"""
        if stat_name in self.stats:
            self.stats[stat_name] += value
    
    async def broadcast_stats(self):
        """Broadcast current stats to dashboard subscribers"""
        message = {
            "type": "analytics_update",
            "stats": {
                **self.stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.manager.broadcast(message)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        return {
            **self.stats,
            "active_connections": len(self.manager.active_connections),
            "active_rooms": len(self.manager.rooms)
        }

# Global manager instance
manager = ConnectionManager()
