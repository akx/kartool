from construct import Struct, Int32ub, Int16ub, Array, Int8ub

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
FILE_TABLE_INTERNAL_HEADER = Struct(
    'type' / Int16ub,  # 2
    'unk' / Array(10, Int8ub),  # 10
)


class FileTableEntry:
    def __init__(self, *, external_path=None, offset=0, size=0, fte=None, ftih=None):
        self.external_path = external_path
        self.offset = offset
        self.size = size
        self.fte = fte
        self.ftih = ftih

    @property
    def external(self):
        return bool(self.external_path)

    @property
    def valid(self):
        return self.external or (self.offset != 0xFFFFFFFF and self.size > 0)


def convert_internal_file_table_entry(file_table_entry, fp, file_table_offset):
    if file_table_entry.id != 0x220A:  # Does file exist?
        return FileTableEntry(fte=file_table_entry)
    info_offset = file_table_entry.offset
    fp.seek(file_table_offset + info_offset)
    internal_header = FILE_TABLE_INTERNAL_HEADER.parse_stream(fp)
    if internal_header.type == 0x220C:  # Internal file (in this FSAR)
        file_table_entry = FILE_TABLE_INTERNAL_ENTRY.parse_stream(fp)
        return FileTableEntry(
            offset=file_table_entry.offset,
            size=file_table_entry.size,
            fte=file_table_entry,
            ftih=internal_header,
        )
    elif internal_header.type == 0x220D:  # File pointer (external file)
        chars = []
        while True:
            ch = fp.read(1)
            if ch == b'\x00':
                break
            chars.append(ch)
        return FileTableEntry(
            external_path=b''.join(chars).decode(),
            fte=file_table_entry,
            ftih=internal_header,
        )
    raise NotImplementedError('Not sure what is fileinfo with header %x' % internal_header.type)


def parse_file_table(fp, file_table_offset):
    fp.seek(file_table_offset)
    file_table_header = FILE_TABLE_HEADER.parse_stream(fp)
    file_table_entries = [FILE_TABLE_ENTRY.parse_stream(fp) for i in range(file_table_header.count)]
    return [convert_internal_file_table_entry(fte, fp, file_table_offset) for fte in file_table_entries]
