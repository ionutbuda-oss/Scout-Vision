"""Run only database preparation and scoring for engine validation."""

from __future__ import annotations

from engine.config import Settings
from engine.prepare_database import prepare_database
from engine.score_players import score_players
from engine.validation import validate_project


def main() -> None:
    settings = Settings()
    validate_project(settings)

    print("=" * 68)
    print("SCOUTVISION — BELGIUM ENGINE VALIDATION")
    print("=" * 68)
    print(f"Competition: {settings.competition_name}")
    print(f"Database: {settings.database_file}")
    print("Position mapping: first Wyscout position token")
    print("DM terminology: Ball Security")

    preparation = prepare_database(settings)
    scoring = score_players(settings)

    print("\nDatabase prepared and scored successfully.")
    print(f"Original players: {preparation['original_players']}")
    print(f"U25 outfield players: {preparation['u25_outfield_players']}")
    print(f"Main ranking pool: {preparation['main_ranking_players']}")
    print(f"Emerging watchlist: {preparation['watchlist_players']}")
    print(f"Insufficient sample: {preparation['insufficient_players']}")
    print(f"Ranked players: {scoring['ranked_players']}")

    print("\nTop player by position:")
    for group, item in scoring["top_players"].items():
        print(
            f"{group:8} | {item['count']:3} players | "
            f"{item['player']} ({item['score']:.1f})"
        )

    print(f"\nPrepared file:\n{settings.prepared_file}")
    print(f"\nRankings file:\n{settings.rankings_file}")
    print("\nNo cards or PDF reports were generated in this validation run.")
    print("=" * 68)


if __name__ == "__main__":
    main()
