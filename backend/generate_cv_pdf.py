#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "reportlab>=4.5.0",
#   "Pillow>=12.0.0",
# ]
# ///
"""Generate a professional CV PDF from cv.md and headshot.jpeg.

All styling, fonts, colours, and layout are defined in this script — no
network calls and no external assets beyond the two source files in
``backend/data/``. Helvetica (built into ReportLab) is used so the script
works offline.

Usage (from any working directory):
    uv run backend/generate_cv_pdf.py

Or, if you prefer plain pip/venv:
    pip install reportlab Pillow
    python backend/generate_cv_pdf.py

Output:
    backend/data/cv.pdf
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    HRFlowable,
    Image as RLImage,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR / "data"
CV_MD = DATA_DIR / "cv.md"
HEADSHOT = DATA_DIR / "headshot.jpeg"
OUTPUT = DATA_DIR / "cv.pdf"


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

NAVY = colors.HexColor("#0f2742")
ACCENT = colors.HexColor("#2563a8")
TEXT = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#6b7280")
DIVIDER = colors.HexColor("#d1d5db")
SOFT_BG = colors.HexColor("#f3f5f8")


# ---------------------------------------------------------------------------
# Page geometry
# ---------------------------------------------------------------------------

PAGE_W, PAGE_H = A4
MARGIN_X = 20 * mm
MARGIN_TOP = 18 * mm
MARGIN_BOTTOM = 18 * mm
CONTENT_W = PAGE_W - 2 * MARGIN_X
HEADSHOT_SIZE = 32 * mm


# ---------------------------------------------------------------------------
# Paragraph styles
# ---------------------------------------------------------------------------

style_name = ParagraphStyle(
    "Name",
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=26,
    textColor=NAVY,
    spaceAfter=2,
)

style_title = ParagraphStyle(
    "Title",
    fontName="Helvetica",
    fontSize=12,
    leading=15,
    textColor=ACCENT,
    spaceAfter=2,
)

style_contact = ParagraphStyle(
    "Contact",
    fontName="Helvetica",
    fontSize=9.5,
    leading=13,
    textColor=MUTED,
)

style_section = ParagraphStyle(
    "Section",
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=13,
    textColor=NAVY,
    spaceAfter=2,
)

style_subhead = ParagraphStyle(
    "Subhead",
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=13,
    textColor=NAVY,
    spaceAfter=1,
)

style_role = ParagraphStyle(
    "Role",
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=13,
    textColor=NAVY,
    spaceAfter=0,
)

style_dates = ParagraphStyle(
    "Dates",
    fontName="Helvetica-Oblique",
    fontSize=9,
    leading=12,
    textColor=MUTED,
    spaceAfter=2,
)

style_body = ParagraphStyle(
    "Body",
    fontName="Helvetica",
    fontSize=9.8,
    leading=13.4,
    textColor=TEXT,
    alignment=TA_LEFT,
    spaceAfter=0,
)

style_skill = ParagraphStyle(
    "Skill",
    fontName="Helvetica",
    fontSize=9.5,
    leading=12,
    textColor=TEXT,
    leftIndent=0,
    spaceAfter=0,
)


# ---------------------------------------------------------------------------
# Markdown parsing (tailored to cv.md, not a generic parser)
# ---------------------------------------------------------------------------

@dataclass
class CVData:
    name: str = ""
    title: str = ""
    contact: str = ""
    summary: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    education: list[tuple[str, str]] = field(default_factory=list)
    certifications: list[tuple[str, str]] = field(default_factory=list)
    experience: list[tuple[str, str, str]] = field(default_factory=list)


def _paragraphs(lines: list[str]) -> list[str]:
    paras: list[str] = []
    buf: list[str] = []
    for line in lines:
        if line.strip():
            buf.append(line.strip())
        elif buf:
            paras.append(" ".join(buf))
            buf = []
    if buf:
        paras.append(" ".join(buf))
    return paras


def _split_subsections(lines: list[str]) -> list[tuple[str, list[str]]]:
    out: list[tuple[str, list[str]]] = []
    head: str | None = None
    body: list[str] = []
    for line in lines:
        if line.startswith("### "):
            if head is not None:
                out.append((head, body))
            head = line[4:].strip()
            body = []
        else:
            body.append(line)
    if head is not None:
        out.append((head, body))
    return out


def parse_cv(md_text: str) -> CVData:
    cv = CVData()
    lines = md_text.splitlines()
    i, n = 0, len(lines)

    while i < n and not lines[i].strip():
        i += 1
    if i < n and lines[i].startswith("# "):
        cv.name = lines[i][2:].strip()
        i += 1

    while i < n and not lines[i].strip():
        i += 1
    if i < n and lines[i].strip() and not lines[i].startswith("#"):
        cv.contact = lines[i].strip()
        i += 1

    while i < n and not lines[i].strip():
        i += 1
    if i < n and lines[i].startswith("## ") and lines[i][3:].strip().lower() not in {
        "summary", "skills", "education", "certifications", "experience"
    }:
        cv.title = lines[i][3:].strip()
        i += 1

    sections: dict[str, list[str]] = {}
    current: str | None = None
    bucket: list[str] = []
    while i < n:
        line = lines[i]
        if line.startswith("## "):
            if current is not None:
                sections[current] = bucket
            current = line[3:].strip()
            bucket = []
        else:
            bucket.append(line)
        i += 1
    if current is not None:
        sections[current] = bucket

    cv.summary = _paragraphs(sections.get("Summary", []))

    cv.skills = [
        line.strip()[2:].strip()
        for line in sections.get("Skills", [])
        if line.strip().startswith("- ")
    ]

    for head, body in _split_subsections(sections.get("Education", [])):
        cv.education.append((head, " ".join(_paragraphs(body))))

    for head, body in _split_subsections(sections.get("Certifications", [])):
        cv.certifications.append((head, " ".join(_paragraphs(body))))

    for head, body in _split_subsections(sections.get("Experience", [])):
        paras = _paragraphs(body)
        dates = paras[0] if paras else ""
        description = " ".join(paras[1:]) if len(paras) > 1 else ""
        cv.experience.append((head, dates, description))

    return cv


# ---------------------------------------------------------------------------
# Inline markdown → ReportLab mini-HTML
# ---------------------------------------------------------------------------

_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD_RE = re.compile(r"\*\*([^*\n]+)\*\*")
_ITALIC_RE = re.compile(r"\*([^*\n]+)\*")
_CODE_RE = re.compile(r"`([^`\n]+)`")


def md_inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = _BOLD_RE.sub(r"<b>\1</b>", text)
    text = _ITALIC_RE.sub(r"<i>\1</i>", text)
    text = _CODE_RE.sub(r'<font face="Courier">\1</font>', text)
    text = _LINK_RE.sub(
        lambda m: f'<link href="{m.group(2)}" color="#2563a8"><u>{m.group(1)}</u></link>',
        text,
    )
    return text


# ---------------------------------------------------------------------------
# Headshot: square-crop, resize, and apply a circular alpha mask
# ---------------------------------------------------------------------------

def circular_headshot(path: Path, target_px: int = 600) -> io.BytesIO:
    img = Image.open(path).convert("RGB")
    side = min(img.size)
    left = (img.width - side) // 2
    top = (img.height - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((target_px, target_px), Image.LANCZOS)

    mask = Image.new("L", (target_px, target_px), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, target_px, target_px), fill=255)

    out = Image.new("RGBA", (target_px, target_px), (255, 255, 255, 0))
    out.paste(img, (0, 0), mask)

    buf = io.BytesIO()
    out.save(buf, format="PNG")
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------------
# Flowable builders
# ---------------------------------------------------------------------------

def header_flowable(cv: CVData) -> Flowable:
    text_cells = [
        Paragraph(md_inline(cv.name), style_name),
        Paragraph(md_inline(cv.title), style_title),
        Paragraph(md_inline(cv.contact), style_contact),
    ]

    headshot_buf = circular_headshot(HEADSHOT, target_px=600)
    photo = RLImage(headshot_buf, width=HEADSHOT_SIZE, height=HEADSHOT_SIZE)

    text_col_w = CONTENT_W - HEADSHOT_SIZE - 6 * mm
    table = Table(
        [[text_cells, photo]],
        colWidths=[text_col_w, HEADSHOT_SIZE + 6 * mm],
    )
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
        ("VALIGN", (1, 0), (1, 0), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return table


def section_header(title: str) -> list[Flowable]:
    return [
        Spacer(1, 8),
        Paragraph(title.upper(), style_section),
        HRFlowable(
            width="100%",
            thickness=0.6,
            color=ACCENT,
            spaceBefore=1,
            spaceAfter=4,
        ),
    ]


def skills_flowable(skills: list[str], cols: int = 3) -> Flowable:
    rows = [skills[i:i + cols] for i in range(0, len(skills), cols)]
    while rows and len(rows[-1]) < cols:
        rows[-1].append("")

    data = [
        [
            Paragraph(f"•&nbsp;&nbsp;{md_inline(s)}", style_skill) if s else ""
            for s in row
        ]
        for row in rows
    ]
    col_w = CONTENT_W / cols
    table = Table(data, colWidths=[col_w] * cols)
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
    ]))
    return table


# ---------------------------------------------------------------------------
# Page chrome
# ---------------------------------------------------------------------------

def draw_page_chrome(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(
        PAGE_W / 2,
        12 * mm,
        f"Page {doc.page}",
    )
    canvas.restoreState()


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_pdf(cv: CVData, output_path: Path) -> None:
    doc = BaseDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=cv.name or "CV",
        author=cv.name or "",
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc.addPageTemplates([
        PageTemplate(id="cv", frames=[frame], onPage=draw_page_chrome),
    ])

    story: list[Flowable] = []

    story.append(header_flowable(cv))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.6, color=DIVIDER))

    if cv.summary:
        story.extend(section_header("Summary"))
        for para in cv.summary:
            story.append(Paragraph(md_inline(para), style_body))
            story.append(Spacer(1, 4))

    if cv.skills:
        story.extend(section_header("Skills"))
        story.append(skills_flowable(cv.skills))

    if cv.education:
        story.extend(section_header("Education"))
        for head, body in cv.education:
            entry = [Paragraph(md_inline(head), style_subhead)]
            if body:
                entry.append(Paragraph(md_inline(body), style_body))
            entry.append(Spacer(1, 4))
            story.append(KeepTogether(entry))

    if cv.certifications:
        story.extend(section_header("Certifications"))
        for head, body in cv.certifications:
            entry = [Paragraph(md_inline(head), style_subhead)]
            if body:
                entry.append(Paragraph(md_inline(body), style_body))
            entry.append(Spacer(1, 5))
            story.append(KeepTogether(entry))

    if cv.experience:
        story.extend(section_header("Experience"))
        for head, dates, description in cv.experience:
            top_block = [Paragraph(md_inline(head), style_role)]
            if dates:
                top_block.append(Paragraph(md_inline(dates), style_dates))
            story.append(KeepTogether(top_block))
            if description:
                story.append(Paragraph(md_inline(description), style_body))
            story.append(Spacer(1, 7))

    doc.build(story)


def main() -> None:
    if not CV_MD.exists():
        raise SystemExit(f"Missing {CV_MD}")
    if not HEADSHOT.exists():
        raise SystemExit(f"Missing {HEADSHOT}")

    cv = parse_cv(CV_MD.read_text(encoding="utf-8"))
    build_pdf(cv, OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
