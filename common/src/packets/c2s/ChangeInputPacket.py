from common.src.entity.ClientInput import ClientInput
from common.src.packets.c2s.AuthorizedPacket import AuthorizedPacket


class ChangeInputPacket(AuthorizedPacket):
    """Sent by the client to the server to indicate that the player's input has changed."""

    def __init__(self, client_input: ClientInput):
        super().__init__()
        self.client_input = client_input
