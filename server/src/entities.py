"""
Server-side entity classes. For rendering etc. see client/src/entities.py.
"""
from time import time

from pygame import Vector2

from common.src.direction import Dir2
from common.src.entities import EntityType


class ServerEntity:
    """Represents an entity in the game world. Can be a player or hostile creature."""

    def __init__(self, uuid: str, entity_type: EntityType, position: Vector2 = Vector2(), health: int = 50):
        self.uuid = uuid  # unique identifier of entity
        self.entity_type = entity_type  # type of entity -> used for sprites, animations etc.
        self.position = position  # tile position of entity
        self.health = health  # health points of entity
        self.direction = Dir2.ZERO  # direction of entity input (facing direction)
        self.last_direction = Dir2.ZERO  # last direction of entity input, only ZERO at start
        self.attacking: bool = False  # whether the entity is attacking
        self.last_move_time: float = 0  # last move time of the entity for handling tile movement speed


class ServerPlayer(ServerEntity):
    """Represents a user/client connected to the *server*."""

    def __init__(self, name: str, addr, uuid, token, position: Vector2 = Vector2(), health: int = 50):
        """
        :param name: the name of the player
        :param addr: the address (ip, port) of the player
        :param uuid: the public unique identifier of the player
        :param token: the private token the player uses to identify themselves
        """
        super().__init__(uuid, EntityType.KNIGHT, position, health)
        self.name = name
        self.addr = addr
        self.token = token
        self.last_ping = time()
