from common.src.packets.Packet import Packet
from common.src.vec.TilePos import TilePos


class PlayerMovePacket(Packet):
    """Sent by the server to clients to indicate that a player moved to the new specified *tile* position."""

    def __init__(self, uuid: int, position: TilePos):
        self.uuid = uuid  # unique identifier of the player that moved
        self.position = position  # new position of the player in tile coordinates
