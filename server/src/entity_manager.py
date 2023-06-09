"""
Spawn/remove entities based on player count.
"""
import secrets
from random import randint
from time import time

from pygame import Vector2

from common.src.entities import EntityType
from common.src.map.tile import Tile
from common.src.packets import EntitySpawnPacket, EntityHealthPacket, EntityMovePacket
from entities import ServerEntity
from mechanics import Mechanics


class EntityManager(Mechanics):
    """
    Handles spawning/removing entities and their movement/attacking logic.
    """
    def __init__(self, server):
        super().__init__(server)
        self.last_spawn_time = time()
        self.last_heart_spawn_time = time()
        self.last_move_time = time()

    ENTITY_SPAWN_INTERVAL = 3  # spawn entities every 3 seconds
    HEART_SPAWN_INTERVAL = 15  # spawn hearts every 15 seconds
    ENTITY_MOVE_INTERVAL = 1.5  # move entities every 1 second

    def _get_random_spawn(self):
        return Vector2(randint(1, self.server.current_map.width - 1), randint(1, self.server.current_map.height - 1))

    def _get_random_entity_spawn(self):
        random_spawn = self._get_random_spawn()
        is_near_player = True
        # Find a valid spawn position that is not near a player
        while Tile.from_coords(self.server, random_spawn).is_solid or is_near_player:
            random_spawn = self._get_random_spawn()
            is_near_player = False
            for player in self.server.clients:
                if (player.position - random_spawn).length_squared() <= 4:
                    is_near_player = True
                    break
        return random_spawn

    @staticmethod
    def get_sign(value):
        """
        :return: 0 for 0, 1 for positive values, -1 for negative values
        """
        if value > 0:
            return 1
        elif value < 0:
            return -1
        else:
            return 0

    def tick(self, _, __):
        """
        Called every tick. Handles entity spawning/removing and movement.
        """
        # maybe spawn/remove entities
        if len(self.server.clients) == 0:
            # remove all entities when all players have left
            self.server.entities.clear()
        else:
            # maybe move entities
            if time() - self.last_move_time >= self.ENTITY_MOVE_INTERVAL:
                self.last_move_time = time()
                for entity in self.server.entities:
                    if entity.entity_type == EntityType.KNIGHT:
                        # don't move players
                        continue
                    if entity.entity_type == EntityType.HEART:
                        # don't move hearts
                        continue
                    # find nearest player
                    nearest_player = None
                    for player in self.server.clients:
                        if not nearest_player or (player.position - entity.position).length_squared() < (
                                nearest_player.position - entity.position).length_squared():
                            nearest_player = player
                    if nearest_player:
                        # move in direction of nearest player
                        direction = (nearest_player.position - entity.position)
                        direction = Vector2(self.get_sign(direction.x), self.get_sign(direction.y))
                        new_position = entity.position + direction
                        if not Tile.from_coords(self.server, new_position).is_solid:
                            entity.position = new_position
                            # send entity move packet to all clients
                            packet = EntityMovePacket(entity.uuid, entity.position)
                            self.server.send_packet_to_all(packet)
                            if nearest_player.position == new_position:
                                print("Entity hit player!")
                                nearest_player.health -= 10
                                packet = EntityHealthPacket(nearest_player.uuid, nearest_player.health)
                                self.server.send_packet_to_all(packet)
                                # death?
                                if nearest_player.health <= 0:
                                    # when the player dies, we reset their health and position
                                    print("Player died!")
                                    nearest_player.health = 50
                                    nearest_player.position = Vector2(1, 2)
                                    # send health and position packets to all clients
                                    packet = EntityHealthPacket(nearest_player.uuid, nearest_player.health)
                                    self.server.send_packet_to_all(packet)
                                    packet = EntityMovePacket(nearest_player.uuid, nearest_player.position)
                                    self.server.send_packet_to_all(packet)

            # difficulty scales with player count
            difficulty = len(self.server.clients)
            if time() - self.last_spawn_time >= self.ENTITY_SPAWN_INTERVAL:
                self.last_spawn_time = time()
                uuid = secrets.token_hex(16)
                random_spawn = self._get_random_entity_spawn()
                # Spawn a random hostile entity
                entity_type = EntityType.GOBLIN if randint(0, 1) == 1 else EntityType.SKELETON
                new_entity = ServerEntity(uuid, entity_type, random_spawn, 10 + difficulty * 10)
                self.server.entities.append(new_entity)
                # Send spawn packet to all clients
                spawn_packet = EntitySpawnPacket(uuid, new_entity.entity_type.value,
                                                 (new_entity.position.x, new_entity.position.y),
                                                 new_entity.health)
                print("Spawned entity: ", uuid, "with health", new_entity.health)
                self.server.send_packet_to_all(spawn_packet)

            if time() - self.last_heart_spawn_time >= self.HEART_SPAWN_INTERVAL:
                self.last_heart_spawn_time = time()
                uuid = secrets.token_hex(16)
                random_spawn = self._get_random_entity_spawn()
                # Spawn a floating heart
                new_entity = ServerEntity(uuid, EntityType.HEART, random_spawn, 10)
                self.server.entities.append(new_entity)
                # Send spawn packet to all clients
                spawn_packet = EntitySpawnPacket(uuid, new_entity.entity_type.value,
                                                 (new_entity.position.x, new_entity.position.y),
                                                 new_entity.health)
                print("Spawned heart entity: ", uuid, "with health", new_entity.health)
                self.server.send_packet_to_all(spawn_packet)

