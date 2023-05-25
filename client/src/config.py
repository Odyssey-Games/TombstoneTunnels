import random


class ClientConfig:
    def __init__(self, player_name=f"Player{str(random.randrange(1000))}", custom_server_address=("localhost", 5857)):
        self.player_name = player_name
        self.custom_server_address = custom_server_address
