from common.src.packets.Packet import Packet


class InfoReplyPacket(Packet):
    """Sent by the server to the client to reply to a RequestInfoPacket."""

    def __init__(self, motd: str, player_count: int, state):
        self.motd = motd
        self.player_count = player_count
        self.state = state
