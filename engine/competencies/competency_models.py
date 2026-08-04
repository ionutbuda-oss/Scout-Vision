"""
ScoutVision Competency Models v1.0
"""

COMPETENCY_MODELS = {

    "PROGRESSION": {
        "Progressive passes per 90": 0.25,
        "Accurate progressive passes, %": 0.20,
        "Forward passes per 90": 0.15,
        "Accurate forward passes, %": 0.10,
        "Passes to final third per 90": 0.15,
        "Accurate passes to final third, %": 0.10,
        "Through passes per 90": 0.03,
        "Accurate through passes, %": 0.02,
    },

    "DISTRIBUTION": {
        "Passes per 90": 0.35,
        "Accurate passes, %": 0.35,
        "Long passes per 90": 0.15,
        "Accurate long passes, %": 0.15,
    },

    "CREATIVITY": {
        "Smart passes per 90": 0.35,
        "Accurate smart passes, %": 0.25,
        "Assists per 90": 0.20,
        "xA per 90": 0.20,
    },

    "BALL_CARRYING": {
        "Dribbles per 90": 0.40,
        "Successful dribbles, %": 0.35,
        "Successful attacking actions per 90": 0.25,
    },

    "DEFENDING": {
        "Successful defensive actions per 90": 0.30,
        "Defensive duels per 90": 0.20,
        "Defensive duels won, %": 0.30,
        "Interceptions per 90": 0.20,
    },

    "OFFENSIVE_DUELS": {
        "Offensive duels per 90": 0.50,
        "Offensive duels won, %": 0.50,
    },

    "GOAL_THREAT": {
        "Goals per 90": 0.35,
        "xG per 90": 0.30,
        "Goal conversion, %": 0.20,
        "Touches in box per 90": 0.15,
    },

    "CHANCE_CREATION": {
        "Crosses per 90": 0.40,
        "Accurate crosses, %": 0.30,
        "xA per 90": 0.30,
    }

}
