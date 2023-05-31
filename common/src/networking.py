"""
File for managing common networking stuff such as serialization and deserialization of packets.
"""
import json
from json import JSONDecodeError

from common.src.packets import *


def serialize(packet: Packet) -> bytes:
    packet_type = packet.__class__.__name__
    # add type to dict
    packet.__dict__["type"] = packet_type
    return json.dumps(packet.__dict__).encode()


def deserialize(data: str | bytes) -> Packet | None:
    """
    Try to deserialize a packet from a json string. If the packet could not be deserialized, None is returned.

    :param data: the json string to deserialize
    :return: the deserialized packet or None if it could not be deserialized
    """
    try:
        packet_dict = json.loads(data)
        # get type from dict
        packet_type = packet_dict["type"]
        clazz = [clazz for name, clazz in packet_classes if name == packet_type][0]
        del packet_dict["type"]
        # handle token
        token = None
        if issubclass(clazz, AuthorizedPacket):
            token = packet_dict["token"]
            del packet_dict["token"]
        instance = clazz(**packet_dict)
        if token:
            instance.token = token
        return instance
    except (JSONDecodeError, KeyError, IndexError) as e:
        print(f"Could not deserialize packet:", e)
