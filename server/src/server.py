import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..', '..'))

import secrets
from socket import *
from time import time

from pygame import Vector2

from User import User
from map_manager import MapManager
from common.src.direction import Dir2
from common.src import networking
from common.src.map.tile import Tile
from common.src.packets import *

SERVER_ADDRESS = ('0.0.0.0', 5857)
PING_TIMEOUT = 5  # timeout clients after not pinging for 5 seconds
PONG_INTERVAL = 1  # send a pong packet every second
MOVE_TIMEOUT = 0.5


class Server:
    """
    :type clients: list[User]
    """

    def __init__(self):
        self.clients = []
        self.sockets = [socket(AF_INET, SOCK_DGRAM), socket(AF_INET, SOCK_STREAM)]
        for sock in self.sockets:
            sock.setblocking(False)
            sock.bind(SERVER_ADDRESS)
            try:  # only for tcp sockets
                sock.listen(5)
            except OSError:
                pass
            print("Bound to", SERVER_ADDRESS)

    def send_packet(self, packet, addr: tuple, socket_type: int):
        data = networking.serialize(packet)
        if len(data) > 1024:
            print(f"Sending big packet of size {len(data)} to {addr} ({socket_type})")
        self.sockets[socket_type].sendto(data, addr)

    def send_packet_to_user(self, packet, user: User):
        self.send_packet(packet, user.addr, user.socket_type)

    def rcvfrom(self, bufsize: int):
        try:
            for sock_type, sock in enumerate(self.sockets):
                try:
                    sock.accept()
                    print("Accepted new tcp connection")
                except Exception as e:
                    pass
                data, addr = sock.recvfrom(bufsize)
                if len(data) > 512:
                    print(f"Received big packet of size {len(data)} from {addr}")
                packet = networking.deserialize(data)
                if not isinstance(packet, Packet):
                    print(f"Received invalid packet: {packet}")
                    return None, None, sock_type
                if isinstance(packet, AuthorizedPacket):
                    if packet.token is None or packet.token not in [other_client.token for other_client in
                                                                    self.clients]:
                        print(f"Received packet from unauthorized client: {packet}")
                        return None, None, sock_type
                return packet, addr, sock_type
        except BlockingIOError:
            return None, None, 0
        except ConnectionResetError:
            return None, None, 0

    def close(self):
        for sock in self.sockets:
            sock.close()


if __name__ == '__main__':
    # TODO simplify server code
    """
    The main server entry point.
    
    Currently one server instance means one "game" (one game state, one set of players, one seed/map, etc.).
    """
    print("Booting...")

    try:
        server = Server()
    except OSError as e:
        print("Could not start server. Is it already running?")
        raise e

    map_manager = MapManager()
    current_map = map_manager.maps[0]

    last_pong = time()
    while True:
        try:
            # maybe pong clients
            if last_pong + PONG_INTERVAL < time():
                for other_user in server.clients:
                    server.send_packet_to_user(PongPacket(), other_user)
                print(f"Ponged {len(server.clients)} clients.")
                last_pong = time()

            # maybe move clients
            for user in server.clients:
                if user.direction != Dir2.ZERO and time() - user.last_move_time >= MOVE_TIMEOUT:
                    user.last_move_time = time()
                    new_position = user.position + Dir2(user.direction).to_tile_vector()
                    # collision check
                    if current_map.tiles is not None:
                        if new_position.y < 0 or new_position.x < 0 or new_position.y >= len(
                                current_map.tiles) or new_position.x >= len(current_map.tiles[0]):
                            continue
                        tile = Tile.from_name(current_map.tiles[int(new_position.y)][int(new_position.x)])
                        if tile.is_solid:
                            continue
                    user.position = new_position
                    move_packet = EntityMovePacket(user.uuid, (user.position.x, user.position.y))
                    for moving_user in server.clients:
                        server.send_packet_to_user(move_packet, moving_user)

            # check pings
            for client in server.clients:
                if client.last_ping + PING_TIMEOUT < time():
                    print(f"Client {client.name} timed out.")
                    server.clients.remove(client)
                    player_remove_packet = PlayerRemovePacket(client.uuid)
                    for other_user in server.clients:
                        server.send_packet_to_user(player_remove_packet, other_user)

            client_packet, client_addr, socket_type = server.rcvfrom(1024)
            if client_packet is None or client_addr is None:
                continue  # no packet received

            if isinstance(client_packet, HelloPacket):
                if client_packet.name in [client.name for client in server.clients]:
                    print(f"Client with name {client_packet.name} already exists.")
                    continue
                print(f"Client with name {client_packet.name} connected.")
                token = secrets.token_hex(16)
                player_uuid = secrets.token_hex(16)
                user = User(client_packet.name, client_addr, player_uuid, token, socket_type, start_pos=Vector2(1, 2))
                server.clients.append(user)
                reply_packet = HelloReplyPacket(token, player_uuid)
                server.send_packet_to_user(reply_packet, user)

                # set map for this client
                map_packet = MapChangePacket(current_map.name, current_map.tiles)
                server.send_packet_to_user(map_packet, user)

                # set own position for this client
                move_packet = EntityMovePacket(player_uuid, (user.position.x, user.position.y))
                server.send_packet_to_user(move_packet, user)

                # spawn other players for this client
                for other_user in server.clients:
                    if other_user.addr != client_addr:
                        player_spawn_packet = PlayerSpawnPacket(other_user.name,
                                                                other_user.uuid,
                                                                (other_user.position.x, other_user.position.y))
                        server.send_packet_to_user(player_spawn_packet, user)

                # spawn player for all clients
                player_spawn_packet = PlayerSpawnPacket(user.name, player_uuid, (user.position.x, user.position.y))
                for other_user in server.clients:
                    server.send_packet_to_user(player_spawn_packet, other_user)

            elif isinstance(client_packet, RequestInfoPacket):
                print(f"Received info request from {client_addr}")
                player_count = len(server.clients)
                reply_packet = InfoReplyPacket('Hello World!', player_count, 'lobby')
                server.send_packet(reply_packet, client_addr, socket_type)

            elif isinstance(client_packet, DisconnectPacket):
                print(f"Received disconnect packet from {client_addr}")
                client = next((client for client in server.clients if client.token == client_packet.token), None)
                server.clients.remove(client)
                player_remove_packet = PlayerRemovePacket(client.uuid)
                for other_user in server.clients:
                    server.send_packet_to_user(player_remove_packet, other_user)

            elif isinstance(client_packet, PingPacket):
                print(f"Received ping from {client_addr}")
                for other_user in server.clients:
                    if other_user.addr == client_addr:
                        other_user.last_ping = time()
                        break

            elif isinstance(client_packet, ChangeInputPacket):
                user = next((client for client in server.clients if client.token == client_packet.token), None)
                user.direction = Dir2(client_packet.direction)
                # update direction for other clients
                direction_packet = EntityDirectionPacket(user.uuid, user.direction.value)
                for client in server.clients:
                    if client.addr != client_addr:
                        server.send_packet_to_user(direction_packet, client)

        except KeyboardInterrupt:
            break
        except Exception as e:
            # we don't want to crash the server because of a client
            print("Exception in main loop:")
            print(e)

    print("Shutting down...")
    server.close()
