from time import time

import pygame


class User:
    """Represents a user connected to the *server*."""

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
        self.position = pygame.Vector2(0, 0)  # todo move player/entity classes to common?
