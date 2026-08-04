"""
ScoutVision Position Parser
"""

from collections import Counter

POSITION_MAP = {

    # Centre Back
    "CB": "CB",
    "LCB": "CB",
    "RCB": "CB",

    # Full Back / Wing Back
    "LB": "FB_WB",
    "RB": "FB_WB",
    "LWB": "FB_WB",
    "RWB": "FB_WB",

    # Defensive Midfielder
    "DMF": "DM",
    "CDM": "DM",
    "LDMF": "DM",
    "RDMF": "DM",

    # Central Midfielder
    "CM": "CM",
    "CMF": "CM",
    "LCMF": "CM",
    "RCMF": "CM",

    # Attacking Midfielder
    "AM": "AM",
    "AMF": "AM",
    "CAM": "AM",
    "LAM": "AM",
    "RAM": "AM",
    "LAMF": "AM",
    "RAMF": "AM",

    # Wingers
    "LW": "Winger",
    "RW": "Winger",
    "LWF": "Winger",
    "RWF": "Winger",

    # Striker
    "CF": "ST",
    "ST": "ST",

    # Goalkeeper
    "GK": "GK",
}


def map_position(position_string: str) -> str:
    """
    Converts Wyscout position strings into one ScoutVision Position Group.

    Examples
    --------
    "RCB, RB" -> "CB"

    "CF, LW, RWF" -> "Winger"

    "LCB, CB, RCB" -> "CB"
    """

    if not isinstance(position_string, str):
        return "Unknown"

    positions = [
        p.strip()
        for p in position_string.split(",")
    ]

    mapped = []

    for pos in positions:

        if pos in POSITION_MAP:
            mapped.append(POSITION_MAP[pos])

    if not mapped:
        return "Unknown"

    return Counter(mapped).most_common(1)[0][0]
