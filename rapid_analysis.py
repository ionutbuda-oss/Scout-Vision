
from statsbombpy import sb
import pandas as pd

# 1. Log in with your club credentials (or use environment variables)
# sb.init(username="your_username", password="your_password")

# 2. Pull player season statistics for your target leagues 
# (You will need the specific competition_id and season_id from sb.competitions())
belgium_stats = sb.player_season_stats(competition_id=X, season_id=Y)
czech_stats = sb.player_season_stats(competition_id=A, season_id=B)
romania_stats = sb.player_season_stats(competition_id=W, season_id=Z)

# 3. Combine them into one master DataFrame
master_df = pd.concat([belgium_stats, czech_stats, romania_stats])

# 4. Export to a CSV file
master_df.to_csv("belgium_czech_romania_players.csv", index=False)