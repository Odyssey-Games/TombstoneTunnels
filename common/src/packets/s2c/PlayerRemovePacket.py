from common.src.packets.Packet import Packet


class PlayerRemovePacket(Packet):
    """Sent by the server to clients to indicate that a player was removed from the current world / left."""

    def __init__(self, uuid):
        self.uuid = uuid
