from time import time

from common.src.vec.Dir2 import Dir2
from common.src.vec.TilePos import TilePos


class User:
    """Represents a user/client connected to the *server*."""

    def __init__(self, name: str, addr, uuid, token):
        """
        :param name: the name of the player
        :param addr: the address (ip, port) of the player
        :param uuid: the public unique identifier of the player
        :param token: the private token the player uses to identify themselves
        """
        self.name = name
        self.addr = addr
        self.uuid = uuid
        self.token = token
        self.last_ping = time()
        self.position: TilePos = TilePos()  # tile position of client - todo move player/entity classes to common?
        self.last_move_time: float = 0  # last move time of client for handling tile movement speed
        self.direction: Dir2 = Dir2.ZERO  # direction of client input
