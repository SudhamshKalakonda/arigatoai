import os
import json
import time
from typing import List, Dict

MEMORY_FILE = "data/session_memory.json"
MAX_TURNS = 10        # Remember last 10 messages per session
SESSION_TTL = 60 * 60 * 24  # Sessions expire after 24 hours

def load_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory: dict) -> None:
    os.makedirs("data", exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

def purge_expired_sessions(memory: dict) -> dict:
    now = time.time()
    active = {
        sid: data for sid, data in memory.items()
        if now - data.get("last_active", 0) < SESSION_TTL
    }
    if len(active) < len(memory):
        print(f"Purged {len(memory) - len(active)} expired sessions")
    return active

def get_session_history(session_id: str) -> List[Dict]:
    """Get conversation history for a session."""
    memory = load_memory()
    memory = purge_expired_sessions(memory)

    if session_id not in memory:
        return []

    return memory[session_id].get("messages", [])

def add_to_session(session_id: str, question: str, answer: str) -> None:
    """Add a Q&A turn to session memory."""
    memory = load_memory()
    memory = purge_expired_sessions(memory)

    if session_id not in memory:
        memory[session_id] = {
            "messages": [],
            "created_at": time.time(),
            "last_active": time.time()
        }

    memory[session_id]["messages"].append({
        "role": "user",
        "content": question
    })
    memory[session_id]["messages"].append({
        "role": "assistant",
        "content": answer
    })

    # Keep only last MAX_TURNS * 2 messages (each turn = 2 messages)
    memory[session_id]["messages"] = memory[session_id]["messages"][-(MAX_TURNS * 2):]
    memory[session_id]["last_active"] = time.time()

    save_memory(memory)
    print(f"Session {session_id[:8]}... updated: {len(memory[session_id]['messages'])} messages")

def get_memory_stats() -> dict:
    memory = load_memory()
    memory = purge_expired_sessions(memory)
    return {
        "active_sessions": len(memory),
        "max_turns_per_session": MAX_TURNS,
        "session_ttl_hours": SESSION_TTL / 3600
    }