from construct import Int16ub, Int32ub, Struct

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


def extract_warc(fp, file_sec_offset, file_info):
    """
    Extract binary blobs (wavs) from a warc
    """
    file_offset = file_sec_offset + 8 + file_info['offset']
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
