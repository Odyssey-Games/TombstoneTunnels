from common.src.packets.Packet import Packet


class HelloPacket(Packet):
    """Sent by the client to the server to login.

    If the server accepts this, it will send a HelloReplyPacket back with our token for this session/game.

    name = unique? todo name servers/login method?
    """
    def __init__(self, name):
        self.name = name

