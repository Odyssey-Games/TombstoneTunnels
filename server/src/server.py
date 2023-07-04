"""
Main server (entrypoint) file.
The server logic is divided into the following mechanics:
- PlayerManager: Handles player connections and disconnections.
- PlayerActions: Handles player actions (e.g. movement, attacking, etc.).
- EntityManager: Handles all entities (players and hostile creatures) and their logic.
"""
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..', '..'))

from socket import *
from entities import ServerPlayer
from entity_manager import EntityManager
from player_manager import PlayerManager
from player_actions import PlayerActions
from map_manager import MapManager
from common.src.common import VERSION
from common.src import networking
from common.src.packets import *

SERVER_ADDRESS = ('0.0.0.0', 5857)


class Server:
    def __init__(self):
        self.entities = []  # list of all entities (and players) except the player of this client
        self.socket = socket(AF_INET, SOCK_DGRAM)  # UDP socket
        self.socket.setblocking(False)  # we don't want the socket to block the main thread
        self.socket.bind(SERVER_ADDRESS)  # bind the socket to the server address; see above
        self.map_manager = MapManager()  # map manager for handling (and currently generating) maps
        self.current_map = self.map_manager.maps[0]  # the current map we're on

        # Mechanics -> managers for specific server-sided tasks
        self.mechanics = (
            EntityManager(self),  # handles all entities (players and hostile creatures) and their logic
            PlayerManager(self),  # handles player connections and disconnections
            PlayerActions(self),  # handles player actions (e.g. movement, attacking, etc.)
        )

    @property
    def clients(self):
        """
        :return: list of all connected clients (ServerPlayer instances)
        """
        return [ent for ent in self.entities if isinstance(ent, ServerPlayer)]

    def send_packet(self, packet, addr: tuple):
        """
        Send a packet to a specific client address.
        :param packet: Packet instance to send
        :param addr: client address to send the packet to (ip, port)
        """
        data = networking.serialize(packet)  # serialize the packet to bytes
        if len(data) > 1024:
            print(f"Sending big packet of size {len(data)} to {addr}")
        self.socket.sendto(data, addr)  # tell the UDP socket to send the data to the client

    def send_packet_to_all(self, packet):
        """
        Send a packet to all connected clients. See send_packet.
        """
        for client1 in self.clients:
            self.send_packet(packet, client1.addr)

    def _rcvfrom(self, bufsize: int) -> (Packet | None, tuple | None):
        """
        Receive a packet from the UDP socket.
        :param bufsize: the maximum size of the packet to receive
        :return: the received Packet instance and the address it was received from (tuple) when a packet was received
        """
        try:
            data, addr = self.socket.recvfrom(bufsize)
            if len(data) > 512:
                print(f"Received big packet of size {len(data)} from {addr}")
            packet = networking.deserialize(data)  # receive a packet from the UDP socket
            if not isinstance(packet, Packet):
                print(f"Received invalid packet: {packet}")
                return None, None
            if isinstance(packet, AuthorizedPacket):
                if packet.token is None or packet.token not in [other_client.token for other_client in self.clients]:
                    print(f"Received packet from unauthorized client: {packet}")
                    return None, None
            return packet, addr
        except BlockingIOError:
            # no packet was received
            return None, None
        except ConnectionResetError:
            # the client probably disconnected
            return None, None

    def tick(self):
        """
        Tick the server once; this means receiving packets from clients and ticking each mechanic
        with the received packet (if any).
        """
        client_packet, client_addr = self._rcvfrom(1024)

        for mechanics in self.mechanics:
            # tick each mechanic
            mechanics.tick(client_packet, client_addr)


def main():
    """
    The main server entry point.

    Currently, one server instance means one "game" (one game state, one set of players, one seed/map, etc.).
    """

    # when running the server with the --debug flag, exceptions will not be caught
    debug = "--debug" in sys.argv

    print(f"Booting... ({VERSION})") if not debug else print(f"Booting... ({VERSION}) (debug mode)")
    try:
        server = Server()
    except OSError as e:
        # OSError will be raised when the port is already in use
        print("Could not initialize server. Is it already running?")
        raise e

    print("Starting main loop...")
    while True:
        try:
            server.tick()  # non-blocking tick call; does not wait for client packets
        except KeyboardInterrupt:
            break  # exit the main loop when the user presses Ctrl+C
        except Exception as e:
            if debug:
                raise e
            # we don't want to crash the server when an unexpected exception occurs; only do this in debug mode
            print("Exception in main loop:")
            print(e)

    print("Shutting down...")


if __name__ == '__main__':
    # main() is called when the server.py file is run directly
    main()
