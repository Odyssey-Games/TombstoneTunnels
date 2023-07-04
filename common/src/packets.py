"""
This file contains all packets that are sent over the network.

The packets are divided into two main categories:
- Client to server (c2s)
    Client packets are further divided into two categories:
    - Authorized (AuthorizedPacket)
        Packets that are sent when the client is already authorized.
        Example: PlayerMovePacket, ChangeInputPacket, etc.
    - Unauthorized
        Packets that are sent when the client is not yet authorized.
        Example: HelloPacket, RequestInfoPacket (currently not implemented), etc.
- Server to client (s2c)

Serialization works using json due to pickle being unsafe (possible arbitrary code execution). This means that
the packets must only use types that are supported by json (dict, list, int, float, str, bool, None), so no
custom classes are allowed/custom classes must be converted when creating the packet or reading its content.
"""


# Base class
class Packet:
    """Base class for all packets.

    The subclasses should have only the properties that should be sent over the network.
    """
    pass


# Client to server
class AuthorizedPacket(Packet):
    def __init__(self):
        self.token = None

    """Baseclass for all packets that are sent when the client is already authorized.

    Example: PlayerMovePacket, PlayerAttackEntityPacket, etc.

    In the send logic of the client, it should check if a packet is an instance of this class, and if so,
    add the client token to the packet (or complain if the client is not authorized).
    """
    pass


class ChangeInputPacket(AuthorizedPacket):
    """Sent by the client to the server to indicate that the player's input has changed."""

    def __init__(self, direction: int, attacking: bool):
        super().__init__()
        self.direction = direction
        self.attacking = attacking


class DisconnectPacket(AuthorizedPacket):
    """Sent by the client to the server to tell it that it wants to quit."""
    pass


class HelloPacket(Packet):
    """Sent by the client to the server to login.

    If the server accepts this, it will send a HelloReplyPacket back with our token for this session/game.

    name = unique? todo name servers/login method?
    """

    def __init__(self, name):
        self.name = name


class PingPacket(Packet):
    """Sent by the client to the server to announce that it is still alive."""
    pass


# Server to client
class EntityDirectionPacket(Packet):
    """
    Sent by the server to clients to indicate that an entity changed their looking direction.
    This is needed for updating the player sprites on the other clients.
    """

    def __init__(self, uuid: str, direction: int):
        self.uuid = uuid  # unique identifier of the player that moved
        self.direction = direction  # new direction of the player


class EntityMovePacket(Packet):
    """Sent by the server to clients to indicate that an entity moved to the new specified *tile* position."""

    def __init__(self, uuid: str, tile_position: (int, int)):
        self.uuid = uuid  # unique identifier of the player that moved
        self.tile_position = tile_position  # new position of the player in tile coordinates


class EntityHealthPacket(Packet):
    """Sent by the server to clients to indicate that an entity's health changed."""

    def __init__(self, uuid: str, health: int):
        self.uuid = uuid  # unique identifier of the player that moved
        self.health = health  # new health of the player


class EntityAttackPacket(Packet):
    """
    Sent by the server to clients to indicate that an entity started attacking.

    Currently, there is only one attack method for each entity, so the client will know what animation to play.
    """

    def __init__(self, uuid: str):
        self.uuid = uuid  # unique identifier of the entity that is attacking


class HelloReplyPacket(Packet):
    """Sent by the server to the client to accept their login.

    This will be the case if the server/game is not yet full (and has not yet started!).
    """

    def __init__(self, token, player_uuid):
        self.token = token
        self.player_uuid = player_uuid


class InfoReplyPacket(Packet):
    """Sent by the server to the client to reply to a RequestInfoPacket."""

    def __init__(self, motd: str, player_count: int, state):
        self.motd = motd
        self.player_count = player_count
        self.state = state


class MapChangePacket(Packet):
    """
    Sent by the server to clients to indicate that the map changed,
    e.g. when match-making is over and the game starts.
    """

    def __init__(self, name: str, tiles: list[list[str]]):
        """
        :param name: the name of the new map
        :param tiles: the new map (list of lists of tile names - y, x)
        """
        self.name = name
        self.tiles = tiles


class EntityRemovePacket(Packet):
    """Sent by the server to clients to indicate that a player/entity was removed from the current world / left."""

    def __init__(self, uuid):
        self.uuid = uuid  # unique identifier of the player that left


class PlayerSpawnPacket(Packet):
    """Sent by the server to clients to indicate that a player spawned at the specified tile position."""

    def __init__(self, name: str, uuid: str, tile_position: (int, int), health: int):
        self.name = name  # name of the player that spawned
        self.uuid = uuid  # unique identifier of the player that spawned
        self.tile_position = tile_position  # position of the player in tile coordinates
        self.health = health  # health of the player


class EntitySpawnPacket(Packet):
    """Sent by the server to clients to indicate that a hostile entity spawned at the specified tile position."""

    def __init__(self, uuid: str, entity_type: str, tile_position: (int, int), health: int):
        self.uuid = uuid  # unique identifier of the entity that spawned
        self.entity_type = entity_type  # type of the entity that spawned
        self.tile_position = tile_position  # position of the entity in tile coordinates
        self.health = health  # health of the entity


class PongPacket(Packet):
    """Sent by the server to clients to announce that it is still alive and the respective client is still connected."""
    pass


# Used for deserialization so that we don't have to hardcode the packet types
# list of tuples (name, class) for each packet
packet_classes = [(key, value) for key, value in locals().copy().items() if key.endswith("Packet") and key != "Packet"]
