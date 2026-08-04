from __future__ import annotations

from pathlib import Path

from engine.config import Settings
from engine.prepare_database import prepare_database
from engine.score_players import score_players
from engine.validation import validate_project
from engine.visualization.distributions import create_position_distribution
from engine.visualization.player_card import create_top_player_cards
from engine.visualization.radar_charts import create_top_player_radars
from engine.reports.generate_top_reports import generate_top_reports
from engine.reports.report_builder import safe_filename


def _print_generated_radars(generated_radars: list[dict[str, Path]]) -> None:
    """Display the generated radar chart files in the terminal."""

    print(f"Radar charts created: {len(generated_radars)}")

    for radar_files in generated_radars:
        png_path = radar_files["png"]
        print(f"- {png_path.name}")


def _print_generated_player_cards(generated_cards: list[Path]) -> None:
    """Display the generated player card files in the terminal."""

    print(f"Player cards created: {len(generated_cards)}")

    for card_path in generated_cards:
        print(f"- {card_path.name}")


def run_pipeline(settings: Settings) -> None:
    """Run the complete ScoutVision pipeline."""

    print("=" * 68)
    print("SCOUTVISION V1.3")
    print("=" * 68)

    validate_project(settings)

    print(f"Competition: {settings.competition_name}")
    print(f"Maximum age: {settings.max_age}")
    print(f"Minimum matches: {settings.minimum_matches}")
    print(f"Database: {settings.database_file}")

    print("\n[1/4] Preparing database...")

    preparation_summary = prepare_database(settings)

    print("Database prepared successfully.")
    print(
        f"Original players: "
        f"{preparation_summary['original_players']}"
    )
    print(
        f"U25 outfield players: "
        f"{preparation_summary['u25_outfield_players']}"
    )
    print(
        f"Main ranking pool: "
        f"{preparation_summary['main_ranking_players']}"
    )
    print(
        f"Emerging watchlist: "
        f"{preparation_summary['watchlist_players']}"
    )
    print(
        f"Insufficient sample: "
        f"{preparation_summary['insufficient_players']}"
    )

    print(
        f"\nPrepared file created:\n"
        f"{settings.prepared_file}"
    )

    print("\n[2/4] Scoring players...")

    scoring_summary = score_players(settings)

    print("Player scoring completed.")
    print(
        f"Ranked players: "
        f"{scoring_summary['ranked_players']}"
    )
    print(
        f"Elite U21 players: "
        f"{scoring_summary['elite_u21']}"
    )
    print(
        f"Position groups: "
        f"{scoring_summary['position_groups']}"
    )

    print("\nTop player by position:")

    for position_group, information in (
        scoring_summary["top_players"].items()
    ):
        print(
            f"{position_group:8} | "
            f"{information['count']:3} players | "
            f"{information['player']} "
            f"({information['score']:.1f})"
        )

    print(
        f"\nRankings file created:\n"
        f"{settings.rankings_file}"
    )

    print("\n[3/4] Creating visualizations...")

    create_position_distribution(
        rankings_file=settings.rankings_file,
        output_folder=settings.charts_dir,
    )

    position_chart = settings.charts_dir / "position_distribution.png"
    position_data = settings.charts_dir / "position_distribution.json"

    radar_output_folder = settings.charts_dir / "radars"
    generated_radars = create_top_player_radars(
        rankings_file=settings.rankings_file,
        output_folder=radar_output_folder,
        competition_name=settings.competition_name,
    )

    player_cards_output_folder = (
        settings.base_dir / "outputs" / "player_cards"
    )
    generated_player_cards = create_top_player_cards(
        rankings_file=settings.rankings_file,
        output_folder=player_cards_output_folder,
        competition_name=settings.competition_name,
    )

    print("Visualizations created successfully.")
    print(
        f"Position distribution chart:\n"
        f"{position_chart}"
    )
    print(
        f"Position distribution data:\n"
        f"{position_data}"
    )
    print(
        f"Radar charts folder:\n"
        f"{radar_output_folder}"
    )
    _print_generated_radars(generated_radars)
    print(
        f"Player cards folder:\n"
        f"{player_cards_output_folder}"
    )
    _print_generated_player_cards(generated_player_cards)

    print("\n[4/4] Generating recruitment reports...")

    reports_output_root = settings.base_dir / "outputs" / "scouting_reports"
    generated_reports = generate_top_reports(
        rankings_file=settings.rankings_file,
        competition_name=settings.competition_name,
        output_root=reports_output_root,
        top_n_per_position=5,
        clear_previous=True,
    )

    print("Recruitment reports created successfully.")
    print(f"Reports created: {len(generated_reports)}")
    print(
        f"Reports folder:\n"
        f"{reports_output_root / safe_filename(settings.competition_name)}"
    )

    print("\n" + "=" * 68)
    print("SCOUTVISION PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 68)
