from common.src.packets.Packet import Packet


class HelloReplyPacket(Packet):
    """Sent by the server to the client to accept their login.

    This will be the case if the server/game is not yet full (and has not yet started!).
    """

    def __init__(self, token, player_uuid):
        self.token = token
        self.player_uuid = player_uuid
