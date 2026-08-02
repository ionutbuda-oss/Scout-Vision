import warnings
warnings.filterwarnings("ignore")

from statsbombpy import sb
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


# ==========================
# OUT-DEGREE CENTRALIZATION
# ==========================

def out_degree_centralization(G):
    n = len(G.nodes())

    if n <= 2:
        return 0

    out_cent = nx.out_degree_centrality(G)
    max_cent = max(out_cent.values())

    numerator = sum(max_cent - v for v in out_cent.values())
    denominator = n - 2

    return numerator / denominator


# ==========================
# BUILD PASSING NETWORK
# ==========================

def build_passing_network(match_ids, team_name):
    all_passes = []

    for match_id in match_ids:
        events = sb.events(match_id=match_id)

        passes = events[
            (events["team"] == team_name)
            & (events["type"] == "Pass")
            & (events["pass_outcome"].isna())
        ]

        passes = passes[["player", "pass_recipient"]].dropna()
        all_passes.append(passes)

    passes_df = pd.concat(all_passes)

    pass_counts = (
        passes_df
        .groupby(["player", "pass_recipient"])
        .size()
        .reset_index(name="weight")
    )

    G = nx.DiGraph()

    for _, row in pass_counts.iterrows():
        G.add_edge(
            row["player"],
            row["pass_recipient"],
            weight=row["weight"]
        )

    return G, pass_counts


# ==========================
# LOAD WORLD CUP 2022 DATA
# ==========================

matches = sb.matches(
    competition_id=43,
    season_id=106
)


# ==========================
# ARGENTINA
# ==========================

arg_matches = matches[
    (matches["home_team"] == "Argentina") |
    (matches["away_team"] == "Argentina")
]

arg_group_ids = arg_matches[
    arg_matches["competition_stage"] == "Group Stage"
]["match_id"].tolist()

arg_knockout_ids = arg_matches[
    arg_matches["competition_stage"] != "Group Stage"
]["match_id"].tolist()

G_arg_group, arg_group_passes = build_passing_network(
    arg_group_ids,
    "Argentina"
)

G_arg_knockout, arg_knockout_passes = build_passing_network(
    arg_knockout_ids,
    "Argentina"
)


# ==========================
# FRANCE
# ==========================

fra_matches = matches[
    (matches["home_team"] == "France") |
    (matches["away_team"] == "France")
]

fra_group_ids = fra_matches[
    fra_matches["competition_stage"] == "Group Stage"
]["match_id"].tolist()

fra_knockout_ids = fra_matches[
    fra_matches["competition_stage"] != "Group Stage"
]["match_id"].tolist()

G_fra_group, fra_group_passes = build_passing_network(
    fra_group_ids,
    "France"
)

G_fra_knockout, fra_knockout_passes = build_passing_network(
    fra_knockout_ids,
    "France"
)


# ==========================
# PRINT RESULTS
# ==========================

print("\nARGENTINA")
print("Group Successful Passes:", arg_group_passes["weight"].sum())
print("Knockout Successful Passes:", arg_knockout_passes["weight"].sum())
print("Group Density:", round(nx.density(G_arg_group), 3))
print("Knockout Density:", round(nx.density(G_arg_knockout), 3))
print("Group Out-Degree Centralization:", round(out_degree_centralization(G_arg_group), 3))
print("Knockout Out-Degree Centralization:", round(out_degree_centralization(G_arg_knockout), 3))

print("\nFRANCE")
print("Group Successful Passes:", fra_group_passes["weight"].sum())
print("Knockout Successful Passes:", fra_knockout_passes["weight"].sum())
print("Group Density:", round(nx.density(G_fra_group), 3))
print("Knockout Density:", round(nx.density(G_fra_knockout), 3))
print("Group Out-Degree Centralization:", round(out_degree_centralization(G_fra_group), 3))
print("Knockout Out-Degree Centralization:", round(out_degree_centralization(G_fra_knockout), 3))


# ==========================
# CHECK FRANCE GROUP VALUES
# ==========================

print("\nFRANCE GROUP - OUT-DEGREE CENTRALITY")
for player, value in nx.out_degree_centrality(G_fra_group).items():
    print(player, round(value, 3))


# ==========================
# BAR CHART
# ==========================

teams_stages = [
    "Argentina\nGroup",
    "Argentina\nKnockout",
    "France\nGroup",
    "France\nKnockout"
]

centralization_values = [
    round(out_degree_centralization(G_arg_group), 3),
    round(out_degree_centralization(G_arg_knockout), 3),
    round(out_degree_centralization(G_fra_group), 3),
    round(out_degree_centralization(G_fra_knockout), 3)
]

plt.figure(figsize=(8, 5))
plt.bar(teams_stages, centralization_values)

plt.title("Out-Degree Centralization by Team and Competition Stage")
plt.ylabel("Out-Degree Centralization")
plt.ylim(0, 1)

for i, value in enumerate(centralization_values):
    plt.text(i, value + 0.02, f"{value:.3f}", ha="center")

plt.tight_layout()
plt.savefig("out_degree_centralization_comparison.png", dpi=300)
plt.show()
# ==========================
# CLOSENESS CENTRALITY
# ==========================

def out_closeness_centrality(G):
    return nx.closeness_centrality(G.reverse())

print("\nARGENTINA GROUP - OUT-CLOSENESS")
for player, value in out_closeness_centrality(G_arg_group).items():
    print(player, round(value, 3))

print("\nARGENTINA KNOCKOUT - OUT-CLOSENESS")
for player, value in out_closeness_centrality(G_arg_knockout).items():
    print(player, round(value, 3))

print("\nFRANCE GROUP - OUT-CLOSENESS")
for player, value in out_closeness_centrality(G_fra_group).items():
    print(player, round(value, 3))

print("\nFRANCE KNOCKOUT - OUT-CLOSENESS")
for player, value in out_closeness_centrality(G_fra_knockout).items():
    print(player, round(value, 3))