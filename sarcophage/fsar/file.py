from construct import Const, Int32ub, Struct

FILE_HEADER = Struct(
    'magic' / Const(b'FILE'),
    'size' / Int32ub,
)


def parse_file_section(fp, file_sec_offset, file_infos):
    fp.seek(file_sec_offset)
    file_header = FILE_HEADER.parse_stream(fp)
    for file_info in file_infos:
        if file_info['external']:
            continue
        if file_info['offset'] == 0xFFFFFFFF:
            continue
        fp.seek(file_sec_offset + 8 + file_info['offset'])
        type_header = fp.read(4)
        print(file_info, type_header)
