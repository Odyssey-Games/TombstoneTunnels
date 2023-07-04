"""
File for managing common networking stuff such as serialization and deserialization of packets.
"""
import json
from json import JSONDecodeError

import pygame

from common.src.packets import *


def serialize(packet: Packet) -> bytes:
    """
    Serialize a packet to json bytes.
    :param packet: the packet instance to serialize
    :return: the serialized packet as json bytes
    """
    packet_type = packet.__class__.__name__
    # add type to dict
    packet.__dict__["type"] = packet_type

    # custom serialization
    for key, value in packet.__dict__.items():
        if isinstance(value, pygame.Vector2):
            packet.__dict__[key] = (value.x, value.y)

    return json.dumps(packet.__dict__).encode()


def deserialize(data: str | bytes) -> Packet | None:
    """
    Try to deserialize a packet from a json string. If the packet could not be deserialized, None is returned.

    :param data: the json string or json bytes to deserialize
    :return: the deserialized packet or None if it could not be deserialized
    """
    try:
        packet_dict = json.loads(data)
        # get type from dict
        packet_type = packet_dict["type"]
        clazz = [clazz for name, clazz in packet_classes if name == packet_type][0]
        del packet_dict["type"]  # remove type from dict; type was included upon serialization
        # handle token; if the packet is an instance of AuthorizedPacket, it must have a token
        token = None
        if issubclass(clazz, AuthorizedPacket):
            token = packet_dict["token"]
            del packet_dict["token"]

        # custom deserialization
        for key, value in packet_dict.items():
            if _is_valid_position(value):
                packet_dict[key] = pygame.Vector2(value[0], value[1])

        # noinspection PyArgumentList
        instance = clazz(**packet_dict)
        if token:
            instance.token = token
        return instance
    except (JSONDecodeError, KeyError, IndexError) as e:
        print(f"Could not deserialize packet:", e)


def _is_valid_position(pos):
    """
    Helper function to check if the given object is a valid position (tuple/list of two numbers).
    """
    return isinstance(pos, list) \
        and len(pos) == 2 \
        and isinstance(pos[0], (float, int)) \
        and isinstance(pos[1], (float, int))
