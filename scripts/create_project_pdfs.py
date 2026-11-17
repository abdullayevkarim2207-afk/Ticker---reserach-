"""Create the Project 2 memo and validation PDFs from their Markdown sources."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "pdf"


def ascii_text(text: str) -> str:
    replacements = {
        "\u2010": "-",
        "\u2011": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def inline_markup(text: str) -> str:
    text = ascii_text(text.strip())
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def styles():
    base = getSampleStyleSheet()
    base.add(
        ParagraphStyle(
            name="TitleCustom",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#19324D"),
            spaceAfter=14,
        )
    )
    base.add(
        ParagraphStyle(
            name="HeadingCustom",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#8A6D00"),
            spaceBefore=9,
            spaceAfter=5,
        )
    )
    base.add(
        ParagraphStyle(
            name="BodyCustom",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12.2,
            textColor=colors.HexColor("#222222"),
            spaceAfter=6,
        )
    )
    base.add(
        ParagraphStyle(
            name="NoteCustom",
            parent=base["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11,
            leftIndent=10,
            textColor=colors.HexColor("#555555"),
            borderColor=colors.HexColor("#C9B458"),
            borderWidth=0,
            borderPadding=4,
            spaceAfter=8,
        )
    )
    base.add(
        ParagraphStyle(
            name="TableHeaderCustom",
            parent=base["BodyCustom"],
            fontName="Helvetica-Bold",
            textColor=colors.white,
            spaceAfter=0,
        )
    )
    return base


def parse_markdown(path: Path, page_width: float, table_columns: int | None = None):
    style = styles()
    lines = path.read_text(encoding="utf-8").splitlines()
    story = []
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        if not line:
            index += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline_markup(line[2:]), style["TitleCustom"]))
            index += 1
            continue
        if line.startswith("## "):
            story.append(Paragraph(inline_markup(line[3:]), style["HeadingCustom"]))
            index += 1
            continue
        if line.startswith("> "):
            story.append(Paragraph(inline_markup(line[2:]), style["NoteCustom"]))
            index += 1
            continue
        if line.startswith("| "):
            raw_rows = []
            while index < len(lines) and lines[index].startswith("|"):
                raw_rows.append(lines[index])
                index += 1
            rows = []
            for row_index, raw in enumerate(raw_rows):
                cells = [cell.strip() for cell in raw.strip("|").split("|")]
                if all(re.fullmatch(r":?-+:?", cell) for cell in cells):
                    continue
                cell_style = style["TableHeaderCustom"] if row_index == 0 else style["BodyCustom"]
                rows.append(
                    [Paragraph(inline_markup(cell), cell_style) for cell in cells]
                )
            count = table_columns or len(rows[0])
            if count == 2:
                widths = [page_width * 0.18, page_width * 0.82]
            else:
                widths = [page_width / count] * count
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#19324D")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B6BDC5")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F8")]),
                    ]
                )
            )
            story.extend([table, Spacer(1, 8)])
            continue
        if line.startswith("- "):
            while index < len(lines) and lines[index].startswith("- "):
                story.append(
                    Paragraph("&#8226; " + inline_markup(lines[index][2:]), style["BodyCustom"])
                )
                index += 1
            continue
        paragraph_lines = [line]
        index += 1
        while index < len(lines) and lines[index].strip() and not lines[index].startswith(("#", ">", "|", "- ")):
            paragraph_lines.append(lines[index].strip())
            index += 1
        story.append(Paragraph(inline_markup(" ".join(paragraph_lines)), style["BodyCustom"]))
    return story


def build_pdf(source: Path, destination: Path, pagesize, table_columns: int | None = None) -> None:
    margin = 0.6 * inch
    page_width, page_height = pagesize
    frame_width = page_width - 2 * margin

    def decorate(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#C9B458"))
        canvas.line(margin, 0.42 * inch, page_width - margin, 0.42 * inch)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(margin, 0.25 * inch, "FIN 43900 Project 2 - educational use only")
        canvas.drawRightString(page_width - margin, 0.25 * inch, f"Page {doc.page}")
        canvas.restoreState()

    document = BaseDocTemplate(
        str(destination),
        pagesize=pagesize,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=0.55 * inch,
        bottomMargin=0.58 * inch,
        title=source.stem,
        author="FIN 43900 student",
    )
    frame = Frame(margin, 0.58 * inch, frame_width, page_height - 1.13 * inch, id="content")
    document.addPageTemplates(PageTemplate(id="project", frames=[frame], onPage=decorate))
    document.build(parse_markdown(source, frame_width, table_columns))


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    build_pdf(
        ROOT / "docs" / "decision-memo.md",
        OUTPUT_DIR / "project-2-decision-memo.pdf",
        letter,
        table_columns=2,
    )
    build_pdf(
        ROOT / "docs" / "validation-and-ai-use.md",
        OUTPUT_DIR / "project-2-validation-and-ai-use.pdf",
        landscape(letter),
        table_columns=5,
    )


if __name__ == "__main__":
    main()
