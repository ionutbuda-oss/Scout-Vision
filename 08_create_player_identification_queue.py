import pandas as pd
from pathlib import Path
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "transfer_template.xlsx"
OUTPUT_FILE = BASE_DIR / "player_identification_queue.xlsx"

df = pd.read_excel(INPUT_FILE)

required_columns = {
    "Player",
    "Season",
    "Age",
    "Minutes played",
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Lipsesc următoarele coloane: {sorted(missing_columns)}"
    )

# Rezumat pentru fiecare jucător
players = (
    df.groupby("Player", as_index=False)
    .agg(
        Seasons=(
            "Season",
            lambda values: ", ".join(
                sorted(set(values.astype(str)))
            ),
        ),
        Age_min=("Age", "min"),
        Age_max=("Age", "max"),
        Minutes_total=("Minutes played", "sum"),
        Observations=("Season", "count"),
    )
)

# Link de căutare. Nu extragem automat rezultate Google.
players["Search query"] = players.apply(
    lambda row: (
        f'{row["Player"]} footballer Romania '
        f'Transfermarkt {row["Seasons"]}'
    ),
    axis=1,
)

players["Google search"] = players["Search query"].apply(
    lambda query: (
        "https://www.google.com/search?q="
        + quote_plus(f"site:transfermarkt.com {query}")
    )
)

# Coloane completate în etapa de verificare
players["Full name"] = ""
players["Transfermarkt URL"] = ""
players["Identity status"] = "Unverified"
players["Identity notes"] = ""

# Ordinea coloanelor
players = players[
    [
        "Player",
        "Full name",
        "Seasons",
        "Age_min",
        "Age_max",
        "Minutes_total",
        "Observations",
        "Google search",
        "Transfermarkt URL",
        "Identity status",
        "Identity notes",
    ]
]

players = players.sort_values("Player").reset_index(drop=True)

players.to_excel(OUTPUT_FILE, index=False)

print("=" * 55)
print("Player identification queue created successfully!")
print("=" * 55)
print(f"Unique players: {len(players)}")
print(f"Output: {OUTPUT_FILE.name}")
from pathlib import Path
import sys
import pandas as pd
from playwright.sync_api import sync_playwright, Error as PlaywrightError

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "player_identification_queue.xlsx"
OUTPUT_FILE = BASE_DIR / "player_profiles_progress.xlsx"
TEST_LIMIT = 10

REQUIRED_COLUMNS = [
    "Player",
    "Google search",
    "Transfermarkt URL",
    "Identity status",
    "Identity notes",
]


def load_data() -> pd.DataFrame:
    source = OUTPUT_FILE if OUTPUT_FILE.exists() else INPUT_FILE

    if not source.exists():
        raise FileNotFoundError(
            f"Nu găsesc {INPUT_FILE.name} în folderul scriptului."
        )

    df = pd.read_excel(source)

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Lipsesc coloanele: {missing}")

    return df


def save_data(df: pd.DataFrame) -> None:
    df.to_excel(OUTPUT_FILE, index=False)


def is_transfermarkt_profile(url: str) -> bool:
    url_lower = url.lower()
    return (
        "transfermarkt." in url_lower
        and "/profil/spieler/" in url_lower
    )


def main() -> None:
    df = load_data()

    status = df["Identity status"].fillna("").astype(str).str.strip().str.lower()
    pending_indices = df.index[
        ~status.isin({"confirmed", "not found"})
    ].tolist()[:TEST_LIMIT]

    if not pending_indices:
        print("Nu mai există jucători neverificați.")
        return

    print("=" * 66)
    print(f"TEST: maximum {len(pending_indices)} jucători")
    print("Comenzi:")
    print("  Y = profil corect; salvează URL-ul paginii deschise")
    print("  N = rezultat greșit; revino în browser și caută alt profil")
    print("  0 = jucător negăsit")
    print("  S = sari peste jucător")
    print("  Q = salvează și închide")
    print("=" * 66)

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=False,
                slow_mo=100,
            )
            context = browser.new_context(
                viewport={"width": 1400, "height": 900},
                locale="ro-RO",
            )
            page = context.new_page()

            for number, idx in enumerate(pending_indices, start=1):
                row = df.loc[idx]
                player = str(row["Player"])
                search_url = str(row["Google search"])

                print("\n" + "-" * 66)
                print(f"Jucător {number}/{len(pending_indices)}: {player}")
                print(f"Sezoane: {row.get('Seasons', '')}")
                print(f"Vârstă: {row.get('Age_min', '')}–{row.get('Age_max', '')}")
                print("În browser, deschide profilul corect de Transfermarkt.")

                try:
                    page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                except PlaywrightError as exc:
                    print(f"Pagina nu s-a încărcat complet: {exc}")
                    print("Poți continua manual în browser.")

                while True:
                    command = input(
                        "\nComandă [Y/N/0/S/Q]: "
                    ).strip().lower()

                    if command == "y":
                        current_url = page.url

                        if not is_transfermarkt_profile(current_url):
                            print(
                                "Pagina deschisă nu pare un profil Transfermarkt.\n"
                                "Intră pe profilul jucătorului și apoi apasă din nou Y."
                            )
                            continue

                        df.at[idx, "Transfermarkt URL"] = current_url
                        df.at[idx, "Identity status"] = "Confirmed"
                        df.at[idx, "Identity notes"] = "Confirmed manually"
                        save_data(df)
                        print(f"Salvat: {current_url}")
                        break

                    if command == "n":
                        print(
                            "Rezultatul nu a fost salvat. Caută alt profil "
                            "în aceeași fereastră."
                        )
                        continue

                    if command == "0":
                        df.at[idx, "Transfermarkt URL"] = ""
                        df.at[idx, "Identity status"] = "Not found"
                        df.at[idx, "Identity notes"] = "No profile found manually"
                        save_data(df)
                        print("Marcat ca negăsit.")
                        break

                    if command == "s":
                        df.at[idx, "Identity notes"] = "Skipped during test"
                        save_data(df)
                        print("Jucător omis.")
                        break

                    if command == "q":
                        save_data(df)
                        print(f"Progres salvat în: {OUTPUT_FILE.name}")
                        context.close()
                        browser.close()
                        return

                    print("Comandă invalidă. Folosește Y, N, 0, S sau Q.")

            save_data(df)
            print("\n" + "=" * 66)
            print("Testul s-a terminat.")
            print(f"Rezultatele sunt în: {OUTPUT_FILE.name}")
            print("=" * 66)

            context.close()
            browser.close()

    except PlaywrightError as exc:
        print("\nPlaywright nu a putut porni Chromium.")
        print("Rulează în Terminal:")
        print("python3 -m playwright install chromium")
        print(f"\nDetaliu tehnic: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()