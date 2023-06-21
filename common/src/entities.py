from enum import Enum


class EntityType(Enum):
    """Represents a type of entity and the sprite used."""

    # FRIENDLY
    KNIGHT = "knight_m"  # player
    # HOSTILE
    GOBLIN = "goblin"
    SKELETON = "skelet"
