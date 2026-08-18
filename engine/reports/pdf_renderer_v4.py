from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor


PAGE_W, PAGE_H = A4




def draw_card(c, x, y, w, h, fill="#102B4C"):
    c.setFillColor(HexColor(fill))
    c.roundRect(
        x,
        y,
        w,
        h,
        8,
        fill=1,
        stroke=0
    )


def draw_score_card(c, x, y, title, value):
    draw_card(c, x, y, 150, 90)

    c.setFillColor(HexColor("#00C2FF"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(
        x + 15,
        y + 65,
        title
    )

    c.setFillColor("white")
    c.setFont(
        "Helvetica-Bold",
        28
    )
    c.drawString(
        x + 15,
        y + 25,
        f"{float(value):.1f}"
    )


def draw_section_title(c, title, y):
    c.setFillColor(HexColor("#00C2FF"))
    c.setFont(
        "Helvetica-Bold",
        16
    )
    c.drawString(
        50,
        y,
        title
    )




def draw_metric_row(c, x, y, label, value, percentile):
    """
    Single KPI row inside competency card
    """

    c.setFillColor(HexColor("#D8E5F2"))
    c.setFont("Helvetica", 8)
    c.drawString(
        x,
        y,
        label
    )

    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(
        x + 170,
        y,
        str(value)
    )

    # percentile
    c.setFillColor(HexColor("#00C2FF"))
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(
        x + 215,
        y,
        f"P{percentile}"
    )

    # bar
    c.setStrokeColor(HexColor("#314B66"))
    c.line(
        x,
        y - 7,
        x + 210,
        y - 7
    )

    c.setStrokeColor(HexColor("#00C2FF"))
    c.line(
        x,
        y - 7,
        x + (210 * float(percentile) / 100),
        y - 7
    )


def draw_competency_card(c, x, y, title, weight, metrics):
    """
    Competency block matching ScoutVision design
    """

    width = 250
    height = 190

    c.setFillColor(HexColor("#102B4C"))
    c.roundRect(
        x,
        y,
        width,
        height,
        8,
        fill=1,
        stroke=0
    )

    c.setFillColor(HexColor("#00C2FF"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(
        x + 12,
        y + height - 20,
        title.upper()
    )

    c.setFillColor(HexColor("#9FB7D0"))
    c.setFont("Helvetica", 7)
    c.drawString(
        x + 12,
        y + height - 35,
        f"Competency weight {weight}%"
    )

    current_y = y + height - 60

    for metric in metrics:
        draw_metric_row(
            c,
            x + 12,
            current_y,
            metric["name"],
            metric["value"],
            metric["percentile"]
        )

        current_y -= 25




def draw_percentile_guide(c, x, y):

    width = 480
    height = 90

    c.setFillColor(HexColor("#102B4C"))
    c.roundRect(
        x,
        y,
        width,
        height,
        8,
        fill=1,
        stroke=0
    )

    c.setFillColor(HexColor("#00C2FF"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(
        x + 15,
        y + 65,
        "Percentile Guide"
    )

    items = [
        ("P90-P100", "Elite", "#22C55E"),
        ("P75-P89", "Above average", "#06B6D4"),
        ("P50-P74", "Average to good", "#F59E0B"),
        ("P0-P49", "Development area", "#F97316"),
    ]

    start_x = x + 15

    for percentile, label, color in items:

        c.setFillColor(HexColor(color))
        c.circle(
            start_x,
            y + 35,
            5,
            fill=1,
            stroke=0
        )

        c.setFillColor("white")
        c.setFont("Helvetica", 8)
        c.drawString(
            start_x + 12,
            y + 30,
            f"{percentile} {label}"
        )

        start_x += 115




def draw_info_card(c, x, y, title, value):

    c.setFillColor(HexColor("#102B4C"))
    c.roundRect(
        x,
        y,
        110,
        55,
        8,
        fill=1,
        stroke=0
    )

    c.setFillColor(HexColor("#00C2FF"))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(
        x + 10,
        y + 38,
        title
    )

    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(
        x + 10,
        y + 15,
        str(value)
    )


def draw_score_panel(c, x, y, score):

    c.setFillColor(HexColor("#102B4C"))
    c.roundRect(
        x,
        y,
        180,
        120,
        10,
        fill=1,
        stroke=0
    )

    c.setFillColor(HexColor("#00C2FF"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(
        x + 15,
        y + 90,
        "SCOUT SCORE"
    )

    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 34)
    c.drawString(
        x + 15,
        y + 45,
        f"{float(score):.1f}"
    )

    c.setStrokeColor(HexColor("#00C2FF"))
    c.line(
        x + 15,
        y + 25,
        x + 15 + (140 * float(score)/100),
        y + 25
    )


def draw_section_box(c, x, y, title, text):

    c.setFillColor(HexColor("#102B4C"))
    c.roundRect(
        x,
        y,
        480,
        80,
        8,
        fill=1,
        stroke=0
    )

    c.setFillColor(HexColor("#00C2FF"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(
        x + 15,
        y + 55,
        title
    )

    c.setFillColor("white")
    c.setFont("Helvetica", 10)
    c.drawString(
        x + 15,
        y + 30,
        str(text)[:90]
    )



def draw_identity_card(c, x, y, profile, score):

    c.setFillColor(HexColor("#102B4C"))
    c.roundRect(
        x, y, 230, 130, 10,
        fill=1,
        stroke=0
    )

    c.setFillColor(HexColor("#00C2FF"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(
        x + 15,
        y + 105,
        "PRIMARY IDENTITY"
    )

    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(
        x + 15,
        y + 70,
        profile.title
    )

    c.setFont("Helvetica-Bold", 24)
    c.drawString(
        x + 15,
        y + 35,
        f"{float(score):.1f}"
    )


def draw_summary_card(c, x, y, summary):

    c.setFillColor(HexColor("#102B4C"))
    c.roundRect(
        x, y, 480, 150, 10,
        fill=1,
        stroke=0
    )

    c.setFillColor(HexColor("#00C2FF"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(
        x + 15,
        y + 125,
        "EXECUTIVE SUMMARY"
    )

    c.setFillColor("white")
    c.setFont("Helvetica", 10)

    words = str(summary).split()

    lines = []
    current = ""

    for word in words:
        test = current + " " + word

        if len(test) > 62:
            lines.append(current.strip())
            current = word
        else:
            current = test

    if current:
        lines.append(current.strip())

    yy = y + 100

    for line in lines:
        c.drawString(
            x + 15,
            yy,
            line
        )
        yy -= 14


def draw_development_card(c, x, y, development):

    c.setFillColor(HexColor("#102B4C"))
    c.roundRect(
        x, y, 230, 100, 10,
        fill=1,
        stroke=0
    )

    c.setFillColor(HexColor("#00C2FF"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(
        x + 15,
        y + 75,
        "DEVELOPMENT FOCUS"
    )

    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(
        x + 15,
        y + 45,
        development["name"]
    )

    c.setFont("Helvetica", 12)
    c.drawString(
        x + 15,
        y + 22,
        f"Score: {development['score_display']}/100"
    )


def render_pdf_v4(output_path: Path, context: dict) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=A4)

    # -----------------
    # -----------------
    # PAGE 1 - PLAYER PROFILE
    # -----------------

    player = context["player"]
    score = context["score"]

    c.setFillColor(HexColor("#071A33"))
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Header

    c.setFillColor(HexColor("#00C2FF"))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(
        50,
        PAGE_H - 70,
        "SCOUTVISION"
    )

    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 26)
    c.drawString(
        50,
        PAGE_H - 130,
        player["name"]
    )

    c.setFont("Helvetica", 12)
    c.drawString(
        50,
        PAGE_H - 160,
        f"{player['team']} | {player['position_group']} | Age {player['age']}"
    )


    # Score panel

    draw_score_panel(
        c,
        360,
        PAGE_H - 220,
        score["value"]
    )


    # Information cards

    draw_info_card(
        c, 50, PAGE_H - 260,
        "MINUTES",
        player["minutes"]
    )

    draw_info_card(
        c, 180, PAGE_H - 260,
        "MATCHES",
        player["matches"]
    )

    draw_info_card(
        c, 310, PAGE_H - 260,
        "COMPETITION",
        player["competition"]
    )


    # Profile sections

    draw_section_box(
        c,
        50,
        PAGE_H - 390,
        "POSITION PROFILE",
        f"{player['position_group']} | {player['position']}"
    )


    draw_identity_card(
        c,
        50,
        PAGE_H - 550,
        context["player_dna"]["primary_profile"],
        context["player_dna"]["primary_score"]
    )


    draw_development_card(
        c,
        300,
        PAGE_H - 520,
        context["development"]
    )


    draw_summary_card(
        c,
        50,
        PAGE_H - 690,
        context["executive_summary"]
    )


    c.showPage()


    # -----------------
    # -----------------
    # PAGE 2 - POSITION MODEL INDICATORS
    # -----------------

    c.setFillColor(HexColor("#071A33"))
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(
        50,
        PAGE_H - 70,
        "Position Model Indicators"
    )

    groups = context["kpi_groups"]

    positions = [
        (50, PAGE_H - 300),
        (320, PAGE_H - 300),
        (50, PAGE_H - 550),
        (320, PAGE_H - 550),
    ]

    for group, pos in zip(groups, positions):

        metrics = []

        for metric in group["metrics"]:
            metrics.append({
                "name": metric["name"],
                "value": metric["value"],
                "percentile": metric["percentile"],
            })

        draw_competency_card(
            c,
            pos[0],
            pos[1],
            group["name"],
            group["weight"],
            metrics,
        )


    draw_percentile_guide(
        c,
        50,
        60
    )

    c.showPage()


    # -----------------
    # PAGE 3
    # -----------------
    c.setFillColor(HexColor("#071A33"))
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(
        50,
        PAGE_H - 70,
        "Tactical Fit"
    )

    c.setFont("Helvetica", 12)
    c.drawString(
        50,
        PAGE_H - 110,
        "Formation & role suitability"
    )

    c.save()

    return output_path
