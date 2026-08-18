"""
ScoutVision V3 - Archetype Ranking Engine

Ranks players by football archetype rather than only
overall recruitment score.
"""

from __future__ import annotations

from typing import Any


ARCHETYPE_WEIGHTS = {

    "BOX STRIKER": {
        "Box Threat": 0.40,
        "Offensive Duels": 0.25,
        "Finishing": 0.25,
        "Goal Threat": 0.10,
    },

    "CLINICAL FINISHER": {
        "Finishing": 0.50,
        "Goal Threat": 0.30,
        "Box Threat": 0.20,
    },

    "BALL-PLAYING DEFENDER": {
        "Distribution": 0.40,
        "Progression": 0.30,
        "Defending": 0.30,
    },

    "COMPLETE CENTRE BACK": {
        "Defending": 0.30,
        "Distribution": 0.25,
        "Progression": 0.20,
        "Defensive Contribution": 0.15,
        "Ball Winning": 0.10,
    },

    "STOPPER CENTRE BACK": {
        "Defending": 0.40,
        "Ball Winning": 0.25,
        "Defensive Contribution": 0.20,
        "Duels per 90": 0.15,
    },

    "COVER DEFENDER": {
        "Defending": 0.30,
        "Interceptions": 0.25,
        "Defensive Contribution": 0.20,
        "Progression": 0.15,
        "Ball Carrying": 0.10,
    },

    "DEFENSIVE ANCHOR": {
        "Defending": 0.50,
        "Defensive Contribution": 0.20,
        "Ball Winning": 0.20,
    },

    "PROGRESSIVE MIDFIELDER": {
        "Progression": 0.40,
        "Ball Carrying": 0.30,
        "Distribution": 0.30,
    },

    "CREATIVE PLAYMAKER": {
        "Creativity": 0.40,
        "Chance Creation": 0.30,
        "Combination Play": 0.25,
    },

    "1V1 WINGER": {
        "Ball Carrying": 0.50,
        "Offensive Duels": 0.30,
        "Chance Creation": 0.20,
    },

    "LINK-UP FORWARD": {
        "Link Play": 0.40,
        "Combination Play": 0.30,
        "Distribution": 0.30,
    },

    "PHYSICAL FORWARD": {
        "Offensive Duels": 0.50,
        "Duels per 90": 0.25,
        "Successful attacking actions": 0.25,
    },

    "DEEP-LYING PLAYMAKER": {
        "Distribution": 0.40,
        "Progression": 0.30,
        "Accurate passes": 0.30,
    },

    "CREATIVE WINGER": {
        "Chance Creation": 0.40,
        "Combination Play": 0.30,
        "Distribution": 0.30,
    },

    "PROGRESSIVE WIDE DEFENDER": {
        "Ball Carrying": 0.40,
        "Progression": 0.30,
        "Chance Creation": 0.30,
    },

    "DEFENSIVE FULL BACK": {
        "Defensive Contribution": 0.50,
        "Defending": 0.30,
        "Ball Winning": 0.20,
    },


    "CREATIVE FULL BACK": {
        "Chance Creation": 0.40,
        "Combination Play": 0.30,
        "Distribution": 0.30,
    },

    "GOAL THREAT WINGER": {
        "Goal Threat": 0.40,
        "Box Threat": 0.30,
        "Finishing": 0.30,
    },

}


def calculate_archetype_score(
    metrics: dict[str, float],
    archetype: str,
) -> float:

    weights = ARCHETYPE_WEIGHTS.get(archetype)

    if not weights:
        return 0.0

    score = 0.0
    available_weight = 0.0

    for metric, weight in weights.items():

        if metric in metrics:
            score += metrics[metric] * weight
            available_weight += weight

    if available_weight == 0:
        return 0.0

    return round(score / available_weight, 1)


def rank_players_by_archetype(
    players: list[dict[str, Any]],
    archetype: str,
) -> list[dict[str, Any]]:

    ranked = []

    for player in players:

        score = calculate_archetype_score(
            player.get("metrics", {}),
            archetype,
        )

        ranked.append(
            {
                "player": player.get("player"),
                "team": player.get("team"),
                "position": player.get("position"),
                "archetype": archetype,
                "archetype_score": score,
            }
        )

    return sorted(
        ranked,
        key=lambda x: x["archetype_score"],
        reverse=True,
    )


ARCHETYPE_POSITIONS = {

    "BOX STRIKER": [
        "ST"
    ],

    "CLINICAL FINISHER": [
        "ST"
    ],

    "LINK-UP FORWARD": [
        "ST"
    ],

    "PHYSICAL FORWARD": [
        "ST"
    ],


    "BALL-PLAYING DEFENDER": [
        "CB"
    ],

    "DEFENSIVE ANCHOR": [
        "DM"
    ],

    "COMPLETE CENTRE BACK": [
        "CB"
    ],

    "STOPPER CENTRE BACK": [
        "CB"
    ],

    "COVER DEFENDER": [
        "CB"
    ],


    "PROGRESSIVE MIDFIELDER": [
        "CM",
        "DM"
    ],

    "DEEP-LYING PLAYMAKER": [
        "DM",
        "CM"
    ],


    "CREATIVE PLAYMAKER": [
        "AM",
        "CM"
    ],


    "1V1 WINGER": [
        "Winger"
    ],

    "CREATIVE WINGER": [
        "Winger"
    ],

    "PROGRESSIVE WIDE DEFENDER": [
        "FB_WB"
    ],

    "DEFENSIVE FULL BACK": [
        "FB_WB"
    ],


    "CREATIVE FULL BACK": [
        "FB_WB"
    ],

    "GOAL THREAT WINGER": [
        "Winger"
    ],

}
