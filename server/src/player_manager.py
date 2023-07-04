"""
Manage simple player stuff like connecting, disconnecting, pinging, timing out.
"""
import secrets
from time import time

from pygame import Vector2

from common.src.packets import *
from entities import ServerPlayer
from mechanics import Mechanics


class PlayerManager(Mechanics):
    """
    Mechanics for managing simple player stuff like connecting, disconnecting, pinging, timing out.
    """
    def __init__(self, server):
        super().__init__(server)
        self.last_pong = time()

    PING_TIMEOUT = 5  # timeout clients after not pinging for 5 seconds
    PONG_INTERVAL = 1  # send a pong packet every second

    def tick(self, packet, client_addr):
        # maybe pong clients
        if self.last_pong + self.PONG_INTERVAL < time():
            self.server.send_packet_to_all(PongPacket())
            print(f"Ponged {len(self.server.clients)} clients.")
            self.last_pong = time()

        # check pings
        for client in self.server.clients:
            if client.last_ping + self.PING_TIMEOUT < time():
                print(f"Client {client.name} timed out.")
                self.server.entities.remove(client)
                player_remove_packet = EntityRemovePacket(client.uuid)
                self.server.send_packet_to_all(player_remove_packet)

        # handle packets
        if isinstance(packet, HelloPacket):
            if packet.name in [client.name for client in self.server.clients]:
                print(f"Client with name {packet.name} already exists.")
                return
            print(f"Client with name {packet.name} connected.")
            token = secrets.token_hex(16)
            player_uuid = secrets.token_hex(16)
            user = ServerPlayer(packet.name, client_addr, player_uuid, token, position=Vector2(1, 2))
            self.server.entities.append(user)
            reply_packet = HelloReplyPacket(token, player_uuid)
            self.server.send_packet(reply_packet, client_addr)

            # set map for this client
            map_packet = MapChangePacket(self.server.current_map.name, self.server.current_map.tiles)
            self.server.send_packet(map_packet, client_addr)

            # set own position for this client
            move_packet = EntityMovePacket(player_uuid, (user.position.x, user.position.y))
            self.server.send_packet(move_packet, client_addr)

            # set own health for this client
            health_packet = EntityHealthPacket(player_uuid, user.health)
            self.server.send_packet(health_packet, client_addr)

            # spawn other players for this client
            for other_user in self.server.clients:
                if other_user.addr != client_addr:
                    player_spawn_packet = PlayerSpawnPacket(other_user.name,
                                                            other_user.uuid,
                                                            (other_user.position.x, other_user.position.y),
                                                            other_user.health)
                    self.server.send_packet(player_spawn_packet, client_addr)

            # spawn player for all clients
            player_spawn_packet = PlayerSpawnPacket(user.name, player_uuid, (user.position.x, user.position.y),
                                                    user.health)
            self.server.send_packet_to_all(player_spawn_packet)

        elif isinstance(packet, DisconnectPacket):
            print(f"Received disconnect packet from {client_addr}")
            client = next((client for client in self.server.clients if client.token == packet.token), None)
            self.server.entities.remove(client)
            player_remove_packet = EntityRemovePacket(client.uuid)
            self.server.send_packet_to_all(player_remove_packet)

        elif isinstance(packet, PingPacket):
            print(f"Received ping from {client_addr}")
            for other_user in self.server.clients:
                if other_user.addr == client_addr:
                    other_user.last_ping = time()
                    break
