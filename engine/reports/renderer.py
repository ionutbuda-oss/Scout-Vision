"""HTML and PDF renderer for ScoutVision recruitment reports."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright


class ReportRenderError(RuntimeError):
    """Raised when Chromium cannot create the report."""


def render_html(template_path: Path, context: dict, output_path: Path) -> Path:
    environment = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = environment.get_template(template_path.name)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template.render(**context), encoding="utf-8")
    return output_path


def _standalone_html(html_path: Path) -> str:
    html = html_path.read_text(encoding="utf-8")
    css_path = Path(__file__).resolve().parent / "templates" / "recruitment_report.css"
    css = css_path.read_text(encoding="utf-8")
    return html.replace(
        '<link rel="stylesheet" href="recruitment_report.css">',
        f"<style>{css}</style>",
    )


def render_pdf(html_path: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1240, "height": 1754}, device_scale_factor=1)
            page.set_content(_standalone_html(html_path), wait_until="networkidle")
            page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
            browser.close()
    except Exception as exc:
        raise ReportRenderError(
            "PDF rendering failed. Install Chromium with: "
            "python3 -m playwright install chromium"
        ) from exc
    return output_path
