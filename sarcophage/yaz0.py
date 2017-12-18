# Based on code by NWPlayer123: "no rights reserved, feel free to do whatever"
from .utils import uint32, uint16, uint8


def decompress_yaz0(data):
    '''Thanks to thakis for yaz0dec, which I modeled this on after
    I cleaned it up in v0.2, what with bit-manipulation and looping
    Thanks to Kinnay for suggestions to make this even faster'''
    pos = 16
    size = uint32(data, 4)  # Uncompressed filesize
    out = []
    bits = 0
    while len(out) < size:  # Read Entire File
        if bits == 0:
            code = uint8(data, pos)
            pos += 1
            bits = 8

        if (code & 0x80) != 0:  # Copy 1 Byte
            out.append(data[pos])
            pos += 1
        else:
            rle = uint16(data, pos)
            pos += 2
            dist = rle & 0xFFF
            dstpos = len(out) - (dist + 1)
            read = (rle >> 12)
            if (rle >> 12) == 0:
                read = ord(data[pos]) + 0x12
                pos += 1
            else:
                read += 2
            for x in range(read):
                out.append(out[dstpos + x])
        code <<= 1
        bits -= 1
    out = "".join(out)
    return out
