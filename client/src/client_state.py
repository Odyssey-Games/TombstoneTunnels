# noinspection GrazieInspection
"""
This file contains all the possible game states. Each tick the client checks the current state and calls the
corresponding render/update functions. That way we only have to update the Client.state variable and the client
will automatically switch to the correct state (render the correct screen).
"""

MAIN_MENU = 0
CONNECTING = 1
IN_GAME = 2
