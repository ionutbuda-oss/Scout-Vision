"""
ScoutVision V3 - Player Archetype Generator

Transforms internal competency profiles into
club-facing scouting archetypes.
"""


def generate_player_archetype(
    *,
    position_group: str,
    competencies: list[dict],
) -> str:

    scores = {
        item["name"]: float(item["score"])
        for item in competencies
    }

    # STRIKERS
    if position_group == "ST":

        if scores.get("Box Threat", 0) >= 85:
            return "BOX STRIKER"

        if scores.get("Finishing", 0) >= 85:
            return "CLINICAL FINISHER"

        if scores.get("Link Play", 0) >= 80:
            return "LINK-UP FORWARD"

        if scores.get("Offensive Duels", 0) >= 85:
            return "PHYSICAL FORWARD"


    # CENTRE BACKS
    if position_group == "CB":

        if scores.get("Distribution", 0) >= 80:
            return "BALL-PLAYING DEFENDER"

        if scores.get("Defending", 0) >= 80:
            return "DEFENSIVE ANCHOR"

        if scores.get("Aerial Defending", 0) >= 80:
            return "AERIAL DEFENDER"


    # FULL BACKS / WING BACKS
    if position_group == "FB_WB":

        if scores.get("Ball Carrying", 0) >= 80:
            return "PROGRESSIVE WING BACK"

        if scores.get("Chance Creation", 0) >= 80:
            return "CREATIVE FULL BACK"

        if scores.get("Defensive Contribution", 0) >= 80:
            return "BALANCED FULL BACK"


    # MIDFIELDERS
    if position_group == "DM":

        if scores.get("Ball Winning", 0) >= 80:
            return "BALL-WINNING MIDFIELDER"

        if scores.get("Distribution", 0) >= 80:
            return "DEEP-LYING PLAYMAKER"


    if position_group == "CM":

        if scores.get("Progression", 0) >= 80:
            return "PROGRESSIVE MIDFIELDER"

        if scores.get("Distribution", 0) >= 80:
            return "CONTROLLING MIDFIELDER"


    if position_group == "AM":

        if scores.get("Creativity", 0) >= 80:
            return "CREATIVE PLAYMAKER"

        if scores.get("Chance Creation", 0) >= 80:
            return "CHANCE CREATOR"


    # WINGERS
    if position_group == "WINGER":

        if scores.get("Ball Carrying", 0) >= 80:
            return "1V1 WINGER"

        if scores.get("Chance Creation", 0) >= 80:
            return "CREATIVE WINGER"


    return "COMPLETE PROFILE"
