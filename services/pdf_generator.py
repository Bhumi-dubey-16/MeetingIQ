import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.platypus import PageBreak
from models.schemas import FullReport, Priority, Severity, Status

# ── Colour palette ─────────────────────────────────────────────────────────────
DARK        = colors.HexColor("#0a0a0f")
PURPLE      = colors.HexColor("#6c63ff")
PURPLE_SOFT = colors.HexColor("#a78bfa")
SURFACE     = colors.HexColor("#111118")
BORDER      = colors.HexColor("#1e1e2e")
TEXT_PRI    = colors.HexColor("#e8e8f0")
TEXT_SEC    = colors.HexColor("#9090a8")
GREEN       = colors.HexColor("#22c55e")
YELLOW      = colors.HexColor("#eab308")
RED         = colors.HexColor("#ef4444")
BLUE        = colors.HexColor("#3b82f6")
WHITE       = colors.white

# ── Priority / Severity colour maps ───────────────────────────────────────────
PRIORITY_COLOR = {
    "HIGH":   RED,
    "MEDIUM": YELLOW,
    "LOW":    GREEN,
}

STATUS_COLOR = {
    "DECIDED":  GREEN,
    "DEFERRED": YELLOW,
    "PENDING":  RED,
}

# ── Style helpers ──────────────────────────────────────────────────────────────
def _style(name, **kwargs) -> ParagraphStyle:
    base = dict(
        fontName="Helvetica",
        fontSize=10,
        textColor=TEXT_PRI,
        leading=14,
        spaceAfter=0,
    )
    base.update(kwargs)
    return ParagraphStyle(name, **base)

S_TITLE      = _style("title",      fontName="Helvetica-Bold", fontSize=22, textColor=WHITE,    leading=28, spaceAfter=4)
S_SUBTITLE   = _style("subtitle",   fontName="Helvetica",      fontSize=11, textColor=TEXT_SEC, leading=16)
S_SECTION    = _style("section",    fontName="Helvetica-Bold", fontSize=13, textColor=PURPLE,   leading=18, spaceAfter=2)
S_BODY       = _style("body",       fontName="Helvetica",      fontSize=9,  textColor=TEXT_PRI, leading=13)
S_BODY_BOLD  = _style("bodybold",   fontName="Helvetica-Bold", fontSize=9,  textColor=TEXT_PRI, leading=13)
S_SMALL      = _style("small",      fontName="Helvetica",      fontSize=8,  textColor=TEXT_SEC, leading=12)
S_TAG        = _style("tag",        fontName="Helvetica-Bold", fontSize=7,  textColor=WHITE,    leading=10, alignment=TA_CENTER)
S_ONE_LINE   = _style("oneline",    fontName="Helvetica",      fontSize=10, textColor=TEXT_SEC, leading=15)
S_META       = _style("meta",       fontName="Helvetica",      fontSize=8,  textColor=TEXT_SEC, leading=12)


# ── Reusable flowables ─────────────────────────────────────────────────────────

def _hr() -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=10, spaceBefore=4)

def _gap(h=6) -> Spacer:
    return Spacer(1, h)

def _section_header(title: str, emoji: str = "") -> list:
    label = f"{emoji}  {title}" if emoji else title
    return [
        _gap(12),
        Paragraph(label, S_SECTION),
        HRFlowable(width="100%", thickness=1, color=PURPLE, spaceAfter=8, spaceBefore=2),
    ]

def _badge(text: str, bg: colors.Color) -> Table:
    """Renders a coloured pill badge."""
    p = Paragraph(text, S_TAG)
    t = Table([[p]], colWidths=[max(len(text) * 5.5 + 10, 36)])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    return t

def _priority_badge(priority: str) -> Table:
    return _badge(priority, PRIORITY_COLOR.get(priority, TEXT_SEC))

def _status_badge(status: str) -> Table:
    return _badge(status, STATUS_COLOR.get(status, TEXT_SEC))

def _card_table(rows: list, col_widths: list) -> Table:
    """A dark-surface card table."""
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        # Header row
        ("BACKGROUND",    (0, 0), (-1, 0),  SURFACE),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  PURPLE_SOFT),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  6),
        ("TOPPADDING",    (0, 0), (-1, 0),  6),
        # Data rows
        ("BACKGROUND",    (0, 1), (-1, -1), DARK),
        ("TEXTCOLOR",     (0, 1), (-1, -1), TEXT_PRI),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("TOPPADDING",    (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        # Grid
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        # Alternating rows
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [DARK, SURFACE]),
    ]))
    return t


# ── Cover page ────────────────────────────────────────────────────────────────

def _cover_page(report: FullReport) -> list:
    W, H = A4
    generated = datetime.now().strftime("%B %d, %Y  •  %H:%M")
    meeting_type = report.summary.meeting_type or "Meeting"

    story = []

    # Dark header band
    header = Table(
        [[Paragraph("MeetingIQ", _style("logo", fontName="Helvetica-Bold", fontSize=28, textColor=WHITE, leading=34)),
          Paragraph("AI Meeting Intelligence", _style("tagline", fontName="Helvetica", fontSize=10, textColor=TEXT_SEC, leading=14))]],
        colWidths=[100*mm, 90*mm]
    )
    header.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (1, 0), (1, 0),   "RIGHT"),
    ]))
    story.append(header)
    story.append(_gap(40))

    # Meeting type badge
    story.append(Table(
        [[_badge(meeting_type.upper(), PURPLE)]],
        colWidths=[190*mm]
    ))
    story.append(_gap(16))

    # One-line summary as title
    story.append(Paragraph(report.summary.one_line, S_TITLE))
    story.append(_gap(8))
    story.append(Paragraph(f"Generated on {generated}", S_ONE_LINE))
    story.append(_gap(32))
    story.append(_hr())
    story.append(_gap(16))

    # Stats row
    n_actions     = len(report.action_items)
    n_risks       = len(report.risks)
    n_financials  = len(report.financial_items)
    n_people      = len(report.people)
    high_risks    = sum(1 for r in report.risks if r.severity == Severity.HIGH)

    stats = [
        ["ACTION ITEMS", "RISKS", "FINANCIALS", "PEOPLE"],
        [str(n_actions), str(n_risks), str(n_financials), str(n_people)],
    ]
    stat_table = Table(stats, colWidths=[47.5*mm]*4)
    stat_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), SURFACE),
        ("TEXTCOLOR",     (0, 0), (3, 0),   TEXT_SEC),
        ("FONTNAME",      (0, 0), (3, 0),   "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (3, 0),   7),
        ("LETTERSPACINGADJUST", (0, 0), (3, 0), 2),
        ("TEXTCOLOR",     (0, 1), (3, 1),   PURPLE),
        ("FONTNAME",      (0, 1), (3, 1),   "Helvetica-Bold"),
        ("FONTSIZE",      (0, 1), (3, 1),   28),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
    ]))
    story.append(stat_table)

    if high_risks:
        story.append(_gap(12))
        story.append(Paragraph(
            f"<font color='#ef4444'><b>⚠  {high_risks} HIGH severity risk(s) identified — review before next steps.</b></font>",
            _style("warn", fontName="Helvetica-Bold", fontSize=9, textColor=RED, leading=13)
        ))

    story.append(PageBreak())
    return story


# ── Section builders ──────────────────────────────────────────────────────────

def _section_summary(report: FullReport) -> list:
    s = report.summary
    story = _section_header("Core Summary", "📋")

    # Decisions table
    if s.decisions_made:
        rows = [["DECISION", "STATUS", "OWNER"]]
        for d in s.decisions_made:
            rows.append([
                Paragraph(d.decision, S_BODY),
                _status_badge(d.status.value),
                Paragraph(d.owner or "—", S_BODY),
            ])
        story.append(_card_table(rows, [95*mm, 28*mm, 57*mm]))
        story.append(_gap(10))

    # Next steps
    if s.next_steps:
        story.append(Paragraph("Next Steps", S_BODY_BOLD))
        story.append(_gap(4))
        for i, step in enumerate(s.next_steps, 1):
            story.append(Paragraph(f"{i}.  {step}", S_BODY))
            story.append(_gap(3))

    return story


def _section_action_items(report: FullReport) -> list:
    if not report.action_items:
        return []
    story = _section_header("Action Items", "✅")
    rows = [["OWNER", "TASK", "DEADLINE", "PRIORITY"]]
    for item in report.action_items:
        rows.append([
            Paragraph(item.owner, S_BODY_BOLD),
            Paragraph(item.task, S_BODY),
            Paragraph(item.deadline or "—", S_SMALL),
            _priority_badge(item.priority.value),
        ])
    story.append(_card_table(rows, [35*mm, 90*mm, 28*mm, 22*mm]))
    return story


def _section_financials(report: FullReport) -> list:
    if not report.financial_items:
        return []
    story = _section_header("Financial Items", "💰")
    rows = [["AMOUNT", "CONTEXT", "STATUS", "OWNER"]]
    for item in report.financial_items:
        rows.append([
            Paragraph(item.amount, S_BODY_BOLD),
            Paragraph(item.context, S_BODY),
            _status_badge(item.status.value),
            Paragraph(item.owner or "—", S_SMALL),
        ])
    story.append(_card_table(rows, [30*mm, 90*mm, 28*mm, 32*mm]))
    return story


def _section_priorities(report: FullReport) -> list:
    if not report.priorities:
        return []
    story = _section_header("Priorities", "🎯")
    rows = [["PRIORITY ITEM", "LEVEL", "OWNER"]]
    for item in report.priorities:
        rows.append([
            Paragraph(item.item, S_BODY),
            _priority_badge(item.priority.value),
            Paragraph(item.owner or "—", S_SMALL),
        ])
    story.append(_card_table(rows, [110*mm, 28*mm, 42*mm]))
    return story


def _section_commitments(report: FullReport) -> list:
    if not report.commitments:
        return []
    story = _section_header("Targets & Commitments", "🤝")
    rows = [["PERSON", "COMMITTED TO", "TARGET", "DEADLINE"]]
    for item in report.commitments:
        rows.append([
            Paragraph(item.person, S_BODY_BOLD),
            Paragraph(item.committed_to, S_BODY),
            Paragraph(item.target or "—", S_SMALL),
            Paragraph(item.deadline or "—", S_SMALL),
        ])
    story.append(_card_table(rows, [35*mm, 85*mm, 30*mm, 30*mm]))
    return story


def _section_questions(report: FullReport) -> list:
    if not report.unresolved_questions:
        return []
    story = _section_header("Unresolved Questions", "❓")
    rows = [["QUESTION", "RAISED BY", "CONTEXT"]]
    for item in report.unresolved_questions:
        rows.append([
            Paragraph(item.question, S_BODY),
            Paragraph(item.raised_by or "—", S_SMALL),
            Paragraph(item.context, S_BODY),
        ])
    story.append(_card_table(rows, [70*mm, 30*mm, 80*mm]))
    return story


def _section_people(report: FullReport) -> list:
    if not report.people:
        return []
    story = _section_header("People & Roles", "👥")
    rows = [["NAME", "ROLE", "EMAIL"]]
    for p in report.people:
        rows.append([
            Paragraph(p.name, S_BODY_BOLD),
            Paragraph(p.role or "—", S_BODY),
            Paragraph(p.email or "—", S_SMALL),
        ])
    story.append(_card_table(rows, [55*mm, 65*mm, 60*mm]))
    return story


def _section_dates(report: FullReport) -> list:
    if not report.dates_deadlines:
        return []
    story = _section_header("Dates & Deadlines", "📅")
    rows = [["DATE", "EVENT", "OWNER", "PRIORITY"]]
    for item in report.dates_deadlines:
        rows.append([
            Paragraph(item.date, S_BODY_BOLD),
            Paragraph(item.event, S_BODY),
            Paragraph(item.owner or "—", S_SMALL),
            _priority_badge(item.priority.value),
        ])
    story.append(_card_table(rows, [30*mm, 95*mm, 35*mm, 20*mm]))
    return story


def _section_risks(report: FullReport) -> list:
    if not report.risks:
        return []
    story = _section_header("Risks & Blockers", "⚠️")
    rows = [["RISK", "SEVERITY", "OWNER", "MITIGATION"]]
    for item in report.risks:
        rows.append([
            Paragraph(item.description, S_BODY),
            _priority_badge(item.severity.value),
            Paragraph(item.owner or "—", S_SMALL),
            Paragraph(item.mitigation or "—", S_BODY),
        ])
    story.append(_card_table(rows, [70*mm, 22*mm, 30*mm, 58*mm]))
    return story


# ── Footer callback ────────────────────────────────────────────────────────────

class _Footer:
    def __init__(self, report: FullReport):
        self.one_line = report.summary.one_line[:60] + "…" if len(report.summary.one_line) > 60 else report.summary.one_line

    def __call__(self, canvas, doc):
        canvas.saveState()
        W, H = A4
        canvas.setFillColor(BORDER)
        canvas.rect(0, 0, W, 14*mm, fill=True, stroke=False)
        canvas.setFillColor(TEXT_SEC)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(16*mm, 5*mm, f"MeetingIQ  •  {self.one_line}")
        canvas.drawRightString(W - 16*mm, 5*mm, f"Page {doc.page}")
        canvas.restoreState()


# ── Public entry point ────────────────────────────────────────────────────────

def generate_pdf(report: FullReport, output_path: str) -> str:
    """
    Generates a styled PDF from a FullReport object.
    Returns the output_path on success.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=16*mm,
        rightMargin=16*mm,
        topMargin=16*mm,
        bottomMargin=20*mm,
        title="MeetingIQ Report",
        author="MeetingIQ",
    )

    footer = _Footer(report)

    story = []
    story += _cover_page(report)
    story += _section_summary(report)
    story += _section_action_items(report)
    story += _section_financials(report)
    story += _section_priorities(report)
    story += _section_commitments(report)
    story += _section_questions(report)
    story += _section_people(report)
    story += _section_dates(report)
    story += _section_risks(report)

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"[PDF] Generated → {output_path}")
    return output_path