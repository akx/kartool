# Based on code by NWPlayer123: "no rights reserved, feel free to do whatever"
import struct


def hexstr(data, length):  # Convert input into hex string
    return hex(data).lstrip("0x").rstrip("L").zfill(length).upper()


def binr(byte):
    return bin(byte).lstrip("0b").zfill(8)


def uint8(data, pos):
    return struct.unpack(">B", data[pos:pos + 1])[0]


def uint16(data, pos):
    return struct.unpack(">H", data[pos:pos + 2])[0]


def uint24(data, pos):
    return struct.unpack(">I", "\00" + data[pos:pos + 3])[0]  # HAX


def uint32(data, pos):
    return struct.unpack(">I", data[pos:pos + 4])[0]


def getstr(data):
    x = data.find(b"\x00")
    if x != -1:
        return data[:x]
    else:
        return data


def intify(out, data, length=0):
    if type(data) == str:
        for x in range(len(data)):
            out.append(ord(data[x]))
    if type(data) == int:
        data = hexstr(data, length * 2)
        for x in range(length):
            out.append(int(data[x * 2:(x * 2) + 2], 16))
    return out
