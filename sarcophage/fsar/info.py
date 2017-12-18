from construct import Int16ub, Int32ub, Struct, Array, Const

INFO_TABLE_KINDS = {
    0x2100: 'audio',
    0x2101: 'bank',
    0x2102: 'player',
    0x2103: 'warc',
    0x2104: 'seq',
    0x2105: 'group',
    0x2106: 'file',
    0x220B: 'eoft',
}

INFO_OFFSET = Struct(
    'id' / Int16ub,
    'unk' / Int16ub,
    'offset' / Int32ub,
)

INFO_HEADER = Struct(
    'magic' / Const(b'INFO'),
    'size' / Int32ub,
    'offsets' / Array(8, INFO_OFFSET),
)

FILE_TABLE_HEADER = Struct(
    'count' / Int32ub,
)

FILE_TABLE_ENTRY = Struct(
    'id' / Int16ub,
    'unk' / Int16ub,
    'offset' / Int32ub,
)

FILE_TABLE_INTERNAL_ENTRY = Struct(
    'unk1' / Int16ub,
    'unk2' / Int16ub,
    'offset' / Int32ub,
    'size' / Int32ub,
)

WARC_HEADER_ENTRY = Struct(
    'magic' / Const(Int16ub, 0x2207),
    'unk' / Int16ub,
    'offset' / Int32ub,
)

WARC_ENTRY = Struct(
    'file_id' / Int32ub,
    'unk1' / Int32ub,
    'unk2' / Int32ub,
    'name_string_id' / Int32ub,
)


def parse_file_infos(fp, file_table_offset):
    fp.seek(file_table_offset)
    file_table_header = FILE_TABLE_HEADER.parse_stream(fp)
    file_info_offsets = [
        fte.offset
        for fte
        in (FILE_TABLE_ENTRY.parse_stream(fp) for i in range(file_table_header.count))
        if fte.id == 0x220A
    ]
    for info_offset in file_info_offsets:
        fp.seek(file_table_offset + info_offset)
        header = Int16ub.parse_stream(fp)
        fp.seek(file_table_offset + info_offset + 0xC)
        if header == 0x220C:  # Internal file (in this FSAR)
            fte = FILE_TABLE_INTERNAL_ENTRY.parse_stream(fp)
            yield dict(dict(fte), external=False, info_offset=info_offset)
        elif header == 0x220D:  # File pointer (external file)
            chars = []
            while True:
                ch = fp.read(1)
                if ch == b'\x00':
                    break
                chars.append(ch)
            yield {
                'info_offset': info_offset,
                'external': True,
                'path': b''.join(chars).decode(),
            }
        else:
            raise NotImplementedError('Not sure what is fileinfo with header %x' % header)


def parse_warc_table(fp, warc_table_offset):
    fp.seek(warc_table_offset)
    warc_count = Int32ub.parse_stream(fp)
    warc_offsets = [
        whe.offset
        for whe in [WARC_HEADER_ENTRY.parse_stream(fp) for i in range(warc_count)]
    ]

    for offset in warc_offsets:
        fp.seek(warc_table_offset + offset)
        yield dict(WARC_ENTRY.parse_stream(fp))


def parse_info_section(fp, info_offset):
    fp.seek(info_offset)
    info_header = INFO_HEADER.parse_stream(fp)
    table_offsets = {INFO_TABLE_KINDS.get(io.id, io.id): io.offset for io in info_header.offsets}
    file_infos = list(parse_file_infos(fp, info_offset + 8 + table_offsets['file']))
    warcs = list(parse_warc_table(fp, info_offset + 8 + table_offsets['warc']))
    return {
        'header': info_header,
        'table_offsets': table_offsets,
        'file_infos': file_infos,
        'warcs': warcs,
    }
