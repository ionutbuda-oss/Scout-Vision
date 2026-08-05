ST_PROFILES = [

    {
        "key":"CLINICAL_FINISHER",
        "title":"CLINICAL FINISHER",
        "signature":"Finishing",
        "archetype":"Goalscorer",
        "description":"Converts chances with efficiency inside the penalty area.",
        "executive_summary":"Striker whose primary value comes from efficient finishing and consistent goalscoring ability inside the penalty area.",
        "weights":{
            "Finishing":0.70,
            "Box Threat":0.30
        }
    },

    {
        "key":"BOX_STRIKER",
        "title":"BOX STRIKER",
        "signature":"Box Threat",
        "archetype":"Poacher",
        "description":"Attacks dangerous spaces and constantly threatens inside the box.",
        "executive_summary":"Penalty-box specialist who consistently attacks dangerous spaces and creates scoring opportunities through intelligent movement.",
        "weights":{
            "Box Threat":0.70,
            "Finishing":0.30
        }
    },

    {
        "key":"LINK_UP_FORWARD",
        "title":"LINK-UP FORWARD",
        "signature":"Link Play",
        "archetype":"Playmaker",
        "description":"Connects attacking play through intelligent combinations.",
        "executive_summary":"Forward capable of linking attacking play through intelligent combinations, passing quality and involvement in possession.",
        "weights":{
            "Link Play":0.70,
            "Offensive Duels":0.30
        }
    },

    {
        "key":"TARGET_FORWARD",
        "title":"TARGET FORWARD",
        "signature":"Offensive Duels",
        "archetype":"Target",
        "description":"Dominates offensive duels and provides a focal point in attack.",
        "executive_summary":"Physically dominant striker who excels in offensive duels, holds up possession and provides a focal point for the attack.",
        "weights":{
            "Offensive Duels":0.70,
            "Link Play":0.30
        }
    },

    {
        "key":"COMPLETE_FORWARD",
        "title":"COMPLETE FORWARD",
        "signature":"Complete",
        "archetype":"Complete",
        "description":"Balanced striker across all attacking phases.",
        "executive_summary":"Well-rounded striker combining finishing, penalty-box presence, link-up play and offensive duel ability across all attacking phases.",
        "weights":{
            "Finishing":0.35,
            "Box Threat":0.25,
            "Link Play":0.20,
            "Offensive Duels":0.20
        }
    }

]
