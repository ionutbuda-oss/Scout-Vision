from engine.config import Settings
from engine.pipeline import run_pipeline


def main():
    settings = Settings()
    run_pipeline(settings)


if __name__ == "__main__":
    main()
