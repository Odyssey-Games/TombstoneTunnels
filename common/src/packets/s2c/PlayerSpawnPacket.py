from common.src.packets.Packet import Packet
from common.src.vec.TilePos import TilePos


class PlayerSpawnPacket(Packet):
    """Sent by the server to clients to indicate that a player spawned at the specified tile position."""

    def __init__(self, uuid, position: TilePos):
        self.uuid = uuid  # unique identifier of the player that spawned
        self.position = position  # position of the player in tile coordinates
