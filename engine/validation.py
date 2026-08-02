from __future__ import annotations

from engine.config import Settings


def validate_project(settings: Settings) -> None:
    required_directories = [
        settings.base_dir / "databases",
        settings.base_dir / "engine",
        settings.base_dir / "outputs" / "prepared",
        settings.base_dir / "outputs" / "rankings",
        settings.base_dir / "outputs" / "reports",
        settings.base_dir / "outputs" / "charts",
        settings.base_dir / "templates",
    ]

    for directory in required_directories:
        directory.mkdir(parents=True, exist_ok=True)

    if not settings.database_file.exists():
        raise FileNotFoundError(
            "\nBaza de date nu a fost găsită.\n"
            f"Copiază L3-France.xlsx în:\n{settings.database_file.parent}\n"
        )
