import random


class ClientConfig:
    """
    Class representing the client configuration, storing the player name and the custom server address.
    The variables can be changed in the main menu.
    """
    def __init__(self, player_name=f"Player{str(random.randrange(1000))}", custom_server_address=("localhost", 5857)):
        self.player_name = player_name
        self.custom_server_address = custom_server_address
