from construct import *

FSAR_SECTION_INFO = Struct(
    'id' / Int16ub,
    'padding' / Int16ub,
    'offset' / Int32ub,
    'size' / Int32ub,
)

FSAR_HEADER = Struct(
    'magic' / Const(b'FSAR'),
    'endianness' / Const(b'\xFE\xFF'),
    'header_size' / Const(Int16ub, 0x0040),
    'version' / Int32ub,
    'size' / Int32ub,
    'section_count' / Const(Int16ub, 3),
    'unknown' / Int16ub,
    'section_infos' / Array(3, FSAR_SECTION_INFO),
    'padding2' / Const(b'\00' * 8),
)

STRG_HEADER = Struct(
    'magic' / Const(b'STRG'),
    'size' / Int32ub,
    'unk1' / Const(Int32ub, 0x24000000),
    'string_table_offset' / Int32ub,
    'unk2' / Const(Int32ub, 0x24010000),
    'lookup_table_offset' / Int32ub,
)

STRING_TABLE_HEADER = Struct(
    'count' / Int32ub,
)

STRING_TABLE_ENTRY = Struct(
    'magic' / Const(Int32ub, 0x1F010000),
    'offset' / Int32ub,
    'size' / Int32ub,
)

LOOKUP_TABLE_HEADER = Struct(
    'start_index' / Int32ub,
    'index2' / Int32ub,
    'count' / Int32ub,
)

LOOKUP_TABLE_ENTRY = Struct(
    'endpoint' / Int16ub,
    'string_bit' / Int16ub,
    'index1' / Int32ub,
    'index2' / Int32ub,
    'string_table_index' / Int32ub,
    'data' / Int8ub,
    'file_id' / Array(3, Int8ub),
)

FILE_HEADER = Struct(
    'magic' / Const(b'FILE'),
    'size' / Int32ub,
)

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

info_kinds = {
    0x2100: 'audio',
    0x2101: 'bank',
    0x2102: 'player',
    0x2103: 'warc',
    0x2104: 'seq',
    0x2105: 'group',
    0x2106: 'file',
    0x220B: 'eoft',
}


def parse_strg_section(fp, strg_offset):
    fp.seek(strg_offset)
    strg_header = STRG_HEADER.parse_stream(fp)
    string_table_offset = strg_offset + 8 + strg_header.string_table_offset
    fp.seek(string_table_offset)
    string_count = STRING_TABLE_HEADER.parse_stream(fp).count
    string_table_entries = [STRING_TABLE_ENTRY.parse_stream(fp) for i in range(string_count)]
    string_entries = []
    for se in string_table_entries:
        fp.seek(string_table_offset + se.offset)
        data = fp.read(se.size)
        string_entries.append(dict(se, data=data))

    # fp.seek(offset + 8 + strg_header.lookup_table_offset)
    # lookup_header = LOOKUP_TABLE_HEADER.parse_stream(fp)
    # print(lookup_header)
    # lookup_table_entries = [LOOKUP_TABLE_ENTRY.parse_stream(fp) for i in range(lookup_header.count)]
    return string_entries


def parse_file_section(fp, file_sec_offset, file_infos):
    fp.seek(file_sec_offset)
    file_header = FILE_HEADER.parse_stream(fp)
    for file_info in file_infos:
        if file_info['external']:
            continue
        fp.seek(file_sec_offset + 8 + file_info['offset'])
        type_header = fp.read(4)
        print(file_info, type_header)


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
            if fte.offset == 0xFFFFFFFF:
                continue
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


def parse_warcs(fp, warc_table_offset):
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
    table_offsets = {info_kinds.get(io.id, io.id): io.offset for io in info_header.offsets}
    file_infos = list(parse_file_infos(fp, info_offset + 8 + table_offsets['file']))
    warcs = list(parse_warcs(fp, info_offset + 8 + table_offsets['warc']))
    for warc in warcs:

        file = file_infos[warc['file_id']]


    return {
        'header': info_header,
        'table_offsets': table_offsets,
        'file_infos': file_infos,
    }


def get_fsar_file_entries(fp):
    header = dict(FSAR_HEADER.parse_stream(fp))
    sections = {si['id']: si for si in header['section_infos']}
    strings = parse_strg_section(fp, sections[0x2000]['offset'])
    info_sec = parse_info_section(fp, sections[0x2001]['offset'])
    file_section = parse_file_section(fp, sections[0x2002]['offset'], file_infos=info_sec['file_infos'])
    return []
