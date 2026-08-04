"""
ScoutVision Competency Validator
"""

from engine.competencies.competency_models import COMPETENCY_MODELS


def validate_models():

    print("=" * 60)
    print("SCOUTVISION COMPETENCY VALIDATOR")
    print("=" * 60)

    passed = True

    for name, model in COMPETENCY_MODELS.items():

        total = sum(model.values())

        if abs(total - 1.0) < 1e-6:
            print(f"✅ {name}: weights = {total:.2f}")
        else:
            print(f"❌ {name}: weights = {total:.2f}")
            passed = False

    print("=" * 60)

    if passed:
        print("ALL COMPETENCY MODELS PASSED")
    else:
        print("VALIDATION FAILED")


if __name__ == "__main__":
    validate_models()
