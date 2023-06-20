"""
Spawn/remove entities based on player count.
"""
import secrets
from random import randint
from time import time

from pygame import Vector2

from common.src.entities import EntityType
from common.src.map.tile import Tile
from common.src.packets import EntitySpawnPacket
from entities import ServerEntity
from mechanics import Mechanics


class EntityManager(Mechanics):
    def __init__(self, server):
        super().__init__(server)

    ENTITY_SPAWN_INTERVAL = 3  # spawn entities every 3 seconds
    last_spawn_time = time()

    def _get_random_spawn(self):
        return Vector2(randint(1, self.server.current_map.width - 1), randint(1, self.server.current_map.height - 1))

    def tick(self, _, __):
        # maybe spawn/remove entities
        if len(self.server.clients) == 0:
            # remove all entities when all players have left
            self.server.entities.clear()
        else:
            # difficulty scales with player count
            difficulty = len(self.server.clients)
            if time() - self.last_spawn_time >= self.ENTITY_SPAWN_INTERVAL:
                self.last_spawn_time = time()
                uuid = secrets.token_hex(16)
                random_spawn = self._get_random_spawn()
                is_near_player = True
                # Find a valid spawn position
                while Tile.from_coords(self.server, random_spawn).is_solid or is_near_player:
                    random_spawn = self._get_random_spawn()
                    is_near_player = False
                    for player in self.server.clients:
                        if (player.position - random_spawn).length_squared() <= 4:
                            is_near_player = True
                            break
                entity_type = EntityType.GOBLIN if randint(0, 1) == 1 else EntityType.SKELETON
                new_entity = ServerEntity(uuid, entity_type, random_spawn, difficulty * 10)
                self.server.entities.append(new_entity)
                spawn_packet = EntitySpawnPacket(uuid, new_entity.entity_type.value,
                                                 (new_entity.position.x, new_entity.position.y),
                                                 new_entity.health)
                print("Spawned entity: ", uuid, "with health", new_entity.health)
                self.server.send_packet_to_all(spawn_packet)
