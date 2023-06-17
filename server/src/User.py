from time import time

from pygame import Vector2

from common.src.direction import Dir2


class User:
    """Represents a user/client connected to the *server*."""

    def __init__(self, name: str, addr, uuid, token, socket_type, start_pos: Vector2 = Vector2()):
        """
        :param name: the name of the player
        :param addr: the address (ip, port) of the player
        :param uuid: the public unique identifier of the player
        :param token: the private token the player uses to identify themselves
        :param socket_type: 0 for UDP, 1 for TCP
        """
        self.name = name
        self.addr = addr
        self.uuid = uuid
        self.token = token
        self.socket_type = socket_type
        self.last_ping = time()
        self.position: Vector2 = start_pos  # tile position of client
        self.last_move_time: float = 0  # last move time of client for handling tile movement speed
        self.direction: Dir2 = Dir2.ZERO  # direction of client input
