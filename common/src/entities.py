from enum import Enum


class EntityType(Enum):
    """Represents a type of entity and the sprite used."""

    # FRIENDLY
    KNIGHT = "knight_m"  # player
    HEART = "heart"  # floating heart that heals players
    # HOSTILE
    GOBLIN = "goblin"
    SKELETON = "skelet"
