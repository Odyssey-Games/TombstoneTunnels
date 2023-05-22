from common.src.vec.Vec2i import Vec2i


class ClientInput:
    """
    Class representing a client's input.

    Currently, this contains the direction in which the player is trying to move.
    """

    def __init__(self, direction: Vec2i):
        """
        :param direction: the direction in which the player is trying to move
        """
        self.direction = direction
