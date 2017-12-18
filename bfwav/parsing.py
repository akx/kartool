import struct

from .structs import HEADER, HEADER_BLK, SAMPLE_INFO, CHANNEL_INFO, ADPCM_INFO
from .dsp_adpcm import decode_adpcm


def readu16(fp):
    return struct.unpack('>H', fp.read(2))[0]


def readu32(fp):
    return struct.unpack('>I', fp.read(4))[0]


def read_bfwav_header(fp):
    header = dict(HEADER.parse_stream(fp))
    assert header['bom'] == 0xFEFF
    sections = [dict(HEADER_BLK.parse_stream(fp)) for sec in range(header['n_sections'])]
    return {
        'header': header,
        'sections': sections,
    }


def parse_ref_table(fp):
    num_refs = readu32(fp)
    for ref in range(num_refs):
        flag = readu16(fp)
        readu16(fp)  # Padding
        offset = readu32(fp)
        yield (flag, offset)


def parse_info_section(fp):
    sample_info = dict(SAMPLE_INFO.parse_stream(fp))
    ref_table_start = fp.tell()
    ref_table_list = list(parse_ref_table(fp))
    ref_table = dict(ref_table_list)
    assert len(ref_table_list) == len(ref_table)  # No duplicates that are hidden, right?
    channel_infos_offset = ref_table[0x7100]
    fp.seek(ref_table_start + channel_infos_offset)
    channel_info = dict(CHANNEL_INFO.parse_stream(fp))
    fp.seek(ref_table_start + channel_info['adpcm_info_offset'])
    adpcm_info = dict(ADPCM_INFO.parse_stream(fp))
    return {
        'sample_info': sample_info,
        'channel_info': channel_info,
        'adpcm_info': adpcm_info,
    }


def decode_data(fp, info):
    assert fp.read(4) == b'DATA'
    data_length = readu32(fp)
    sound_data = fp.read(data_length)
    n_samples = info['sample_info']['loop_end'] - info['sample_info']['loop_start']
    assert info['sample_info']['encoding'] == 2  # "DSP ADPCM"
    adpcm_info = info['adpcm_info']
    pcm_data = decode_adpcm(
        sound_data,
        initial_hist1=adpcm_info['yn1'],
        initial_hist2=adpcm_info['yn2'],
        num_samples=n_samples,
        coefs=list(adpcm_info['coefficients']),
    )
    return pcm_data


def read_bfwav(fp):
    header = read_bfwav_header(fp)
    sec_infos = {si['flag']: (si['offset'], si['size']) for si in header['sections']}
    info_start, info_length = sec_infos[0x7000]
    fp.seek(info_start)
    info = parse_info_section(fp)
    data_start, data_length = sec_infos[0x7001]
    fp.seek(data_start)
    pcm_data = decode_data(fp, info)
    return {
        'header': header,
        'info': info,
        'data': pcm_data,
    }
