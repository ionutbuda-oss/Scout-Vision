"""
ScoutVision
Centre Back DNA Profiles
"""

CB_PROFILES = [

    {
        "key":"DEFENSIVE_STOPPER",
        "title":"DEFENSIVE STOPPER",
        "archetype":"Defender",
        "description":"Wins duels and protects the defensive line.",
        "executive_summary":"Centre-back whose primary value comes from defensive reliability, consistently winning duels and protecting the back line under pressure.",
        "weights":{
            "Defending":0.75,
            "Distribution":0.25
        }
    },

    {
        "key":"BALL_PLAYING_DEFENDER",
        "title":"BALL-PLAYING DEFENDER",
        "archetype":"Playmaker",
        "description":"Builds play through composed distribution.",
        "executive_summary":"Centre-back capable of initiating build-up through composed passing, distribution accuracy and control in possession.",
        "weights":{
            "Distribution":0.70,
            "Progression":0.30
        }
    },

    {
        "key":"PROGRESSIVE_DEFENDER",
        "title":"PROGRESSIVE DEFENDER",
        "archetype":"Progressor",
        "description":"Breaks opposition lines through progressive passing.",
        "executive_summary":"Defender who consistently advances possession by breaking opposition lines with progressive passing.",
        "weights":{
            "Progression":0.70,
            "Distribution":0.30
        }
    },

    {
        "key":"COMPLETE_CENTRE_BACK",
        "title":"COMPLETE CENTRE-BACK",
        "archetype":"Complete",
        "description":"Balanced defender across all phases of play.",
        "executive_summary":"Well-rounded centre-back combining defensive stability, secure distribution and effective progression throughout all phases of possession.",
        "weights":{
            "Defending":0.40,
            "Distribution":0.30,
            "Progression":0.30
        }
    },

    {
        "key":"BUILD_UP_DEFENDER",
        "title":"BUILD-UP DEFENDER",
        "archetype":"Distributor",
        "description":"Controls the first phase of possession.",
        "executive_summary":"Defender responsible for organizing build-up through consistent passing quality and secure possession from deep areas.",
        "weights":{
            "Distribution":0.50,
            "Defending":0.30,
            "Progression":0.20
        }
    }

]
