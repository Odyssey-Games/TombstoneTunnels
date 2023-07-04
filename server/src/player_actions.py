"""
Mechanics for simple player logic like connecting, disconnecting, pinging, timing out.
"""
from time import time

from common.src.direction import Dir2
from common.src.map.tile import Tile
from common.src.packets import *
from mechanics import Mechanics


class PlayerActions(Mechanics):
    def __init__(self, server):
        super().__init__(server)

    # players can only attack or move every 0.5 seconds (hostile entities can move every 1.5 seconds)
    ACTION_INTERVAL = 0.5

    def tick(self, packet, client_addr):
        # maybe move clients
        for user in self.server.clients:
            if time() - user.last_move_time >= self.ACTION_INTERVAL:
                # The player can either attack or move every MOVE_TIMEOUT seconds.
                if user.attacking and user.last_direction != Dir2.ZERO:
                    user.last_move_time = time()
                    self.server.send_packet_to_all(EntityAttackPacket(user.uuid))

                    # TODO multiple different player attacks
                    # get tiles in front of player (currently, we only have one attack type: sword - 1 tile in front)
                    attacked_tile = user.position + user.last_direction.to_tile_vector()
                    try:
                        # check if the tile is solid, if it is we can't attack it
                        tile = Tile.from_name(self.server.current_map.tiles[int(attacked_tile.y)][int(attacked_tile.x)])
                        if tile.is_solid:
                            continue
                        # damage entities on the attacked tile
                        for entity in self.server.entities:
                            if entity.position == attacked_tile:
                                print("Attacked entity: ", entity.uuid)
                                entity.health -= 10
                                # update entity health on the clients
                                self.server.send_packet_to_all(EntityHealthPacket(entity.uuid, entity.health))
                                if entity.health <= 0:
                                    # entity died; remove it on the server and clients
                                    self.server.entities.remove(entity)
                                    self.server.send_packet_to_all(EntityRemovePacket(entity.uuid))
                    except IndexError:
                        # no tile found
                        continue
                elif user.direction != Dir2.ZERO:
                    # player doesn't want to attack but wants to move
                    user.last_move_time = time()  # update move/action cooldown
                    new_position = user.position + Dir2(user.direction).to_tile_vector()  # possible new position
                    # collision check
                    if self.server.current_map.tiles is not None:
                        if new_position.y < 0 or new_position.x < 0 \
                                or new_position.y >= len(self.server.current_map.tiles) \
                                or new_position.x >= len(self.server.current_map.tiles[0]):
                            # tile is outside of map
                            continue
                        tile = Tile.from_name(self.server.current_map.tiles[int(new_position.y)][int(new_position.x)])
                        if tile.is_solid:
                            # tile is solid
                            continue
                    user.position = new_position  # set new pos on server
                    # send new position to clients
                    move_packet = EntityMovePacket(user.uuid, (user.position.x, user.position.y))
                    self.server.send_packet_to_all(move_packet)

        # handle incoming packets from clients affecting player movement (ChangeInputPacket)
        if isinstance(packet, ChangeInputPacket):
            # player has changed an input variable like movement direction or whether the player wants to attack
            user = next((client for client in self.server.clients if client.token == packet.token), None)
            user.direction = Dir2(packet.direction)
            if user.direction != Dir2.ZERO:
                user.last_direction = user.direction
            user.attacking = packet.attacking
            # update direction of player for other clients (purely visual)
            direction_packet = EntityDirectionPacket(user.uuid, user.direction.value)
            for client in self.server.clients:
                # only send direction packet to other clients; the player that changed direction knows it
                if client.addr != client_addr:
                    self.server.send_packet(direction_packet, client.addr)
