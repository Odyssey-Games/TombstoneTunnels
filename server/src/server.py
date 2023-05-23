import os
import pickle
import secrets
import sys
from socket import *
from time import time

from User import User
from common.src.map.map_manager import MapManager
from common.src.packets.s2c.MapChangePacket import MapChangePacket
from common.src.vec.Dir2 import Dir2
from common.src.vec.TilePos import TilePos

sys.path.insert(1, os.path.join(sys.path[0], '..', '..'))

from common.src.packets.c2s.DisconnectPacket import DisconnectPacket
from common.src.common import print_hi
from common.src.packets.c2s.AuthorizedPacket import AuthorizedPacket
from common.src.packets.c2s.ChangeInputPacket import ChangeInputPacket
from common.src.packets.c2s.HelloPacket import *
from common.src.packets.c2s.PingPacket import PingPacket
from common.src.packets.c2s.RequestInfoPacket import RequestInfoPacket
from common.src.packets.s2c.HelloReplyPacket import HelloReplyPacket
from common.src.packets.s2c.InfoReplyPacket import InfoReplyPacket
from common.src.packets.s2c.EntityMovePacket import EntityMovePacket
from common.src.packets.s2c.PlayerSpawnPacket import PlayerSpawnPacket
from common.src.packets.s2c.PlayerRemovePacket import PlayerRemovePacket
from common.src.packets.s2c.PongPacket import PongPacket

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
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setblocking(False)
        self.socket.bind(SERVER_ADDRESS)

    def send_packet(self, packet, addr: tuple):
        data = pickle.dumps(packet)
        if len(data) > 1024:
            print(f"Sending big packet of size {len(data)} to {addr}")
        self.socket.sendto(data, addr)

    def rcvfrom(self, bufsize: int):
        try:
            data, addr = self.socket.recvfrom(bufsize)
            if len(data) > 512:
                print(f"Received big packet of size {len(data)} from {addr}")
            packet = pickle.loads(data)
            if not isinstance(packet, Packet):
                print(f"Received invalid packet: {packet}")
                return None, None
            if isinstance(packet, AuthorizedPacket):
                if packet.token is None or packet.token not in [client.token for client in self.clients]:
                    print(f"Received packet from unauthorized client: {packet}")
                    return None, None
            return packet, addr
        except BlockingIOError:
            return None, None
        except ConnectionResetError:
            return None, None


if __name__ == '__main__':
    # TODO simplify server code
    """
    The main server entry point.
    
    Currently one server instance means one "game" (one game state, one set of players, one seed/map, etc.).
    """
    print_hi('Server')

    try:
        server = Server()
    except OSError as e:
        print("Could not start server. Is it already running?")
        raise e

    map_manager = MapManager()
    current_map = map_manager.maps[0]
    print("Current map:", current_map.name)
    print(f"Current map 0/0: {current_map.tiles[0][0].name}")
    print(f"Current map 0/1: {current_map.tiles[0][1].name}")
    print(f"Current map 1/0: {current_map.tiles[1][0].name}")
    print(f"Current map 1/1: {current_map.tiles[1][1].name}")

    last_pong = time()
    while True:
        try:
            # maybe pong clients
            if last_pong + PONG_INTERVAL < time():
                for other_user in server.clients:
                    server.send_packet(PongPacket(), other_user.addr)
                print(f"Ponged {len(server.clients)} clients.")
                last_pong = time()

            # maybe move clients
            for user in server.clients:
                if user.direction != Dir2.ZERO and time() - user.last_move_time >= MOVE_TIMEOUT:
                    user.last_move_time = time()
                    new_position = user.position + user.direction.to_vector()
                    # collision check
                    if current_map.tiles is not None:
                        if new_position.y < 0 or new_position.x < 0 or new_position.y >= len(current_map.tiles) or new_position.x >= len(current_map.tiles[0]):
                            print(f"Player {user.name} is colliding with a wall: {new_position} | out of bounds.")
                            continue
                        tile = current_map.tiles[new_position.y][new_position.x]
                        if tile.is_solid:
                            print(f"Player {user.name} is colliding with a wall: {new_position} | {tile.name}.")
                            continue
                    user.position += user.direction.to_vector()
                    move_packet = EntityMovePacket(user.uuid, user.position)
                    for moving_user in server.clients:
                        print(f"Sending move packet to {moving_user.name} with position {user.position}.")
                        server.send_packet(move_packet, moving_user.addr)

            # check pings
            for client in server.clients:
                if client.last_ping + PING_TIMEOUT < time():
                    print(f"Client {client.name} timed out.")
                    server.clients.remove(client)

            client_packet, client_addr = server.rcvfrom(1024)
            if client_packet is None or client_addr is None:
                continue  # no packet received

            if isinstance(client_packet, HelloPacket):
                if client_packet.name in [client.name for client in server.clients]:
                    print(f"Client with name {client_packet.name} already exists.")
                    continue
                print(f"Client with name {client_packet.name} connected.")
                token = secrets.token_hex(16)
                player_uuid = secrets.token_hex(16)
                user = User(client_packet.name, client_addr, player_uuid, token, start_pos=TilePos(1, 2))
                server.clients.append(user)
                reply_packet = HelloReplyPacket(token, player_uuid)
                server.send_packet(reply_packet, client_addr)

                # set map for this client
                map_packet = MapChangePacket(current_map)
                server.send_packet(map_packet, client_addr)

                # set own position for this client
                move_packet = EntityMovePacket(player_uuid, user.position)
                server.send_packet(move_packet, client_addr)

                # spawn other players for this client
                for other_user in server.clients:
                    if other_user.addr != client_addr:
                        player_spawn_packet = PlayerSpawnPacket(other_user.uuid, other_user.position)
                        server.send_packet(player_spawn_packet, client_addr)

                # spawn player for all clients
                player_spawn_packet = PlayerSpawnPacket(player_uuid, user.position)
                for other_user in server.clients:
                    server.send_packet(player_spawn_packet, other_user.addr)

            elif isinstance(client_packet, RequestInfoPacket):
                print(f"Received info request from {client_addr}")
                player_count = len(server.clients)
                reply_packet = InfoReplyPacket('Hello World!', player_count, 'lobby')
                server.send_packet(reply_packet, client_addr)

            elif isinstance(client_packet, DisconnectPacket):
                print(f"Received disconnect packet from {client_addr}")
                client = next((client for client in server.clients if client.token == client_packet.token), None)
                server.clients.remove(client)
                player_remove_packet = PlayerRemovePacket(client.uuid)
                for other_user in server.clients:
                    server.send_packet(player_remove_packet, other_user.addr)

            elif isinstance(client_packet, PingPacket):
                print(f"Received ping from {client_addr}")
                for other_user in server.clients:
                    if other_user.addr == client_addr:
                        other_user.last_ping = time()
                        break

            elif isinstance(client_packet, ChangeInputPacket):
                user = next((client for client in server.clients if client.token == client_packet.token), None)
                user.direction = client_packet.client_input.direction

                print("Received ChangeInputPacket from client: " + str(user.direction))
        except KeyboardInterrupt:
            print("Shutting down...")
            break
        except Exception as e:
            # we don't want to crash the server because of a client
            print("Exception in main loop:")
            raise e
