from dataclasses import dataclass
from pathlib import Path

from engine.config import Settings
from engine.prepare_database import prepare_database
from engine.score_players import score_players


@dataclass(frozen=True)
class SerbiaAllPlayersSettings(Settings):
    competition_name: str = "Serbia 1"
    input_filename: str = "Liga 1-Serbia.xlsx"
    max_age: int = 99
    minimum_matches: int = 10

    @property
    def prepared_file(self) -> Path:
        return (
            self.base_dir
            / "outputs"
            / "prepared"
            / "Serbia_1_ALL_prepared.xlsx"
        )

    @property
    def rankings_file(self) -> Path:
        return (
            self.base_dir
            / "outputs"
            / "rankings"
            / "Serbia_1_ALL_rankings.xlsx"
        )

    @property
    def report_file(self) -> Path:
        return (
            self.base_dir
            / "outputs"
            / "reports"
            / "Serbia_1_ALL_Scouting_Report.pdf"
        )


def main():
    settings = SerbiaAllPlayersSettings()

    print("=" * 70)
    print("SCOUTVISION — SERBIA 1 ALL PLAYERS")
    print("=" * 70)

    print(f"Database: {settings.database_file}")
    print(f"Maximum age: {settings.max_age}")
    print(f"Minimum matches: {settings.minimum_matches}")

    print("\n[1/2] Preparing database...")
    result = prepare_database(settings)

    print("\nPreparation complete:")
    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n[2/2] Scoring all players...")
    scoring_result = score_players(settings)

    print("\n" + "=" * 70)
    print("SERBIA 1 ALL-PLAYER RANKING COMPLETE")
    print("=" * 70)
    print(f"Rankings: {settings.rankings_file}")

    if isinstance(scoring_result, dict):
        for key, value in scoring_result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
