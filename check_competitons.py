from statsbombpy import sb
import pandas as pd

# Afișează toate coloanele în terminal
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

# Descarcă lista competițiilor la care ai acces
competitions = sb.competitions()

print("\nToate coloanele disponibile:")
print(competitions.columns.tolist())

print("\nCompetiții din Belgia și Cehia:")

selected = competitions[
    competitions["country_name"]
    .astype(str)
    .str.contains(
        "Belgium|Czech|Czechia",
        case=False,
        na=False
    )
]

columns_to_show = [
    "country_name",
    "competition_name",
    "competition_id",
    "season_name",
    "season_id"
]

print(selected[columns_to_show].to_string(index=False))
from statsbombpy import sb
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

competitions = sb.competitions()

search_text = (
    competitions["country_name"].fillna("").astype(str)
    + " "
    + competitions["competition_name"].fillna("").astype(str)
)

results = competitions[
    search_text.str.contains(
        "Romania|Romanian|Liga I|SuperLiga|Liga 1",
        case=False,
        na=False
    )
]

print(
    results[
        [
            "country_name",
            "competition_name",
            "competition_id",
            "season_name",
            "season_id"
        ]
    ].to_string(index=False)
)