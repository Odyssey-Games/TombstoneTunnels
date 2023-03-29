import pygame

from common.src.packets.Packet import Packet


class PlayerMovePacket(Packet):
    """Sent by the server to clients to indicate that a player moved to the new specified position."""

    def __init__(self, uuid: int, position: pygame.Vector2):
        self.uuid = uuid
        self.position = position
