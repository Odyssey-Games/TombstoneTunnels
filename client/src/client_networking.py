import os
import pickle
import sys
from socket import socket, AF_INET, SOCK_DGRAM
from time import time

sys.path.insert(1, os.path.join(sys.path[0], '..\\..'))

import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..\\..'))

from common.src.packets.Packet import Packet
from common.src.packets.c2s.AuthorizedPacket import AuthorizedPacket
from common.src.packets.c2s.HelloPacket import HelloPacket
from common.src.packets.c2s.PingPacket import PingPacket
from common.src.packets.s2c.HelloReplyPacket import HelloReplyPacket
from common.src.packets.s2c.PlayerMovePacket import PlayerMovePacket
from common.src.packets.s2c.PlayerSpawnPacket import PlayerSpawnPacket
from common.src.packets.s2c.PongPacket import PongPacket
from player import *

PING_INTERVAL = 1  # we send a ping packet every second
PONG_TIMEOUT = 5  # we wait 5 seconds for a pong packet before we assume that the connection to the server is lost


class ClientNetworking:
    def __init__(self, client, name="John Doe", address=('127.0.0.1', 5000)):
        self.client = client
        self.name = name
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.address = address
        self.socket.connect(address)
        self.socket.setblocking(False)  # don't block the current thread when receiving packets
        self.token = None  # auth token that we get from the server when it accepts our HelloPacket
        self.last_ping = time()
        self.last_server_pong = time()

    def try_login(self):
        """Try to send a HelloPacket to the server."""
        packet = HelloPacket(self.name)
        self.send_packet(packet)
        print("Sent login packet.")

    def send_packet(self, packet: Packet):
        """Sends a packet to the server.

        Here we use pickle to create a byte array from the packet object. Additionally, we check if the packet is of
        type AuthorizedPacket. If this is the case, we require the token variable to be set and add it to the packet.
        """
        if isinstance(packet, AuthorizedPacket):
            if self.token is None:
                raise Exception("Token is not set but required for this packet.")
            packet.token = self.token

        data = pickle.dumps(packet)
        self.socket.sendto(data, self.address)

    def _handle_packet(self, packet: Packet):
        """Handle a packet that was received from the server.

        This method is called by the try_receive method for each packet that was received.
        """
        if isinstance(packet, HelloReplyPacket):
            if packet.token is None:
                print("Server rejected our login.")
            else:
                print("Server accepted our login.")
                self.token = packet.token
                self.client.player_uuid = packet.player_uuid
        elif isinstance(packet, PongPacket):
            print("Received pong packet.")
            self.last_server_pong = time()
        elif isinstance(packet, PlayerSpawnPacket):
            print("Received player spawn packet.")
            if self.client.player_uuid == packet.uuid:
                # this is our player
                self.client.update_player(Player(self, packet.uuid, packet.position))
            else:
                # this is another player, todo add to entities
                self.client.entities.append(Player(self, packet.uuid, packet.position))
        elif isinstance(packet, PlayerMovePacket):
            # find player in entities and update position
            for entity in self.client.entities:
                if entity.uuid == packet.uuid:
                    entity.position = packet.position
                    break
        # todo handle other packets here

    def tick(self, events, dt) -> bool:
        """Handle incoming packets and todo send ping packet.

        This will not block the current thread, but will return if there is no packet to receive.

        :return True if the connection to the server is still alive, False otherwise
        """
        # Check server connection
        if (time() - self.last_server_pong) > PONG_TIMEOUT:
            print("Connection to server lost.")
            return False
        # Maybe ping server
        if (time() - self.last_ping) > PING_INTERVAL:
            print("Sending ping packet.")
            self.send_packet(PingPacket())
            self.last_ping = time()

        while True:  # we want to be able to receive multiple packets per tick
            try:
                data = self.socket.recv(1024)
                packet = pickle.loads(data)
                if not isinstance(packet, Packet):
                    print(f"Received invalid packet: {packet}")
                    continue
                self._handle_packet(packet)
            except BlockingIOError:
                break  # no more packets to receive
            except Exception as e:
                print(f"Error while receiving packet: {e}. Disconnecting.")
                return False

        return True
