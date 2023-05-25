# This file contains all the code for the client to communicate with the server, like login, packet sending, receiving and handeling.
#

import os
import pickle
import sys
from socket import socket, AF_INET, SOCK_DGRAM
from time import time

import requests as requests

from common.src.packets.s2c.MapChangePacket import MapChangePacket

sys.path.insert(1, os.path.join(sys.path[0], '..', '..'))

import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..', '..'))

from common.src.packets.Packet import Packet
from common.src.packets.c2s.AuthorizedPacket import AuthorizedPacket
from common.src.packets.c2s.HelloPacket import HelloPacket
from common.src.packets.c2s.DisconnectPacket import DisconnectPacket
from common.src.packets.c2s.PingPacket import PingPacket
from common.src.packets.s2c.HelloReplyPacket import HelloReplyPacket
from common.src.packets.s2c.EntityMovePacket import EntityMovePacket
from common.src.packets.s2c.PlayerSpawnPacket import PlayerSpawnPacket
from common.src.packets.s2c.PlayerRemovePacket import PlayerRemovePacket
from common.src.packets.s2c.PongPacket import PongPacket
from player import *
import client_state

PING_INTERVAL = 1  # we send a ping packet every second
PONG_TIMEOUT = 5  # we wait 5 seconds for a pong packet before we assume that the connection to the server is lost


class ClientNetworking:
    DEFAULT_SERVER_PORT = 5857

    def __init__(self, client):
        self.client = client
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.global_address = self.get_public_address()
        self.custom_address = ("localhost", self.DEFAULT_SERVER_PORT)
        self.current_address = self.global_address
        self.socket.setblocking(False)  # don't block the current thread when receiving packets
        self.token = None  # auth token that we get from the server when it accepts our HelloPacket
        self.last_ping = time()
        self.last_server_pong = time()

    @staticmethod
    def get_public_address():
        """Gets the address of the public server."""
        try:
            address = requests.get("https://api.odysseygames.de/server").text
            return address.split(":")[0], int(address.split(":")[1])
        except Exception as e:
            print("Could not get server address from api.odysseygames.de. Using localhost instead.")
            print(e)
            return "localhost"

    def set_custom_address(self, address: str):
        """Sets the address of the server to connect to."""
        split = address.split(":")
        if len(split) == 1:
            # we have no port
            port = self.DEFAULT_SERVER_PORT
        else:
            port = split[1]

        self.custom_address = (split[0], int(port))

    def try_login(self, custom: bool = False):
        if not self.socket:
            self.socket = socket(AF_INET, SOCK_DGRAM)

        if custom:
            self.current_address = self.custom_address
        else:
            self.current_address = self.global_address
        print(f"Connecting to address: {self.current_address}")
        self.socket.connect(self.current_address)
        self.socket.setblocking(False)

        """Try to send a HelloPacket to the server."""
        packet = HelloPacket(self.client.player_name)
        self.send_packet(packet)
        self.last_server_pong = time()
        print("Sent login packet.")

    def disconnect(self):
        if self.token:
            # we are connected
            packet = DisconnectPacket()
            self.send_packet(packet)
            print("Sent disconnect packet.")
        self.token = None
        self.socket.shutdown(2)
        self.socket = None

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
        self.socket.sendto(data, self.current_address)

    def _handle_packet(self, packet: Packet):
        """Handle a packet that was received from the server.

        This method is called by the try_receive method for each packet that was received.
        """
        if isinstance(packet, HelloReplyPacket):
            if packet.token is None:
                print("Server rejected our login.")
                self.disconnect()
                self.client.state = client_state.MAIN_MENU
            else:
                print("Server accepted our login.")
                self.token = packet.token
                self.client.player_uuid = packet.player_uuid
                self.client.state = client_state.IN_GAME
        elif isinstance(packet, PongPacket):
            print("Received pong packet.")
            self.last_server_pong = time()
        elif isinstance(packet, PlayerSpawnPacket):
            print("Received player spawn packet.")
            if self.client.player_uuid == packet.uuid:
                # this is our player
                self.client.update_player(ClientPlayer(self, packet.uuid, packet.position))
            else:
                # this is another player, add to entities
                self.client.entities.append(ClientPlayer(self, packet.uuid, packet.position))
        elif isinstance(packet, EntityMovePacket):
            # find entity in entities and update position
            for entity in (self.client.entities + [self.client.player]):
                if not entity:
                    continue
                if entity.uuid == packet.uuid:
                    entity.tile_position = packet.position
                    entity.animated_position = AbsPos.from_tile_pos(packet.position)  # todo smooth animation
                    break
        elif isinstance(packet, PlayerRemovePacket):
            # find player in entities and remove it
            # get entity first to prevent concurrent modification?
            client_entity = next((entity for entity in self.client.entities if entity.uuid == packet.uuid), None)
            if client_entity:
                self.client.entities.remove(client_entity)
        elif isinstance(packet, MapChangePacket):
            print(f"Received map change packet with map {packet.new_map}.")
            self.client.map = packet.new_map
            # todo animate map change
        # todo handle other packets here

    def tick(self, events, dt) -> bool:
        """Handle incoming packets and send ping packet.

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
                data = self.socket.recv(8192)
                if len(data) > 512:
                    print(f"Received big packet of size {len(data)} from {self.global_address}")
                packet = pickle.loads(data)
                if not isinstance(packet, Packet):
                    print(f"Received invalid packet: {packet}")
                    continue
                self._handle_packet(packet)
            except BlockingIOError:
                break  # no more packets to receive
            except Exception as e:
                print(f"Error while receiving packet: {e}. Disconnecting.")
                self.socket = None
                return False

        return True
