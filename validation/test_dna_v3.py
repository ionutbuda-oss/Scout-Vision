from engine.intelligence.v3.dna_engine_v3 import build_player_dna_v3

competencies = {
    "Defending": 80,
    "Progression": 71,
    "Chance Creation": 86,
    "Ball Carrying": 48,
}

result = build_player_dna_v3(
    "FB_WB",
    competencies,
)

print("=" * 60)
print("SCOUTVISION DNA V3")
print("=" * 60)

print(result)
