import logging
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException
from langgraph.types import Command

from ..agent import build_agent
from ..dependencies import get_token
from ..schemas import ChatRequest, ChatResponse
from ..session import Session, store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


def _extract_text(content) -> str:
    """LangChain message content can be a string or a list of blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts)
    return str(content)

def _get_owned_session(session_id: str, token: str) -> Session:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    if session.token != token:
        raise HTTPException(status_code=403, detail="Session does not belong to this user")
    return session

async def _run(session : Session, agent_input) -> ChatRequest:
    """Run the agent, and convert the result into either a reply or an approval request."""
    config = {"configurable" : {"thread_id" : session.session_id}}
    try:
        result = await session.agent.ainvoke(agent_input,  config)
    except:
        pass


@router.post("", response_model=ChatResponse)
async def chat(body: ChatRequest, token: str = Depends(get_token)):
    store.purge_expired()

    session = store.get(body.session_id)

    if session and session.token != token:
        raise HTTPException(status_code=403, detail="Session does not belong to this user")

    if session is None:
        try:
            agent = await build_agent(token)
        except Exception:
            logger.exception("Failed to build agent")
            raise HTTPException(status_code=502, detail="AI service is unavailable")
        session = Session(session_id=uuid.uuid4().hex, token=token, agent=agent)
        store.add(session)

    # one request at a time per session, so history can't get interleaved
    async with session.lock:
        session.history.append({"role": "user", "content": body.message})
        try:
            result = await session.agent.ainvoke({"messages": session.history})
        except Exception:
            logger.exception("Agent invocation failed")
            session.history.pop()  # drop the unanswered user message
            raise HTTPException(status_code=502, detail="The assistant failed to respond. Please try again.")

        session.history = result["messages"]
        session.last_used = time.time()
        reply = _extract_text(result["messages"][-1].content)

    return ChatResponse(session_id=session.session_id, reply=reply)


@router.delete("/{session_id}", status_code=204)
async def end_session(session_id: str, token: str = Depends(get_token)):
    session = store.get(session_id)
    if session is None:
        return
    if session.token != token:
        raise HTTPException(status_code=403, detail="Session does not belong to this user")
    store.delete(session_id)