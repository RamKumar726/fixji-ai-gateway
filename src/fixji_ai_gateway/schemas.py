from pydantic import BaseModel, Field
from typing import Literal


class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Email or phone")
    password: str


class LoginResponse(BaseModel):
    token: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = Field(
        default=None,
        description="Omit on the first message. Reuse the returned session_id afterwards.",
    )


class ChatResponse(BaseModel):
    session_id: str
    status: Literal["message", "pending_approval"]
    reply: str
    approval: dict | None = Field(
        default=None,
        description="Exact booking details awaiting approval (only when status=pending_approval)",
    )

class DecisionRequest(BaseModel):
    decision: Literal["approve", "reject"]
    reason: str | None = Field(
        default=None,
        description="Optional, for reject. Example: 'wrong address'",
    )