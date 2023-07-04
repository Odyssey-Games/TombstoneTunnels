from abc import abstractmethod

from common.src.packets import Packet


class Mechanics:
    """
    Base class for all mechanics.

    This class is used to split up the server main loop code into multiple classes to
    improve the readability and maintainability of the code.
    """
    def __init__(self, server):
        self.server = server

    @abstractmethod
    def tick(self, packet: Packet | None, addr: tuple | None):
        """
        Called every tick by the server.

        :param packet: The packet sent by the client or None if no packet was sent.
        :param addr: The network address of the client (address, port) or None if packet is None.
        """
        pass
