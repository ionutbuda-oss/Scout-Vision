"""
ScoutVision Position Models v3.0
"""

POSITION_MODELS = {

    "CB": {

        "core": {
            "DEFENDING": 1.0,
        },

        "primary": {
            "DISTRIBUTION": 0.60,
            "PROGRESSION": 0.40,
        },

        "support": {
            "BALL_CARRYING": 1.0,
        },

    },

    "FB_WB": {

        "core": {
            "DEFENDING": 1.0,
        },

        "primary": {
            "BALL_CARRYING": 0.60,
            "PROGRESSION": 0.40,
        },

        "support": {
            "CHANCE_CREATION": 1.0,
        },

    },

    "DM": {

        "core": {
            "DEFENDING": 0.50,
            "DISTRIBUTION": 0.50,
        },

        "primary": {
            "PROGRESSION": 1.0,
        },

        "support": {
            "BALL_CARRYING": 1.0,
        },

    },

    "CM": {

        "core": {
            "PROGRESSION": 1.0,
        },

        "primary": {
            "DISTRIBUTION": 0.50,
            "CREATIVITY": 0.50,
        },

        "support": {
            "BALL_CARRYING": 1.0,
        },

    },

    "AM": {

        "core": {
            "CREATIVITY": 1.0,
        },

        "primary": {
            "PROGRESSION": 0.60,
            "GOAL_THREAT": 0.40,
        },

        "support": {
            "BALL_CARRYING": 1.0,
        },

    },

    "Winger": {

        "core": {
            "BALL_CARRYING": 1.0,
        },

        "primary": {
            "CHANCE_CREATION": 0.60,
            "GOAL_THREAT": 0.40,
        },

        "support": {
            "OFFENSIVE_DUELS": 1.0,
        },

    },

    "ST": {

        "core": {
            "GOAL_THREAT": 1.0,
        },

        "primary": {
            "OFFENSIVE_DUELS": 1.0,
        },

        "support": {
            "BALL_CARRYING": 0.50,
            "CHANCE_CREATION": 0.50,
        },

    },

}
