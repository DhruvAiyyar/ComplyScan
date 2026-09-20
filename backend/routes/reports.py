"""
ComplyScan - PDF Report API

Provides:
    GET /api/report/{scan_id}/pdf
"""

from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Scan


router = APIRouter(
    prefix="/api/report",
    tags=["Reports"]
)


@router.get("/{scan_id}/pdf")
def generate_report(
    scan_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate a PDF compliance report for a scan.
    """

    # Find scan
    scan = (
        db.query(Scan)
        .filter(Scan.id == scan_id)
        .first()
    )

    if scan is None:
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )

    # --------------------------------------------------------
    # IMPORT REPORTLAB
    # --------------------------------------------------------

    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )

    # --------------------------------------------------------
    # CREATE PDF IN MEMORY
    # --------------------------------------------------------

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    story = []

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "COMPLYSCAN",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            "Packaged Commodity Label Compliance Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 15))

    # --------------------------------------------------------
    # SCAN INFORMATION
    # --------------------------------------------------------

    status = scan.overall_status.upper()

    scan_info = [
        ["Scan ID", str(scan.id)],
        ["Overall Status", status],
        ["Timestamp", str(scan.timestamp)],
    ]

    table = Table(
        scan_info,
        colWidths=[140, 330]
    )

    table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(table)
    story.append(Spacer(1, 20))

    # --------------------------------------------------------
    # EXTRACTED TEXT
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Extracted Text",
            styles["Heading2"]
        )
    )

    extracted_text = scan.extracted_text or "No extracted text available."

    # Convert new lines into HTML line breaks.
    extracted_text = extracted_text.replace(
        "\n",
        "<br/>"
    )

    story.append(
        Paragraph(
            extracted_text,
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 20))

    # --------------------------------------------------------
    # RULE RESULTS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Compliance Rule Results",
            styles["Heading2"]
        )
    )

    rule_data = [
        ["Rule", "Status", "Details"]
    ]

    for result in scan.rule_results:

        rule_data.append([
            result.rule_name,
            result.status.upper(),
            result.detail or ""
        ])

    rule_table = Table(
        rule_data,
        colWidths=[150, 70, 250],
        repeatRows=1
    )

    rule_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(rule_table)

    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    document.build(story)

    buffer.seek(0)

    filename = f"complyscan_report_{scan.id}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
