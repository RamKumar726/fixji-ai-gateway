import logging
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException
from langgraph.types import Command

from ..agent import build_agent
from ..dependencies import get_token
from ..schemas import ChatRequest, ChatResponse, DecisionRequest
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
    except Exception:
        logger.excpetion("Agent Invocation failed")
        raise HTTPException(
            status_code = 502,
            detail = "The assistance failed to respond. Please try again."
        )

    session.last_used = time.time()
    interrupts = result.get("__interrupt__")
    if interrupts:
        action = interrupts[0].value["action_requests"][0]
        session.pending_approval = True
        return ChatResponse(
            session_id=session.session_id,
            status="pending_approval",
            reply="Please review and confirm your booking.",
            approval=action["args"],  # the REAL arguments, not LLM-written text
        )

    session.pending_approval = False
    return ChatResponse(
        session_id=session.session_id,
        status="message",
        reply=_extract_text(result["messages"][-1].content),
    )



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
        if session.pending_approval:
            raise HTTPException(
                status_code=409,
                detail="A booking is waiting for your approval. Approve or reject it first.",
            )
        # only the NEW message is sent; the checkpointer holds the history
        return await _run(
            session,
            {"messages": [{"role": "user", "content": body.message}]},
        )

@router.post("/{session_id}/decision", response_model=ChatResponse)
async def decide(session_id: str, body: DecisionRequest, token: str = Depends(get_token)):
    session = _get_owned_session(session_id, token)

    async with session.lock:
        if not session.pending_approval:
            raise HTTPException(status_code=409, detail="Nothing is waiting for approval")

        if body.decision == "approve":
            decision = {"type": "approve"}
        else:
            decision = {
                "type": "reject",
                "message": body.reason or "The customer rejected this booking.",
            }

        return await _run(session, Command(resume={"decisions": [decision]}))


@router.delete("/{session_id}", status_code=204)
async def end_session(session_id: str, token: str = Depends(get_token)):
    session = store.get(session_id)
    if session is None:
        return
    if session.token != token:
        raise HTTPException(status_code=403, detail="Session does not belong to this user")
    store.delete(session_id)