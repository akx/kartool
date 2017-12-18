from construct import Array, Const, Int16ub, Int32ub, Struct

from .structs import FSAR_HEADER

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

FILE_HEADER = Struct(
    'magic' / Const(b'FILE'),
    'size' / Int32ub,
)


def parse_fsar_header(fp):
    return dict(FSAR_HEADER.parse_stream(fp))
