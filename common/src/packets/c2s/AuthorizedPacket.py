from common.src.packets.Packet import Packet


class AuthorizedPacket(Packet):
    def __init__(self):
        self.token = None

    """Baseclass for all packets that are sent when the client is already authorized.

    Example: PlayerMovePacket, PlayerAttackEntityPacket, etc.

    In the send logic of the client, it should check if a packet is an instance of this class, and if so,
    add the client token to the packet (or complain if the client is not authorized).
    """
    pass
