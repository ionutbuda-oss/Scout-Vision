from pathlib import Path
from jinja2 import Environment,FileSystemLoader,select_autoescape
from playwright.sync_api import sync_playwright

def render_html(template_path:Path,context:dict,output_path:Path)->Path:
    env=Environment(loader=FileSystemLoader(str(template_path.parent)),autoescape=select_autoescape(["html"]))
    output_path.parent.mkdir(parents=True,exist_ok=True)
    output_path.write_text(env.get_template(template_path.name).render(**context),encoding="utf-8")
    return output_path

def render_png(html_path:Path,output_path:Path)->Path:
    output_path.parent.mkdir(parents=True,exist_ok=True)
    html=html_path.read_text(encoding="utf-8")
    css_path=Path(__file__).resolve().parent/"templates"/"player_card.css"
    css=css_path.read_text(encoding="utf-8")
    html=html.replace('<link rel="stylesheet" href="player_card.css">',f"<style>{css}</style>")
    with sync_playwright() as p:
        try: browser=p.chromium.launch()
        except Exception: browser=p.chromium.launch(executable_path="/usr/bin/chromium",args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1280,"height":1800},device_scale_factor=1)
        page.set_content(html,wait_until="networkidle")
        page.locator(".player-card").screenshot(path=str(output_path),animations="disabled")
        browser.close()
    return output_path
