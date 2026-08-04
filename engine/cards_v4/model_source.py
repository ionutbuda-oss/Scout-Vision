try:
    from engine.scoring.profile_models import ROLE_MODELS
except ModuleNotFoundError:
    from engine.score_players import ROLE_MODELS
__all__ = ["ROLE_MODELS"]
