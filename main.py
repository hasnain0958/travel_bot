from fastapi import FastAPI
from pydantic import BaseModel
import uuid
from .state import ConversationState
from .policy import respond

app = FastAPI(title="TravelBot API")
SESSIONS: dict[str, ConversationState] = {}

class ChatIn(BaseModel):
    session_id: str | None = None
    message: str

class ChatOut(BaseModel):
    session_id: str
    reply: str

@app.post("/chat", response_model=ChatOut)
def chat(inp: ChatIn):
    sid = inp.session_id or str(uuid.uuid4())
    state = SESSIONS.get(sid) or ConversationState(session_id=sid)
    state = respond(state, inp.message)
    SESSIONS[sid] = state
    return ChatOut(session_id=sid, reply=state.history[-1].bot)