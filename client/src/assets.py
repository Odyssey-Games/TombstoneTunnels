import os

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
if not os.path.exists(ASSETS_PATH):  # for pyinstaller; different data folder loc
    ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")


class Assets:
    @staticmethod
    def get(*path: str) -> str:
        return os.path.join(ASSETS_PATH, *path)
