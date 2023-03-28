import pickle
import secrets
from socket import *
from threading import Thread
from time import sleep, time

from User import User
from common.src.common import print_hi
from common.src.packets.c2s.AuthorizedPacket import AuthorizedPacket
from common.src.packets.c2s.HelloPacket import *
from common.src.packets.c2s.PingPacket import PingPacket
from common.src.packets.c2s.PlayerMovePacket import PlayerMovePacket
from common.src.packets.c2s.RequestInfoPacket import RequestInfoPacket
from common.src.packets.s2c.HelloReplyPacket import HelloReplyPacket
from common.src.packets.s2c.InfoReplyPacket import InfoReplyPacket

SERVER_ADDRESS = ('localhost', 5000)
PING_TIMEOUT = 5  # timeout clients after not pinging for 5 seconds


class Server:
    clients: list[User]

    def __init__(self, address: tuple):
        self.clients = []
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(address)
        timeouts_thread = Thread(target=self.manage_timeouts)
        timeouts_thread.start()

    def send_packet(self, packet, addr: tuple):
        data = pickle.dumps(packet)
        self.socket.sendto(data, addr)

    def rcvfrom(self, bufsize: int):
        data, addr = self.socket.recvfrom(bufsize)
        packet = pickle.loads(data)
        if not isinstance(packet, Packet):
            print(f"Received invalid packet: {packet}")
            return None, None
        if isinstance(packet, AuthorizedPacket):
            if packet.token is None or packet.token not in [client.token for client in self.clients]:
                print(f"Received packet from unauthorized client: {packet}")
                return None, None
        return packet, addr

    def manage_timeouts(self):
        while True:
            for client in self.clients:
                if client.last_ping + PING_TIMEOUT < time():
                    print(f"Client {client.name} timed out.")
                    self.clients.remove(client)
            sleep(1)  # todo proper concurrency (asyncio?)


if __name__ == '__main__':
    """The main server entry point.
    
    Currently one server instance means one "game" (one game state, one set of players, one seed/map, etc.).
    """
    print_hi('Server')

    server = Server(('localhost', 5000))
    while True:
        client_packet, client_addr = server.rcvfrom(1024)
        if client_packet is None or client_addr is None:
            continue

        print(f"Received {client_packet} from {client_addr}")
        if isinstance(client_packet, HelloPacket):
            if client_packet.name in [client.name for client in server.clients]:
                print(f"Client with name {client_packet.name} already exists.")
                continue
            print(f"Client with name {client_packet.name} connected.")
            token = secrets.token_hex(16)
            user = User(client_packet.name, client_addr, token)
            server.clients.append(user)
            reply_packet = HelloReplyPacket(token)
            server.send_packet(reply_packet, client_addr)

        elif isinstance(client_packet, RequestInfoPacket):
            print(f"Received info request from {client_addr}")
            player_count = len(server.clients)
            reply_packet = InfoReplyPacket('Hello World!', player_count, 'lobby')
            server.send_packet(reply_packet, client_addr)

        elif isinstance(client_packet, PingPacket):
            print(f"Received ping from {client_addr}")
            for client in server.clients:
                if client.addr == client_addr:
                    client.last_ping = time()
                    break

        elif isinstance(client_packet, PlayerMovePacket):
            print(f"Received player move from {client_addr} with new position: {client_packet.position}")
