from common.src.map.map import Map
from common.src.packets.Packet import Packet


class MapChangePacket(Packet):
    """
    Sent by the server to clients to indicate that the map changed,
    e.g. when match-making is over and the game starts.
    """

    def __init__(self, new_map: Map):
        """
        :param new_map: the new map with its tiles
        """
        self.new_map = new_map
