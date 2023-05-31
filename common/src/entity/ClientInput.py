from common.src.direction import Dir2


class ClientInput:
    """
    Class representing a client's input.

    Currently, this contains the direction in which the player is trying to move.
    """

    def __init__(self, direction: Dir2):
        """
        :param direction: the direction in which the player is trying to move
        """
        self.direction = direction
