"""
ScoutVision
Full-Back / Wing-Back DNA Profiles
"""

FB_PROFILES = [

    {
        "key":"DEFENSIVE_FULL_BACK",
        "signature":"Defending",
        "title":"DEFENSIVE FULL-BACK",
        "archetype":"Defender",
        "description":"Provides defensive stability on the flank.",
        "executive_summary":"Full-back who provides defensive security through reliable duel success, intelligent positioning and consistent protection of the defensive flank.",
        "weights":{
            "Defending":0.75,
            "Progression":0.25
        }
    },

    {
        "key":"CREATIVE_FULL_BACK",
        "signature":"Chance Creation",
        "title":"CREATIVE FULL-BACK",
        "archetype":"Creator",
        "description":"Creates chances through crossing quality and intelligent final-third delivery.",
        "executive_summary":"Creative full-back capable of consistently generating chances through crossing quality, intelligent final-third passing and attacking support from wide areas.",
        "weights":{
            "Chance Creation":0.65,
            "Progression":0.20,
            "Ball Carrying":0.15
        }
    },

    {
        "key":"PROGRESSIVE_FULL_BACK",
        "signature":"Progression",
        "title":"PROGRESSIVE FULL-BACK",
        "archetype":"Progressor",
        "description":"Advances possession through progressive distribution.",
        "executive_summary":"Full-back who consistently advances possession through progressive passing and forward-oriented build-up involvement.",
        "weights":{
            "Progression":0.75,
            "Defending":0.25
        }
    },

    {
        "key":"WING_BACK",
        "signature":"Ball Carrying",
        "title":"WING-BACK",
        "archetype":"Runner",
        "description":"Drives attacks through width and dynamic movement.",
        "executive_summary":"Dynamic wide player capable of carrying possession forward while supporting attacks through width, progression and chance creation.",
        "weights":{
            "Ball Carrying":0.50,
            "Chance Creation":0.30,
            "Progression":0.20
        }
    },

    {
        "key":"COMPLETE_FULL_BACK",
        "signature":"Complete",
        "title":"COMPLETE FULL-BACK",
        "archetype":"Complete",
        "description":"Balanced full-back across all phases of play.",
        "executive_summary":"Well-rounded full-back combining defensive reliability, progressive distribution, ball carrying and attacking contribution across all phases of play.",
        "weights":{
            "Defending":0.30,
            "Progression":0.30,
            "Ball Carrying":0.20,
            "Chance Creation":0.20
        }
    }

]
