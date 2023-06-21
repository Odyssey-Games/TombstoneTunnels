"""
Manage simple player stuff like connecting, disconnecting, pinging, timing out.
"""
from time import time

from common.src.direction import Dir2
from common.src.map.tile import Tile
from common.src.packets import *
from mechanics import Mechanics


class PlayerActions(Mechanics):
    def __init__(self, server):
        super().__init__(server)

    ACTION_INTERVAL = 0.5  # players can only attack or move every 0.5 seconds

    def tick(self, packet, client_addr):
        # maybe move clients
        for user in self.server.clients:
            if time() - user.last_move_time >= self.ACTION_INTERVAL:
                # The player can either attack or move every MOVE_TIMEOUT seconds.
                if user.attacking and user.last_direction != Dir2.ZERO:
                    user.last_move_time = time()
                    self.server.send_packet_to_all(EntityAttackPacket(user.uuid))

                    # TODO multiple different player attacks
                    # get tiles in front of player
                    attacked_tile = user.position + user.last_direction.to_tile_vector()
                    try:
                        tile = Tile.from_name(self.server.current_map.tiles[int(attacked_tile.y)][int(attacked_tile.x)])
                        if tile.is_solid:
                            continue
                        # damage entities
                        for entity in self.server.entities:
                            if entity.position == attacked_tile:
                                print("Attacked entity: ", entity.uuid)
                                entity.health -= 10
                                self.server.send_packet_to_all(EntityHealthPacket(entity.uuid, entity.health))
                                if entity.health <= 0:
                                    self.server.send_packet_to_all(EntityRemovePacket(entity.uuid))
                    except IndexError:
                        continue
                elif user.direction != Dir2.ZERO:
                    user.last_move_time = time()
                    new_position = user.position + Dir2(user.direction).to_tile_vector()
                    # collision check
                    if self.server.current_map.tiles is not None:
                        if new_position.y < 0 or new_position.x < 0 \
                                or new_position.y >= len(self.server.current_map.tiles) \
                                or new_position.x >= len(self.server.current_map.tiles[0]):
                            continue
                        tile = Tile.from_name(self.server.current_map.tiles[int(new_position.y)][int(new_position.x)])
                        if tile.is_solid:
                            continue
                    user.position = new_position
                    move_packet = EntityMovePacket(user.uuid, (user.position.x, user.position.y))
                    self.server.send_packet_to_all(move_packet)

        # handle packets
        if isinstance(packet, ChangeInputPacket):
            user = next((client for client in self.server.clients if client.token == packet.token), None)
            user.direction = Dir2(packet.direction)
            if user.direction != Dir2.ZERO:
                user.last_direction = user.direction
            user.attacking = packet.attacking
            # update direction for other clients
            direction_packet = EntityDirectionPacket(user.uuid, user.direction.value)
            for client in self.server.clients:
                if client.addr != client_addr:
                    self.server.send_packet(direction_packet, client.addr)
