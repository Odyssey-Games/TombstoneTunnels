import os
from typing import Dict

import pygame.image
from pygame import Surface, Vector2

from assets import Assets
from pos import abs_from_tile_pos


class ClientTileManager:
    def __init__(self):
        self.images: Dict[str, Surface] = self._load_tiles()

    @staticmethod
    def _load_tiles() -> Dict[str, Surface]:
        images = {}
        for filename in os.listdir(Assets.get("tilemap", "tiles")):
            if filename.endswith(".png"):
                images[filename.removesuffix(".png")] = pygame.image \
                    .load(Assets.get("tilemap", "tiles", filename)) \
                    .convert_alpha()
        print(f"Loaded {len(images)} tiles")
        return images

    def get_image(self, tile: str) -> Surface:
        return self.images[tile]


class ClientTileMap:
    """Client side tile map class for rendering the current map."""

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
                abs_pos = abs_from_tile_pos(Vector2(x, y))
                camera.renderTexture.blit(
                    self.tiles.get_image(tile),
                    (
                        self.position.x + abs_pos.x - camera.position.x,
                        self.position.y + abs_pos.y - camera.position.y
                    )
                )
