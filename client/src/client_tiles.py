import os
from typing import Dict

import pygame.image
from pygame import Surface, Vector2

from assets import Assets
from pos import abs_from_tile_pos


class ClientTileManager:
    """
    Class for loading the tiles (tile images) on the client side.
    """
    def __init__(self):
        self.images: Dict[str, Surface] = self._load_tiles()

    @staticmethod
    def _load_tiles() -> Dict[str, Surface]:
        """
        Load the tiles from the assets folder.
        :return: A dictionary (map) with the tile names as keys and the tile images as values.
        """
        images = {}
        for filename in os.listdir(Assets.get("tilemap", "tiles")):
            if filename.endswith(".png"):
                images[filename.removesuffix(".png")] = pygame.image \
                    .load(Assets.get("tilemap", "tiles", filename)) \
                    .convert_alpha()
        print(f"Loaded {len(images)} tiles")
        return images

    def get_image(self, tile: str) -> Surface:
        """
        Get the image for the specified tile.
        :param tile: the tile name
        :return: the tile image as a pygame Surfaces
        """
        return self.images[tile]


class ClientTileMap:
    """Client side tile map class for rendering the current map. Gets the tiles with the ClientTileManager."""

    def __init__(self, client, tile_size: int, pos: Vector2 = Vector2(0, 0)):
        self.client = client
        self.tile_size = tile_size
        self.position = pos
        self.tiles = ClientTileManager()

    def render(self, camera):  # unoptimised rendering, assuming tilemap is relatively small
        if not self.client.map:
            return
        for y, row in enumerate(self.client.map.tiles):
            for x, tile in enumerate(row):
                if tile == "":  # ignore empty tiles
                    continue
                # get the absolute position of the tile (tile pos * tile size)
                abs_pos = abs_from_tile_pos(Vector2(x, y))
                # render all tiles to the render texture, calculating in the current camera offset
                camera.renderTexture.blit(
                    self.tiles.get_image(tile),
                    (
                        self.position.x + abs_pos.x - camera.position.x,
                        self.position.y + abs_pos.y - camera.position.y
                    )
                )
