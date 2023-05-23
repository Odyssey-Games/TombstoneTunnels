import os
from typing import Dict

import pygame.image
from pygame import Surface

from common.src.map.tile import Tile


class ClientTileManager:
    def __init__(self, assets_path):
        self.assets_path = assets_path
        self.images: Dict[str, Surface] = self.load_tiles()

    def load_tiles(self) -> Dict[str, Surface]:
        images = {}
        for filename in os.listdir(os.path.join(self.assets_path, "tilemap", "tiles")):
            if filename.endswith(".png"):
                images[filename.removesuffix(".png")] = pygame.image \
                    .load(os.path.join(self.assets_path, "tilemap", "tiles", filename)) \
                    .convert_alpha()
        print(f"Loaded {len(images)} tiles")
        return images

    def get_image(self, tile: Tile) -> Surface:
        return self.images[tile.name]


class ClientTileMap:
    """Client side tile map class for rendering the current map."""

    def __init__(self, client, tile_size: int, assets_path: str, pos: pygame.Vector2 = pygame.Vector2(0, 0)):
        self.client = client
        self.tile_size = tile_size
        self.position = pos
        self.tiles = ClientTileManager(assets_path)

    def render(self, camera):  # unoptimised rendering, assuming tilemap is relatively small
        if not self.client.map:
            return
        for y, row in enumerate(self.client.map.tiles):
            for x, tile in enumerate(row):
                if tile.name == "":  # ignore empty tiles
                    continue

                camera.renderTexture.blit(
                    self.tiles.get_image(tile),
                    (
                        self.position.x + (x * self.tile_size) - camera.position.x,
                        self.position.y + (y * self.tile_size) - camera.position.y
                    )
                )
