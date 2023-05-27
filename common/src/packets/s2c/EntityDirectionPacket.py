from common.src.packets.Packet import Packet
from common.src.vec.Dir2 import Dir2


class EntityDirectionPacket(Packet):
    """
    Sent by the server to clients to indicate that an entity changed their looking direction.
    This is needed for updating the player sprites on the other clients.
    """

    def __init__(self, uuid: str, direction: Dir2):
        self.uuid = uuid  # unique identifier of the player that moved
        self.direction = direction  # new direction of the player
