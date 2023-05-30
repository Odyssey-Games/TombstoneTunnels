import os
from typing import Dict

import pygame.image
from pygame import Surface

from assets import Assets
from common.src.map.tile import Tile
from common.src.vec.TilePos import TilePos
from vec.AbsPos import AbsPos


class ClientTileManager:
    def __init__(self):
        self.images: Dict[str, Surface] = self.load_tiles()

    def load_tiles(self) -> Dict[str, Surface]:
        images = {}
        for filename in os.listdir(Assets.get("tilemap", "tiles")):
            if filename.endswith(".png"):
                images[filename.removesuffix(".png")] = pygame.image \
                    .load(Assets.get("tilemap", "tiles", filename)) \
                    .convert_alpha()
        print(f"Loaded {len(images)} tiles")
        return images

    def get_image(self, tile: Tile) -> Surface:
        return self.images[tile.name]


class ClientTileMap:
    """Client side tile map class for rendering the current map."""

    def __init__(self, renderer, tile_size: int, pos: pygame.Vector2 = pygame.Vector2(0, 0)):
        self.renderer = renderer
        self.tile_size = tile_size
        self.position = pos
        self.tiles = ClientTileManager()
        self.rendered_tiles = False

    def render(self, camera):
        if not self.renderer.client.map:
            return
        if self.rendered_tiles:
            return

        self.rendered_tiles = True
        for y, row in enumerate(self.renderer.client.map.tiles):
            for x, tile in enumerate(row):
                if tile.name == "":  # ignore empty tiles
                    continue
                abs_pos = AbsPos.from_tile_pos(TilePos(x, y))
                screen_pos = self.renderer.camera.world_to_screen(abs_pos)
                if screen_pos.x + 16 * 8 > 0 \
                        and screen_pos.y + 16 * 8 > 0 \
                        and screen_pos.x < self.renderer.screen_size.x \
                        and screen_pos.y < self.renderer.screen_size.y:
                    camera.tilemap_surface.blit(
                        self.tiles.get_image(tile),
                        (
                            self.position.x + abs_pos.x,
                            self.position.y + abs_pos.y
                        )
                    )
