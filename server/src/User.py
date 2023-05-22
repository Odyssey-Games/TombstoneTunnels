from time import time

from common.src.vec.Vec2i import Vec2i


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
        self.position = Vec2i()  # tile position of client - todo move player/entity classes to common?
        self.direction = Vec2i()  # direction of client input
