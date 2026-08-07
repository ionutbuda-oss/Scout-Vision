"""ScoutVision Tactical Fit V1 — tactical role library.

Alpha role weights are experimental and require external validation.
"""

ROLE_LIBRARY = {
    "4-3-3": {

        "CB": {

            "BALL_PLAYING_CB": {
                "title": "BALL-PLAYING CB",
                "weights": {
                    "Distribution": 0.40,
                    "Progression": 0.35,
                    "Defending": 0.25,
                },
            },

            "PROGRESSIVE_CB": {
                "title": "PROGRESSIVE CB",
                "weights": {
                    "Progression": 0.50,
                    "Distribution": 0.25,
                    "Defending": 0.25,
                },
            },

            "DEFENSIVE_CB": {
                "title": "DEFENSIVE CB",
                "weights": {
                    "Defending": 0.60,
                    "Distribution": 0.25,
                    "Progression": 0.15,
                },
            },

        },


        "FB_WB": {

            "DEFENSIVE_FULL_BACK": {
                "title": "DEFENSIVE FULL-BACK",
                "weights": {
                    "Defending": 0.50,
                    "Progression": 0.20,
                    "Ball Carrying": 0.15,
                    "Chance Creation": 0.15,
                },
            },

            "PROGRESSIVE_FULL_BACK": {
                "title": "PROGRESSIVE FULL-BACK",
                "weights": {
                    "Progression": 0.40,
                    "Ball Carrying": 0.30,
                    "Defending": 0.20,
                    "Chance Creation": 0.10,
                },
            },

            "ATTACKING_FULL_BACK": {
                "title": "ATTACKING FULL-BACK",
                "weights": {
                    "Chance Creation": 0.35,
                    "Ball Carrying": 0.25,
                    "Progression": 0.25,
                    "Defending": 0.15,
                },
            },

        },


        "DM": {

            "HOLDING_MIDFIELDER": {
                "title": "HOLDING MIDFIELDER",
                "weights": {
                    "Ball Winning": 0.45,
                    "Distribution": 0.40,
                    "Progression": 0.15,
                },
            },

            "BALL_WINNING_6": {
                "title": "BALL-WINNING #6",
                "weights": {
                    "Ball Winning": 0.65,
                    "Distribution": 0.20,
                    "Progression": 0.15,
                },
            },

            "DEEP_LYING_PLAYMAKER": {
                "title": "DEEP-LYING PLAYMAKER",
                "weights": {
                    "Distribution": 0.40,
                    "Progression": 0.40,
                    "Ball Winning": 0.20,
                },
            },

        },


        "CM": {

            "BOX_TO_BOX_8": {
                "title": "BOX-TO-BOX #8",
                "weights": {
                    "Defensive Contribution": 0.35,
                    "Progression": 0.25,
                    "Distribution": 0.20,
                    "Creativity": 0.20,
                },
            },

            "PROGRESSIVE_8": {
                "title": "PROGRESSIVE #8",
                "weights": {
                    "Progression": 0.45,
                    "Distribution": 0.25,
                    "Creativity": 0.20,
                    "Defensive Contribution": 0.10,
                },
            },

            "CREATIVE_8": {
                "title": "CREATIVE #8",
                "weights": {
                    "Creativity": 0.45,
                    "Progression": 0.25,
                    "Distribution": 0.20,
                    "Defensive Contribution": 0.10,
                },
            },

        },


        "Winger": {

            "DIRECT_WINGER": {
                "title": "DIRECT WINGER",
                "weights": {
                    "Ball Carrying": 0.45,
                    "Chance Creation": 0.20,
                    "Goal Threat": 0.20,
                    "Combination Play": 0.15,
                },
            },

            "CREATIVE_WINGER": {
                "title": "CREATIVE WINGER",
                "weights": {
                    "Chance Creation": 0.40,
                    "Ball Carrying": 0.25,
                    "Combination Play": 0.20,
                    "Goal Threat": 0.15,
                },
            },

            "INSIDE_FORWARD": {
                "title": "INSIDE FORWARD",
                "weights": {
                    "Goal Threat": 0.40,
                    "Ball Carrying": 0.30,
                    "Chance Creation": 0.15,
                    "Combination Play": 0.15,
                },
            },

        },


        "ST": {

            "CLINICAL_FINISHER": {
                "title": "CLINICAL FINISHER",
                "weights": {
                    "Finishing": 0.50,
                    "Box Threat": 0.30,
                    "Link Play": 0.10,
                    "Offensive Duels": 0.10,
                },
            },

            "BOX_STRIKER": {
                "title": "BOX STRIKER",
                "weights": {
                    "Box Threat": 0.50,
                    "Finishing": 0.30,
                    "Link Play": 0.10,
                    "Offensive Duels": 0.10,
                },
            },

            "LINK_UP_FORWARD": {
                "title": "LINK-UP FORWARD",
                "weights": {
                    "Link Play": 0.50,
                    "Offensive Duels": 0.20,
                    "Finishing": 0.15,
                    "Box Threat": 0.15,
                },
            },

            "TARGET_FORWARD": {
                "title": "TARGET FORWARD",
                "weights": {
                    "Offensive Duels": 0.45,
                    "Link Play": 0.20,
                    "Box Threat": 0.20,
                    "Finishing": 0.15,
                },
            },

        },

    },
    "4-2-3-1": {

        "CB": {

            "BALL_PLAYING_CB": {
                "title": "BALL-PLAYING CB",
                "weights": {
                    "Distribution": 0.40,
                    "Progression": 0.35,
                    "Defending": 0.25,
                },
            },

            "PROGRESSIVE_CB": {
                "title": "PROGRESSIVE CB",
                "weights": {
                    "Progression": 0.50,
                    "Distribution": 0.25,
                    "Defending": 0.25,
                },
            },

            "DEFENSIVE_CB": {
                "title": "DEFENSIVE CB",
                "weights": {
                    "Defending": 0.60,
                    "Distribution": 0.25,
                    "Progression": 0.15,
                },
            },

        },

        "FB_WB": {

            "DEFENSIVE_FULL_BACK": {
                "title": "DEFENSIVE FULL-BACK",
                "weights": {
                    "Defending": 0.45,
                    "Progression": 0.25,
                    "Ball Carrying": 0.15,
                    "Chance Creation": 0.15,
                },
            },

            "PROGRESSIVE_FULL_BACK": {
                "title": "PROGRESSIVE FULL-BACK",
                "weights": {
                    "Progression": 0.35,
                    "Ball Carrying": 0.30,
                    "Defending": 0.20,
                    "Chance Creation": 0.15,
                },
            },

            "ATTACKING_FULL_BACK": {
                "title": "ATTACKING FULL-BACK",
                "weights": {
                    "Chance Creation": 0.35,
                    "Ball Carrying": 0.25,
                    "Progression": 0.25,
                    "Defending": 0.15,
                },
            },

        },

        "DM": {

            "HOLDING_PIVOT": {
                "title": "HOLDING PIVOT",
                "weights": {
                    "Ball Winning": 0.40,
                    "Distribution": 0.45,
                    "Progression": 0.15,
                },
            },

            "BALL_WINNING_PIVOT": {
                "title": "BALL-WINNING PIVOT",
                "weights": {
                    "Ball Winning": 0.65,
                    "Distribution": 0.20,
                    "Progression": 0.15,
                },
            },

            "DEEP_LYING_PLAYMAKER": {
                "title": "DEEP-LYING PLAYMAKER",
                "weights": {
                    "Distribution": 0.45,
                    "Progression": 0.35,
                    "Ball Winning": 0.20,
                },
            },

        },

        "CM": {

            "BOX_TO_BOX_PIVOT": {
                "title": "BOX-TO-BOX PIVOT",
                "weights": {
                    "Defensive Contribution": 0.35,
                    "Progression": 0.25,
                    "Distribution": 0.20,
                    "Creativity": 0.20,
                },
            },

            "PROGRESSIVE_PIVOT": {
                "title": "PROGRESSIVE PIVOT",
                "weights": {
                    "Progression": 0.40,
                    "Distribution": 0.25,
                    "Creativity": 0.20,
                    "Defensive Contribution": 0.15,
                },
            },

            "CONTROLLING_PIVOT": {
                "title": "CONTROLLING PIVOT",
                "weights": {
                    "Distribution": 0.45,
                    "Progression": 0.30,
                    "Creativity": 0.15,
                    "Defensive Contribution": 0.10,
                },
            },

        },

        "AM": {

            "CREATIVE_10": {
                "title": "CREATIVE #10",
                "weights": {
                    "Creativity": 0.45,
                    "Progression": 0.25,
                    "Ball Carrying": 0.20,
                    "Goal Threat": 0.10,
                },
            },

            "DYNAMIC_10": {
                "title": "DYNAMIC #10",
                "weights": {
                    "Ball Carrying": 0.35,
                    "Progression": 0.30,
                    "Creativity": 0.20,
                    "Goal Threat": 0.15,
                },
            },

            "GOAL_THREAT_10": {
                "title": "GOAL-THREAT #10",
                "weights": {
                    "Goal Threat": 0.40,
                    "Creativity": 0.20,
                    "Ball Carrying": 0.20,
                    "Progression": 0.20,
                },
            },

        },

        "Winger": {

            "DIRECT_WINGER": {
                "title": "DIRECT WINGER",
                "weights": {
                    "Ball Carrying": 0.45,
                    "Chance Creation": 0.25,
                    "Combination Play": 0.15,
                    "Goal Threat": 0.15,
                },
            },

            "CREATIVE_WINGER": {
                "title": "CREATIVE WINGER",
                "weights": {
                    "Chance Creation": 0.40,
                    "Combination Play": 0.30,
                    "Ball Carrying": 0.20,
                    "Goal Threat": 0.10,
                },
            },

            "INSIDE_FORWARD": {
                "title": "INSIDE FORWARD",
                "weights": {
                    "Goal Threat": 0.40,
                    "Ball Carrying": 0.30,
                    "Chance Creation": 0.15,
                    "Combination Play": 0.15,
                },
            },

        },

        "ST": {

            "CLINICAL_FINISHER": {
                "title": "CLINICAL FINISHER",
                "weights": {
                    "Finishing": 0.50,
                    "Box Threat": 0.30,
                    "Link Play": 0.10,
                    "Offensive Duels": 0.10,
                },
            },

            "BOX_STRIKER": {
                "title": "BOX STRIKER",
                "weights": {
                    "Box Threat": 0.50,
                    "Finishing": 0.30,
                    "Link Play": 0.10,
                    "Offensive Duels": 0.10,
                },
            },

            "LINK_UP_FORWARD": {
                "title": "LINK-UP FORWARD",
                "weights": {
                    "Link Play": 0.50,
                    "Offensive Duels": 0.20,
                    "Finishing": 0.15,
                    "Box Threat": 0.15,
                },
            },

            "TARGET_FORWARD": {
                "title": "TARGET FORWARD",
                "weights": {
                    "Offensive Duels": 0.45,
                    "Link Play": 0.20,
                    "Box Threat": 0.20,
                    "Finishing": 0.15,
                },
            },

        },

    },


}
