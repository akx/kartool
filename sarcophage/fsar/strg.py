from construct import Int16ub, Int32ub, Struct, Array, Const, Int8ub

STRG_HEADER = Struct(
    'magic' / Const(b'STRG'),
    'size' / Int32ub,
    'unk1' / Const(0x24000000, Int32ub),
    'string_table_offset' / Int32ub,
    'unk2' / Const(0x24010000, Int32ub),
    'lookup_table_offset' / Int32ub,
)

STRING_TABLE_HEADER = Struct(
    'count' / Int32ub,
)

STRING_TABLE_ENTRY = Struct(
    'magic' / Const(0x1F010000, Int32ub),
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
