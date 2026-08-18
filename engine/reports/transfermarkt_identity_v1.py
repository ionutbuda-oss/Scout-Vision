from pathlib import Path
import re
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
FILE = BASE / "outputs/global_scoutvision/scoutvision_romania_transfermarkt_identity_v1.xlsx"

def get_id(url):
    m = re.search(r"/profil/spieler/(\d+)", url)
    return m.group(1) if m else ""

df = pd.read_excel(FILE, sheet_name="Transfermarkt Identity", dtype=str)

for i, row in df.iterrows():

    if str(row["Verification Status"]).upper() == "CONFIRMED":
        continue

    player = row["Player"]
    team = row["Team"]
    position = row["Position"]

    print("\n" + "=" * 90)
    print(f"PLAYER   : {player}")
    print(f"TEAM     : {team}")
    print(f"POSITION : {position}")
    print("=" * 90)

    while True:
        url = input("Paste Transfermarkt URL [0=NOT FOUND / S=SKIP / Q=QUIT]: ").strip()

        if url.upper() == "Q":
            df.to_excel(FILE, sheet_name="Transfermarkt Identity", index=False)
            print("PROGRESS SAVED.")
            raise SystemExit

        if url.upper() == "S":
            break

        if url == "0":
            df.at[i, "Verification Status"] = "NOT FOUND"
            df.at[i, "Verification Notes"] = "Not found manually"
            df.to_excel(FILE, sheet_name="Transfermarkt Identity", index=False)
            print("NOT FOUND — saved.")
            break

        if "/profil/spieler/" not in url or "transfermarkt." not in url:
            print("❌ Nu este un URL valid de profil Transfermarkt.")
            continue

        tm_id = get_id(url)

        if not tm_id:
            print("❌ Nu am putut extrage Transfermarkt ID.")
            continue

        df.at[i, "Transfermarkt URL"] = url
        df.at[i, "Transfermarkt ID"] = tm_id
        df.at[i, "Verification Status"] = "CONFIRMED"
        df.at[i, "Verification Notes"] = "Confirmed by pasted URL"

        df.to_excel(FILE, sheet_name="Transfermarkt Identity", index=False)

        print(f"✅ CONFIRMED — TM ID: {tm_id}")
        break

print("\n" + "=" * 90)
print("IDENTITY ENGINE FINISHED")
print("=" * 90)
print(df["Verification Status"].value_counts().to_string())
print(f"\nOUTPUT: {FILE}")
