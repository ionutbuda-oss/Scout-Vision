"""
ScoutVision
Central Midfielder DNA Profiles
"""

CM_PROFILES = [

    {
        "key":"BOX_TO_BOX_MIDFIELDER",
        "title":"BOX-TO-BOX MIDFIELDER",
        "archetype":"Runner",
        "description":"Contributes in both attacking and defensive phases.",
        "executive_summary":"Energetic central midfielder contributing across both phases of play through continuous movement, progression and defensive work rate.",
        "weights":{
            "Progression":0.40,
            "Distribution":0.25,
            "Defensive Contribution":0.20,
            "Creativity":0.15
        }
    },

    {
        "key":"DEEP_LYING_PLAYMAKER",
        "title":"DEEP-LYING PLAYMAKER",
        "archetype":"Playmaker",
        "description":"Controls possession from deeper midfield areas.",
        "executive_summary":"Central midfielder who controls possession through intelligent ball circulation, progressive distribution and consistent tempo management.",
        "weights":{
            "Distribution":0.70,
            "Progression":0.30
        }
    },

    {
        "key":"PROGRESSIVE_MIDFIELDER",
        "title":"PROGRESSIVE MIDFIELDER",
        "archetype":"Progressor",
        "description":"Advances possession through progressive passing.",
        "executive_summary":"Central midfielder capable of accelerating attacking phases through progressive passing and vertical ball progression.",
        "weights":{
            "Progression":0.70,
            "Distribution":0.30
        }
    },

    {
        "key":"CREATIVE_MIDFIELDER",
        "title":"CREATIVE MIDFIELDER",
        "archetype":"Creator",
        "description":"Creates opportunities through vision and passing.",
        "executive_summary":"Creative midfielder who generates attacking opportunities through vision, intelligent passing and final-third decision making.",
        "weights":{
            "Creativity":0.60,
            "Progression":0.40
        }
    },

    {
        "key":"COMPLETE_MIDFIELDER",
        "title":"COMPLETE MIDFIELDER",
        "archetype":"Complete",
        "description":"Balanced midfielder across all phases of play.",
        "executive_summary":"Well-rounded central midfielder combining distribution, progression, creativity and defensive contribution across all phases of play.",
        "weights":{
            "Distribution":0.30,
            "Progression":0.30,
            "Creativity":0.20,
            "Defensive Contribution":0.20
        }
    }

]
