from construct import Int16ub, Int32ub, Struct, Array, Const

from sarcophage.fsar.file_table import parse_file_table
from sarcophage.fsar.warc import parse_warc_table

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


def parse_info_section(fp, info_offset):
    fp.seek(info_offset)
    info_header = INFO_HEADER.parse_stream(fp)
    table_offsets = {INFO_TABLE_KINDS.get(io.id, io.id): io.offset for io in info_header.offsets}
    file_infos = list(parse_file_table(fp, info_offset + 8 + table_offsets['file']))
    warcs = list(parse_warc_table(fp, info_offset + 8 + table_offsets['warc']))
    return {
        'header': info_header,
        'table_offsets': table_offsets,
        'file_infos': file_infos,
        'warcs': warcs,
    }
