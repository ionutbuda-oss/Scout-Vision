from pathlib import Path

from engine.reports.renderer import render_pdf


HTML_FILE = Path(
    "outputs/recruitment_boards/Serbia_1_ALL_Recruitment_Board_V3.html"
)

PDF_FILE = Path(
    "outputs/recruitment_boards/Serbia_1_ALL_Recruitment_Board_V3.pdf"
)


def main():

    render_pdf(
        HTML_FILE,
        PDF_FILE
    )

    print("✅ Serbia 1 ALL Recruitment Board PDF generated")
    print(PDF_FILE)


if __name__ == "__main__":
    main()
