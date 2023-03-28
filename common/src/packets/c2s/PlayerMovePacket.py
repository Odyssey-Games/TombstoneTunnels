import pygame

from common.src.packets.c2s.AuthorizedPacket import AuthorizedPacket


class PlayerMovePacket(AuthorizedPacket):
    """Sent by the client to the server to indicate that the player moved to the new specified position."""

    def __init__(self, position: pygame.Vector2):
        self.position = position
