import time


class Lock:
    def __init__(self):
        self.locked = False

    def __enter__(self):
        while self.locked:
            time.sleep(0.01)
        self.locked = True

    def __exit__(self, *args):
        self.locked = False


def twosComplement(value, length):
    """Compute the 2's complement of int value

    Given an unsigned integer return signed value.

    Would be better to do this with [from/to]_bytes but
    the "signed" arg is not implemented in circuitpython ¯\_(ツ)_/¯

    :param value: Unsigned integer
    :type value: int
    :param length: Length of unsigned integer in bytes
    :type length: int
    :returns: Signed integer
    :rtype: int
    """
    maxInt = int.from_bytes(bytes([0xFF] * length), "little")
    if value < 0:
        maxInt += value
        return list(maxInt.to_bytes(length, "little"))
    width = length * 8
    sign_bit = 1 << (width - 1)
    if value & sign_bit:
        value -= 1 << width
    return value
