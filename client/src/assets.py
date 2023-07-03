"""
Utilities for accessing assets (images, sounds, etc.) in the assets folder.
For packaging the assets to the executable, see the pyinstaller spec file.
There, the assets folder is copied to the executable's root folder.
"""
import os

# when using pyinstaller the assets are copied to the root folder of the executable
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
if not os.path.exists(ASSETS_PATH):  # default path is the assets folder in client/assets, so we have to go one level up
    ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")


class Assets:
    @staticmethod
    def get(*path: str) -> str:
        """
        Get the path to an asset.
        :param path: The path to the asset, relative to the assets folder.
        :return: The absolute path to the asset.
        """
        return os.path.join(ASSETS_PATH, *path)
