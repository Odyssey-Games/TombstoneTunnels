from time import time

import pygame


class User:
    """Represents a user connected to the *server*."""

    def __init__(self, name: str, addr, token):
        self.name = name
        self.addr = addr
        self.token = token
        self.last_ping = time()
        self.position = pygame.Vector2(0, 0)  # todo move player/entity classes to common?
