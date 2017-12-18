# Based on code by NWPlayer123: "no rights reserved, feel free to do whatever"
from sarcophage.file_entry import FileEntry
from .utils import getstr, uint16, uint32


def get_sarc_file_entries(data):
    pos = 6
    order = uint16(data, pos)
    pos += 6  # Byte Order Mark
    if order != 65279:  # 0xFEFF - Big Endian
        raise NotImplementedError("Little endian not supported!")
    doff = uint32(data, pos)
    pos += 8  # Start of data section
    # ---------------------------------------------------------------
    magic2 = data[pos:pos + 4]
    pos += 6
    assert magic2 == b"SFAT"
    nodec = uint16(data, pos)
    pos += 6  # Node Count
    nodes = []
    for x in range(nodec):
        pos += 8
        srt = uint32(data, pos)
        pos += 4  # File Offset Start
        end = uint32(data, pos)
        pos += 4  # File Offset End
        nodes.append([srt, end])
    # ---------------------------------------------------------------
    magic3 = data[pos:pos + 4]
    pos += 8
    assert magic3 == b"SFNT"
    file_names = []
    if getstr(data[pos:]) == "":
        for x in range(nodec):
            file_names.append("bfbin%d.bfbin" % x)
    else:
        for x in range(nodec):
            string = getstr(data[pos:])
            pos += len(string)
            while data[pos] == 0:
                pos += 1  # Move to the next string
            file_names.append(string)
    # ---------------------------------------------------------------
    for x in range(nodec):
        yield FileEntry(
            name=file_names[x].decode(),
            data=(data[doff + nodes[x][0]:doff + nodes[x][1]]),
        )
