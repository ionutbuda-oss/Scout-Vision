"""
ScoutVision
Attacking Midfielder DNA Profiles
"""

AM_PROFILES = [

    {
        "key":"PROGRESSIVE_PLAYMAKER",
        "title":"PROGRESSIVE PLAYMAKER",
        "description":"Progresses possession through vertical passing.",
        "weights":{
            "Progression":0.60,
            "Creativity":0.40
        }
    },

    {
        "key":"BALL_PROGRESSOR",
        "title":"BALL PROGRESSOR",
        "description":"Advances play through progressive carries.",
        "weights":{
            "Ball Carrying":0.60,
            "Progression":0.40
        }
    },

    {
        "key":"CHANCE_CREATOR",
        "title":"CHANCE CREATOR",
        "description":"Creates chances through vision and passing.",
        "weights":{
            "Creativity":0.70,
            "Goal Threat":0.30
        }
    },

    {
        "key":"ATTACKING_CONNECTOR",
        "title":"ATTACKING CONNECTOR",
        "description":"Links midfield with the attacking line.",
        "weights":{
            "Creativity":0.35,
            "Progression":0.35,
            "Ball Carrying":0.30
        }
    }

]
