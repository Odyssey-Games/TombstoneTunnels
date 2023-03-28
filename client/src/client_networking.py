import pickle
from socket import socket, AF_INET, SOCK_DGRAM

from common.src.packets.Packet import Packet
from common.src.packets.c2s.AuthorizedPacket import AuthorizedPacket
from common.src.packets.c2s.HelloPacket import HelloPacket
from common.src.packets.s2c.HelloReplyPacket import HelloReplyPacket


class ClientNetworking:
    def __init__(self, name="John Doe", address=('127.0.0.1', 5000)):
        self.name = name
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.address = address
        self.socket.connect(address)
        self.socket.setblocking(False)  # don't block the current thread when receiving packets
        self.token = None  # auth token that we get from the server when it accepts our HelloPacket

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
        # todo handle other packets here

    def tick(self):
        """Handle incoming packets and todo send ping packet.

        This will not block the current thread, but will return if there is no packet to receive.
        """
        while True:  # we want to be able to receive multiple packets per tick
            try:
                data = self.socket.recv(1024)
                packet = pickle.loads(data)
                if not isinstance(packet, Packet):
                    print(f"Received invalid packet: {packet}")
                    continue
                self._handle_packet(packet)
            except BlockingIOError:
                break # no more packets to receive
