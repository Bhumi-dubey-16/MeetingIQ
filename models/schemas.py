from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


# ── Enums (fixed value options) ───────────────────────────────────────────────

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


# ── Individual data models ────────────────────────────────────────────────────

class ActionItem(BaseModel):
    owner    : str            = Field(description="Person responsible")
    task     : str            = Field(description="What needs to be done")
    deadline : Optional[str] = Field(description="When it needs to be done")
    priority : Priority       = Field(description="HIGH, MEDIUM or LOW")

class FinancialItem(BaseModel):
    amount   : str            = Field(description="The number mentioned e.g. 50 lakh, $200K")
    context  : str            = Field(description="What this amount is about")
    status   : Status         = Field(description="DECIDED, DEFERRED or PENDING")
    owner    : Optional[str] = Field(description="Who is responsible for this")

class Priority_Item(BaseModel):
    item     : str            = Field(description="The priority item or task")
    priority : Priority       = Field(description="HIGH, MEDIUM or LOW")
    owner    : Optional[str] = Field(description="Who owns this")

class Commitment(BaseModel):
    person     : str          = Field(description="Who made the commitment")
    committed_to: str         = Field(description="What they committed to")
    target     : Optional[str]= Field(description="Any number or metric mentioned")
    deadline   : Optional[str]= Field(description="By when")

class UnresolvedQuestion(BaseModel):
    question   : str          = Field(description="The question that was raised")
    raised_by  : Optional[str]= Field(description="Who raised it")
    context    : str          = Field(description="Why it matters")

class Person(BaseModel):
    name       : str          = Field(description="Full name or role")
    role       : Optional[str]= Field(description="Their role or designation")
    email      : Optional[str]= Field(description="Email if mentioned in transcript")

class DateItem(BaseModel):
    date       : str          = Field(description="The date or timeframe mentioned")
    event      : str          = Field(description="What happens on this date")
    owner      : Optional[str]= Field(description="Who is responsible")
    priority   : Priority     = Field(description="How critical this deadline is")

class RiskItem(BaseModel):
    description: str          = Field(description="What the risk is")
    severity   : Severity     = Field(description="HIGH, MEDIUM or LOW")
    owner      : Optional[str]= Field(description="Who should handle this")
    mitigation : Optional[str]= Field(description="Any solution discussed")

class Decision(BaseModel):
    decision   : str          = Field(description="What was decided")
    status     : Status       = Field(description="DECIDED or DEFERRED")
    owner      : Optional[str]= Field(description="Who owns this decision")

class CoreSummary(BaseModel):
    one_line       : str          = Field(description="One line — what was this meeting about")
    decisions_made : List[Decision]= Field(description="All decisions made or deferred")
    next_steps     : List[str]    = Field(description="What happens after this meeting")
    meeting_type   : str          = Field(description="e.g. Planning, Review, Standup, Sales, HR")


# ── The full report — all sections combined ───────────────────────────────────

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
    status     : str
    message    : str
