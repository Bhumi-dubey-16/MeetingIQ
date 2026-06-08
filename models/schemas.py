from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class Priority(str, Enum):
    HIGH   = "HIGH"
    MEDIUM = "MEDIUM"
    LOW    = "LOW"

class Severity(str, Enum):
    HIGH   = "HIGH"
    MEDIUM = "MEDIUM"
    LOW    = "LOW"

class Status(str, Enum):
    DECIDED  = "DECIDED"
    DEFERRED = "DEFERRED"
    PENDING  = "PENDING"


# ── Coercion helpers ──────────────────────────────────────────────────────────
# The LLM occasionally returns values outside the allowed enum set
# (e.g. "AT RISK", "TBD", "APPROVED"). Instead of crashing, we map them
# to the closest valid value and keep the report intact.

def _coerce_status(v) -> str:
    """Map any freeform LLM status string → DECIDED | DEFERRED | PENDING."""
    if isinstance(v, Status):
        return v
    s = str(v).upper().strip()
    if s in ("DECIDED", "APPROVED", "CONFIRMED", "DONE", "COMPLETE", "COMPLETED"):
        return "DECIDED"
    if s in ("DEFERRED", "POSTPONED", "DELAYED", "ON HOLD", "BLOCKED"):
        return "DEFERRED"
    # Everything else (AT RISK, TBD, UNKNOWN, etc.) → PENDING
    return "PENDING"

def _coerce_priority(v) -> str:
    """Map any freeform LLM priority string → HIGH | MEDIUM | LOW."""
    if isinstance(v, (Priority, Severity)):
        return v
    s = str(v).upper().strip()
    if s in ("HIGH", "CRITICAL", "URGENT", "P0", "P1"):
        return "HIGH"
    if s in ("MEDIUM", "MODERATE", "NORMAL", "P2"):
        return "MEDIUM"
    return "LOW"

def _coerce_severity(v) -> str:
    """Map any freeform LLM severity string → HIGH | MEDIUM | LOW."""
    return _coerce_priority(v)  # same mapping logic


# ── Individual data models ────────────────────────────────────────────────────

class ActionItem(BaseModel):
    owner    : str            = Field(description="Person responsible")
    task     : str            = Field(description="What needs to be done")
    deadline : Optional[str] = Field(default=None, description="When it needs to be done")
    priority : Priority       = Field(description="HIGH, MEDIUM or LOW")

    @field_validator("priority", mode="before")
    @classmethod
    def coerce_priority(cls, v):
        return _coerce_priority(v)


class FinancialItem(BaseModel):
    amount   : str            = Field(description="The number mentioned e.g. 50 lakh, $200K")
    context  : str            = Field(description="What this amount is about")
    status   : Status         = Field(description="DECIDED, DEFERRED or PENDING")
    owner    : Optional[str] = Field(default=None, description="Who is responsible for this")

    @field_validator("status", mode="before")
    @classmethod
    def coerce_status(cls, v):
        return _coerce_status(v)


class Priority_Item(BaseModel):
    item     : str            = Field(description="The priority item or task")
    priority : Priority       = Field(description="HIGH, MEDIUM or LOW")
    owner    : Optional[str] = Field(default=None, description="Who owns this")

    @field_validator("priority", mode="before")
    @classmethod
    def coerce_priority(cls, v):
        return _coerce_priority(v)


class Commitment(BaseModel):
    person      : str          = Field(description="Who made the commitment")
    committed_to: str          = Field(description="What they committed to")
    target      : Optional[str]= Field(default=None, description="Any number or metric mentioned")
    deadline    : Optional[str]= Field(default=None, description="By when")


class UnresolvedQuestion(BaseModel):
    question  : str           = Field(description="The question that was raised")
    raised_by : Optional[str] = Field(default=None, description="Who raised it")
    context   : str           = Field(description="Why it matters")


class Person(BaseModel):
    name  : str           = Field(description="Full name or role")
    role  : Optional[str] = Field(default=None, description="Their role or designation")
    email : Optional[str] = Field(default=None, description="Email if mentioned in transcript")


class DateItem(BaseModel):
    date     : str          = Field(description="The date or timeframe mentioned")
    event    : str          = Field(description="What happens on this date")
    owner    : Optional[str]= Field(default=None, description="Who is responsible")
    priority : Priority     = Field(description="How critical this deadline is")

    @field_validator("priority", mode="before")
    @classmethod
    def coerce_priority(cls, v):
        return _coerce_priority(v)


class RiskItem(BaseModel):
    description: str          = Field(description="What the risk is")
    severity   : Severity     = Field(description="HIGH, MEDIUM or LOW")
    owner      : Optional[str]= Field(default=None, description="Who should handle this")
    mitigation : Optional[str]= Field(default=None, description="Any solution discussed")

    @field_validator("severity", mode="before")
    @classmethod
    def coerce_severity(cls, v):
        return _coerce_severity(v)


class Decision(BaseModel):
    decision : str          = Field(description="What was decided")
    status   : Status       = Field(description="DECIDED or DEFERRED")
    owner    : Optional[str]= Field(default=None, description="Who owns this decision")

    @field_validator("status", mode="before")
    @classmethod
    def coerce_status(cls, v):
        return _coerce_status(v)


class CoreSummary(BaseModel):
    one_line       : str           = Field(description="One line — what was this meeting about")
    decisions_made : List[Decision] = Field(description="All decisions made or deferred")
    next_steps     : List[str]     = Field(description="What happens after this meeting")
    meeting_type   : str           = Field(description="e.g. Planning, Review, Standup, Sales, HR")


# ── The full report ───────────────────────────────────────────────────────────

class FullReport(BaseModel):
    summary             : CoreSummary
    action_items        : List[ActionItem]
    financial_items     : List[FinancialItem]
    priorities          : List[Priority_Item]
    commitments         : List[Commitment]
    unresolved_questions: List[UnresolvedQuestion]
    people              : List[Person]
    dates_deadlines     : List[DateItem]
    risks               : List[RiskItem]


# ── API request/response models ───────────────────────────────────────────────

class AnalyseResponse(BaseModel):
    report_id  : str
    report     : FullReport
    transcript : str

class EmailRequest(BaseModel):
    report_id  : str
    emails     : List[str]
    attendees  : List[Person]

class StatusResponse(BaseModel):
    status  : str
    message : str