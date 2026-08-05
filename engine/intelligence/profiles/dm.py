"""
ScoutVision
Defensive Midfielder DNA Profiles
"""

DM_PROFILES = [

    {
        "key":"BALL_WINNER",
        "title":"BALL WINNER",
        "archetype":"Destroyer",
        "description":"Recovers possession through defensive actions.",
        "executive_summary":"Holding midfielder who protects the defensive structure through ball recoveries, duel dominance and intelligent defensive positioning.",
        "weights":{
            "Ball Winning":0.75,
            "Distribution":0.25
        }
    },

    {
        "key":"DEEP_LYING_PLAYMAKER",
        "title":"DEEP-LYING PLAYMAKER",
        "archetype":"Playmaker",
        "description":"Controls possession from deep areas.",
        "executive_summary":"Holding midfielder who dictates build-up from deep while providing balance in front of the defensive line through composed distribution and intelligent positioning.",
        "weights":{
            "Distribution":0.70,
            "Progression":0.30
        }
    },

    {
        "key":"PROGRESSIVE_PIVOT",
        "title":"PROGRESSIVE PIVOT",
        "archetype":"Progressor",
        "description":"Advances possession through progressive passing.",
        "executive_summary":"Holding midfielder capable of advancing possession through progressive distribution and vertical passing between opposition lines.",
        "weights":{
            "Progression":0.70,
            "Distribution":0.30
        }
    },

    {
        "key":"COMPLETE_HOLDING_MIDFIELDER",
        "title":"COMPLETE HOLDING MIDFIELDER",
        "archetype":"Complete",
        "description":"Balanced holding midfielder across all phases.",
        "executive_summary":"Balanced defensive midfielder combining defensive stability, secure distribution and progressive possession management.",
        "weights":{
            "Ball Winning":0.40,
            "Distribution":0.35,
            "Progression":0.25
        }
    },

    {
        "key":"POSSESSION_ANCHOR",
        "title":"POSSESSION ANCHOR",
        "archetype":"Anchor",
        "description":"Maintains possession and stabilizes build-up.",
        "executive_summary":"Holding midfielder responsible for maintaining possession, controlling tempo and providing stability during the build-up phase.",
        "weights":{
            "Distribution":0.50,
            "Ball Winning":0.30,
            "Progression":0.20
        }
    }

]
