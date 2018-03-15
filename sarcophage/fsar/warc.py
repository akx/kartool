from construct import Int16ub, Int32ub, Struct, Const

WARC_SECTION_ENTRY = Struct(
    'header' / Int16ub,
    'unk' / Int16ub,
    'offset' / Int32ub,
    'size' / Int32ub,
)

WARC_WAVE_ENTRY = Struct(
    'header' / Int16ub,
    'unk' / Int16ub,
    'offset' / Int32ub,
    'size' / Int32ub,
)

WARC_HEADER_ENTRY = Struct(
    'magic' / Const(0x2207, Int16ub),
    'unk' / Int16ub,
    'offset' / Int32ub,
)

WARC_ENTRY = Struct(
    'file_id' / Int32ub,
    'unk1' / Int32ub,
    'unk2' / Int32ub,
    'name_string_id' / Int32ub,
)


def extract_warc(fp, file_sec_offset, file_table_entry):
    """
    Extract binary blobs (wavs) from a warc
    :type file_table_entry: sarcophage.info.FileTableEntry
    """
    file_offset = file_sec_offset + 8 + file_table_entry.offset
    fp.seek(file_offset + 0x10)
    section_count = Int16ub.parse_stream(fp)
    fp.read(2)
    sections = {se.header: se for se in [WARC_SECTION_ENTRY.parse_stream(fp) for x in range(section_count)]}
    info_offset = sections[0x6800].offset
    data_offset = sections[0x6801].offset
    fp.seek(file_offset + info_offset + 8)
    wav_count = Int32ub.parse_stream(fp)
    wavs = []
    for i in range(wav_count):
        fp.seek(file_offset + info_offset + 12 + i * 12)
        wavs.append(WARC_WAVE_ENTRY.parse_stream(fp))
    for wav in wavs:
        if wav.size > 0:
            fp.seek(file_offset + data_offset + 8 + wav.offset)
            yield fp.read(wav.size)


def parse_warc_table(fp, warc_table_offset):
    fp.seek(warc_table_offset)
    warc_count = Int32ub.parse_stream(fp)
    # Parse these sequentially, before the seek-a-thon
    warc_headers = [WARC_HEADER_ENTRY.parse_stream(fp) for i in range(warc_count)]
    warc_entries = []

    for i, header in enumerate(warc_headers):
        fp.seek(warc_table_offset + header.offset)
        warc_entry = WARC_ENTRY.parse_stream(fp)
        warc_entry.header = header
        warc_entries.append(warc_entry)
    return warc_entries
