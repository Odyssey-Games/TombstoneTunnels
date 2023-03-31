from common.src.packets.c2s.AuthorizedPacket import AuthorizedPacket


class DisconnectPacket(AuthorizedPacket):
    """Sent by the client to the server to tell it that it wants to quit."""
    pass
