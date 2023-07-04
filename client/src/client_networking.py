"""
This file contains all the code for the client to communicate with the server,
like login, packet sending, receiving and handling.
"""

from socket import socket, AF_INET, SOCK_DGRAM

import requests as requests

import client_state
from common.src import networking
from common.src.map.map import Map
from entities import *

PING_INTERVAL = 1  # we send a ping packet every second
PONG_TIMEOUT = 5  # we wait 5 seconds for a pong packet before we assume that the connection to the server is lost


class ClientNetworking:
    """
    Class for handling all the networking logic on the client side. This includes sending and receiving packets,
    logging in, disconnecting, etc. This class is used by the Client class. Every tick we check if we have received
    any packets from the server and handle them accordingly. We also send a ping packet every second to the server
    and wait for a pong packet. If we don't receive a pong packet within 5 seconds, we assume that the connection
    to the server is lost and disconnect.
    """
    DEFAULT_SERVER_PORT = 5857

    def __init__(self, client):
        self.client = client
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.global_address = self.get_public_address()
        self.current_address = self.global_address
        self.socket.setblocking(False)  # don't block the current thread when receiving packets
        self.token = None  # auth token that we get from the server when it accepts our HelloPacket
        self.last_ping = time()
        self.last_server_pong = time()

    @staticmethod
    def get_public_address():
        """
        Gets the address of the public server. Currently, this is saved in a file on the server which we can access
        via the api.odysseygames.de website.
        """
        try:
            address = requests.get("https://api.odysseygames.de/server").text
            return address.split(":")[0], int(address.split(":")[1])
        except Exception as e:
            print("Could not get server address from api.odysseygames.de. Using localhost instead.")
            print(e)
            return "localhost"

    def try_login(self, custom: bool = False):
        """
        Try to connect/authorize to the server. This sends a HelloPacket to the server. If the server accepts our login,
        it will send us a HelloReplyPacket with our auth token. We save this token and use it for all future packets
        where we need to be authorized, e.g. when we send a PlayerMovePacket.

        :param custom: If True, we try to connect to the custom server address that the user has entered on the main
        menu (e.g. "localhost"). If False, we try to connect to the public server address.
        """
        # todo try connect in thread + fix multiple connection tries when clicking fast
        if not self.socket:
            self.socket = socket(AF_INET, SOCK_DGRAM)

        if custom:
            self.current_address = tuple(self.client.config.custom_server_address)
        else:
            self.current_address = self.global_address
        print(f"Connecting to address: {self.current_address}")
        try:
            self.socket.connect(self.current_address)
            self.socket.setblocking(False)

            # Try to send a HelloPacket to the server.
            packet = HelloPacket(self.client.config.player_name)
            self.send_packet(packet)
            self.last_server_pong = time()
            print("Sent login packet.")
        except Exception as e:
            # we could not connect to the server; go back to main menu
            print("Could not connect to server:")
            print(e)
            self.client.state = client_state.MAIN_MENU

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
        """
        Sends a packet to the server.

        Here we check if the packet is of type AuthorizedPacket. If this is the case,
        we require the token variable to be set and add it to the packet.
        """
        if isinstance(packet, AuthorizedPacket):
            if self.token is None:
                raise Exception("Token is not set but required for this packet.")
            packet.token = self.token

        data = networking.serialize(packet)
        self.socket.sendto(data, self.current_address)

    def _handle_packet(self, packet: Packet):
        """
        Handle a packet that was received from the server.

        This method is called by the try_receive method for each packet that was received.
        """
        if isinstance(packet, HelloReplyPacket):
            # after we sent the HelloPacket, the server can reply with a HelloReplyPacket when it accepts the login
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
            # pong packet should be sent by the server every second; after 5 seconds without a pong packet, we assume
            # that the connection to the server is lost
            print("Received pong packet.")
            self.last_server_pong = time()
        elif isinstance(packet, PlayerSpawnPacket):
            # the server sends us a PlayerSpawnPacket when a new player joins the game or when we join the game. When
            # the latter is the case we can update our player object with the data (position) from the packet.
            print("Received player spawn packet.")
            if self.client.player_uuid == packet.uuid:
                # this is our player
                self.client.update_player(ClientPlayer(self, packet.name, packet.uuid, packet.tile_position))
            else:
                # this is another player, add to entities
                self.client.entities.append(ClientPlayer(self, packet.name, packet.uuid, packet.tile_position))
        elif isinstance(packet, EntitySpawnPacket):
            # the server sends us an EntitySpawnPacket when a new entity is spawned in the game. We can add this entity
            # to our entities list. The entities list contains all entities including the players.
            print("Received entity spawn packet.")
            self.client.entities.append(ClientEntity(packet.uuid, EntityType(packet.entity_type), packet.tile_position, packet.health, hostile=True))

        elif isinstance(packet, EntityMovePacket):
            # find entity in entities and update position
            for entity in (self.client.entities + [self.client.player]):
                if not entity:
                    continue
                if entity.uuid == packet.uuid:
                    entity.tile_position = Vector2(packet.tile_position[0], packet.tile_position[1])
                    break
        elif isinstance(packet, EntityDirectionPacket):
            # find entity in entities and update direction
            for entity in (self.client.entities + [self.client.player]):
                if not entity:
                    continue
                if entity.uuid == packet.uuid:
                    entity.direction = Dir2(packet.direction)
                    if entity.direction != Dir2.ZERO:
                        entity.last_direction = entity.direction
                    if entity.direction == Dir2.LEFT:
                        entity.flip_image = True
                    elif entity.direction == Dir2.RIGHT:
                        entity.flip_image = False
                    break
        elif isinstance(packet, EntityRemovePacket):
            # find player in entities and remove it
            # get entity first to prevent concurrent modification?
            client_entity = next((entity for entity in self.client.entities if entity.uuid == packet.uuid), None)
            if client_entity:
                self.client.entities.remove(client_entity)
        elif isinstance(packet, EntityHealthPacket):
            # find entity in entities and update health
            for entity in (self.client.entities + [self.client.player]):
                if not entity:
                    continue
                if entity.uuid == packet.uuid:
                    if entity.health > packet.health:
                        # damage animation
                        entity.damage_animation_time = time()
                        pass
                    entity.health = packet.health
                    break

        elif isinstance(packet, MapChangePacket):
            new_map = Map(packet.name, packet.tiles)
            print(f"Received map change packet with map {new_map}.")
            self.client.map = new_map
            # todo animate map change

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
            try:
                self.send_packet(PingPacket())
            except Exception as e:
                print(f"Error while sending ping packet: {e}. Disconnecting.")
                self.socket = None
                return False
            self.last_ping = time()

        while True:  # we want to be able to receive multiple packets per tick
            try:
                data = self.socket.recv(8192)
                if len(data) > 512:
                    print(f"Received big packet of size {len(data)} from {self.global_address}")
                packet = networking.deserialize(data)
                if not isinstance(packet, Packet):
                    print(f"Received invalid packet: {packet}")
                    continue
                self._handle_packet(packet)
            except BlockingIOError:
                break  # no more packets to receive; return
            except Exception as e:
                print(f"Error while receiving packet: {e}. Disconnecting.")
                self.socket = None
                return False  # return false to indicate that the connection was lost

        return True
