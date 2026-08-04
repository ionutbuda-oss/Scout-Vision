from dataclasses import dataclass

"""
ScoutVision DNA Engine
Transforms competency scores into football identities.
"""



@dataclass
class DNAProfile:
    title: str
    description: str

DNA_LIBRARY = {

    "Progression": {
        "title": "PROGRESSIVE PLAYMAKER",
        "description":
        "Progresses possession through line-breaking passing."
    },

    "Creativity": {
        "title": "CHANCE CREATOR",
        "description":
        "Creates chances through vision and creative passing."
    },

    "Ball Carrying": {
        "title": "BALL CARRIER",
        "description":
        "Advances play through progressive ball carrying."
    },

    "Goal Threat": {
        "title": "GOAL-SCORING MIDFIELDER",
        "description":
        "Looks to attack the penalty area and finish chances."
    }

}


def build_player_dna(competencies):
    """
    competencies:
    {
        "Creativity":78,
        "Ball Carrying":81,
        "Progression":98,
        "Goal Threat":38
    }
    """

    strongest = max(
        competencies,
        key=competencies.get
    )

    dna = DNA_LIBRARY[strongest]

    return {
        "name": strongest,
        "title": dna["title"],
        "description": dna["description"],
        "score": competencies[strongest]
    }

