"""
03_find_transfermarkt_profile_paste_link.py

Identifică profilurile Transfermarkt prin căutare web contextuală.

Flux:
1. Scriptul deschide Google pentru jucătorul curent.
2. Deschizi profilul corect Transfermarkt.
3. Copiezi URL-ul din browser.
4. Lipești URL-ul direct în Terminal și apeși Enter.
5. Scriptul validează și salvează automat linkul.

Comenzi:
- lipește un URL Transfermarkt valid = salvează și continuă
- R = caută din nou cu alt text
- O = redeschide căutarea inițială
- 0 = profil negăsit
- S = sari peste jucător
- Q = salvează și închide
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote_plus, urlparse
import sys
import time

import pandas as pd
from playwright.sync_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "player_identification_queue.xlsx"
OUTPUT_FILE = BASE_DIR / "player_profiles_progress.xlsx"

# Lasă None pentru toți jucătorii.
# Pentru test poți pune 10.
TEST_LIMIT: int | None = None

GOOGLE_SEARCH_URL = "https://www.google.com/search?q={query}"

FINISHED_STATUSES = {
    "confirmed",
    "confirmat",
    "not found",
    "not_found",
    "negăsit",
    "negasit",
}


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().split())


def first_existing_column(
    df: pd.DataFrame,
    candidates: list[str],
) -> str | None:
    lookup = {str(column).strip().lower(): str(column) for column in df.columns}

    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]

    return None


def ensure_output_columns(df: pd.DataFrame) -> pd.DataFrame:
    defaults = {
        "Transfermarkt URL": "",
        "Identity status": "",
        "Identity notes": "",
        "Search query used": "",
        "Checked at": "",
    }

    for column, default in defaults.items():
        if column not in df.columns:
            df[column] = default

        # Forțează coloanele de progres să fie text.
        # Excel/pandas poate interpreta o coloană goală drept float64,
        # ceea ce împiedică ulterior salvarea unui URL.
        df[column] = df[column].fillna("").astype("string")

    return df


def load_data() -> pd.DataFrame:
    source = OUTPUT_FILE if OUTPUT_FILE.exists() else INPUT_FILE

    if not source.exists():
        raise FileNotFoundError(
            f"\nNu găsesc {INPUT_FILE.name} în folderul:\n{BASE_DIR}\n"
        )

    df = pd.read_excel(source)

    if df.empty:
        raise ValueError(f"Fișierul {source.name} nu conține date.")

    player_column = first_existing_column(
        df,
        ["Player", "Player name", "Name", "Jucător", "Jucator"],
    )

    if player_column is None:
        raise ValueError(
            "Nu găsesc o coloană pentru numele jucătorului.\n"
            f"Coloane existente: {list(df.columns)}"
        )

    if player_column != "Player":
        df = df.rename(columns={player_column: "Player"})

    return ensure_output_columns(df)


def save_data(df: pd.DataFrame) -> None:
    temporary_file = OUTPUT_FILE.with_name(
        f"{OUTPUT_FILE.stem}_temporary{OUTPUT_FILE.suffix}"
    )
    df.to_excel(temporary_file, index=False)
    temporary_file.replace(OUTPUT_FILE)


def build_contextual_query(
    row: pd.Series,
    team_column: str | None,
    season_column: str | None,
    position_column: str | None,
) -> str:
    player = normalize_text(row.get("Player", ""))
    team = normalize_text(row.get(team_column, "")) if team_column else ""
    season = normalize_text(row.get(season_column, "")) if season_column else ""
    position = (
        normalize_text(row.get(position_column, ""))
        if position_column
        else ""
    )

    parts = [
        f'"{player}"',
        f'"{team}"' if team else "",
        position,
        season,
        "footballer",
        "Transfermarkt",
    ]

    return " ".join(part for part in parts if part)


def build_google_url(query: str) -> str:
    return GOOGLE_SEARCH_URL.format(query=quote_plus(query))


def clean_pasted_url(value: str) -> str:
    value = value.strip()

    # Uneori terminalul poate primi URL-ul între ghilimele.
    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in {'"', "'"}
    ):
        value = value[1:-1].strip()

    return value


def is_valid_transfermarkt_profile(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    hostname = (parsed.hostname or "").lower()
    path = parsed.path.lower()

    return (
        parsed.scheme in {"http", "https"}
        and "transfermarkt." in hostname
        and "/profil/spieler/" in path
    )


def display_context(
    row: pd.Series,
    number: int,
    total: int,
    team_column: str | None,
    season_column: str | None,
    age_column: str | None,
    position_column: str | None,
) -> None:
    print("\n" + "=" * 72)
    print(f"JUCĂTOR {number}/{total}")
    print("=" * 72)
    print(f"Nume:      {normalize_text(row.get('Player', ''))}")

    if team_column:
        print(f"Echipă:    {normalize_text(row.get(team_column, ''))}")
    if season_column:
        print(f"Sezon:     {normalize_text(row.get(season_column, ''))}")
    if age_column:
        print(f"Vârstă:    {normalize_text(row.get(age_column, ''))}")
    if position_column:
        print(f"Poziție:   {normalize_text(row.get(position_column, ''))}")


def print_instructions() -> None:
    print(
        "\nLipește linkul profilului Transfermarkt și apasă Enter.\n"
        "Alte comenzi:\n"
        "  R = caută din nou cu alt text\n"
        "  O = redeschide căutarea inițială\n"
        "  0 = profil negăsit\n"
        "  S = sari peste jucător\n"
        "  Q = salvează și închide\n"
    )


def open_search(page, query: str) -> None:
    try:
        page.goto(
            build_google_url(query),
            wait_until="domcontentloaded",
            timeout=60_000,
        )
    except PlaywrightTimeoutError:
        print(
            "Pagina s-a încărcat lent. "
            "Poți continua manual în browser."
        )
    except PlaywrightError as exc:
        print(f"Eroare la deschiderea căutării: {exc}")


def main() -> None:
    try:
        df = load_data()
    except Exception as exc:
        print(exc)
        sys.exit(1)

    team_column = first_existing_column(
        df,
        [
            "Current Team",
            "Current team",
            "Team",
            "Club",
            "Current club",
            "Echipă",
            "Echipa",
        ],
    )
    season_column = first_existing_column(
        df,
        ["Season", "Seasons", "Sezon"],
    )
    age_column = first_existing_column(
        df,
        ["Age", "Age_min", "Age_max", "Vârstă", "Varsta"],
    )
    position_column = first_existing_column(
        df,
        ["Position", "Poziție", "Pozitie"],
    )

    statuses = (
        df["Identity status"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    pending_indices = df.index[~statuses.isin(FINISHED_STATUSES)].tolist()

    if TEST_LIMIT is not None:
        pending_indices = pending_indices[:TEST_LIMIT]

    if not pending_indices:
        print("Nu mai există jucători neverificați.")
        print(f"Rezultatele sunt în: {OUTPUT_FILE}")
        return

    print("\nIDENTIFICARE TRANSFERMARKT PRIN LIPIREA LINKULUI")
    print(f"Intrare:  {INPUT_FILE.name}")
    print(f"Progres:  {OUTPUT_FILE.name}")
    print(f"Jucători în sesiune: {len(pending_indices)}")

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=False,
                slow_mo=100,
            )

            context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                locale="ro-RO",
            )

            page = context.new_page()
            page.set_default_timeout(20_000)

            total = len(pending_indices)

            for number, idx in enumerate(pending_indices, start=1):
                row = df.loc[idx]

                display_context(
                    row=row,
                    number=number,
                    total=total,
                    team_column=team_column,
                    season_column=season_column,
                    age_column=age_column,
                    position_column=position_column,
                )

                initial_query = build_contextual_query(
                    row=row,
                    team_column=team_column,
                    season_column=season_column,
                    position_column=position_column,
                )
                current_query = initial_query

                print(f"\nCăutare web:\n{current_query}")
                open_search(page, current_query)

                while True:
                    print_instructions()
                    user_input = input("Link sau comandă: ").strip()

                    if not user_input:
                        print("Nu ai introdus nimic.")
                        continue

                    command = user_input.lower()

                    if command == "r":
                        custom_query = input(
                            "Scrie noua căutare "
                            "(exemplu: Aly Abeid UTA Arad Transfermarkt): "
                        ).strip()

                        if not custom_query:
                            print("Căutarea nu poate fi goală.")
                            continue

                        current_query = custom_query
                        open_search(page, current_query)
                        print(f"Căutare nouă:\n{current_query}")
                        continue

                    if command == "o":
                        current_query = initial_query
                        open_search(page, current_query)
                        continue

                    if command == "0":
                        df.at[idx, "Transfermarkt URL"] = ""
                        df.at[idx, "Identity status"] = "Not found"
                        df.at[idx, "Identity notes"] = "No profile found manually"
                        df.at[idx, "Search query used"] = current_query
                        df.at[idx, "Checked at"] = pd.Timestamp.now().isoformat(
                            timespec="seconds"
                        )

                        save_data(df)
                        print("Jucător marcat drept negăsit.")
                        break

                    if command == "s":
                        df.at[idx, "Identity notes"] = "Skipped"
                        df.at[idx, "Search query used"] = current_query
                        save_data(df)
                        print("Jucător omis pentru moment.")
                        break

                    if command == "q":
                        save_data(df)
                        print(f"\nProgres salvat în:\n{OUTPUT_FILE}")
                        context.close()
                        browser.close()
                        return

                    pasted_url = clean_pasted_url(user_input)

                    if not is_valid_transfermarkt_profile(pasted_url):
                        print(
                            "\nLink invalid.\n"
                            "Trebuie să conțină un profil de forma:\n"
                            "https://www.transfermarkt.../nume/profil/spieler/123456\n"
                        )
                        continue

                    df.at[idx, "Transfermarkt URL"] = pasted_url
                    df.at[idx, "Identity status"] = "Confirmed"
                    df.at[idx, "Identity notes"] = "Confirmed by pasted URL"
                    df.at[idx, "Search query used"] = current_query
                    df.at[idx, "Checked at"] = pd.Timestamp.now().isoformat(
                        timespec="seconds"
                    )

                    save_data(df)

                    print("\nSALVAT CU SUCCES:")
                    print(pasted_url)
                    break

                time.sleep(0.5)

            save_data(df)

            print("\n" + "=" * 72)
            print("SESIUNEA S-A ÎNCHEIAT")
            print(f"Progres salvat în:\n{OUTPUT_FILE}")
            print("=" * 72)

            context.close()
            browser.close()

    except PlaywrightError as exc:
        print("\nChromium nu a putut fi pornit.")
        print("Rulează:")
        print("python3 -m playwright install chromium")
        print(f"\nDetaliu tehnic: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
