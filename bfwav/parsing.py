import struct

from bfwav.excs import MultiChannelFile
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
    ref_table = list(parse_ref_table(fp))
    channel_infos = []
    for flag, offset in ref_table:
        if flag == 0x7100:
            fp.seek(ref_table_start + offset)
            channel_info = dict(CHANNEL_INFO.parse_stream(fp))
            fp.seek(ref_table_start + channel_info['adpcm_info_offset'])
            adpcm_info = dict(ADPCM_INFO.parse_stream(fp))
            channel_info['adpcm_info'] = adpcm_info
            channel_infos.append(channel_info)
        else:
            raise NotImplementedError('...')

    return {
        'sample_info': sample_info,
        'channel_infos': channel_infos,
    }


def decode_data(fp, info):
    """
    Decode a parsed BFWAV into PCM data.

    :param fp: file pointer
    :param info: info dict
    :return: list of PCM data streams
    """
    assert fp.read(4) == b'DATA'
    data_length = readu32(fp)
    n_channels = len(info['channel_infos'])
    assert data_length % n_channels == 0
    sound_data = fp.read(data_length)
    n_samples = info['sample_info']['loop_end'] - info['sample_info']['loop_start']
    assert info['sample_info']['encoding'] == 2  # "DSP ADPCM"
    pcm_datas = []
    for i, channel in enumerate(info['channel_infos']):
        channel_sound_data = sound_data[i::n_channels]  # De-interleave
        adpcm_info = channel['adpcm_info']
        print(i, n_channels, adpcm_info, len(channel_sound_data))
        pcm_data = decode_adpcm(
            channel_sound_data,
            initial_hist1=adpcm_info['yn1'],
            initial_hist2=adpcm_info['yn2'],
            num_samples=n_samples,
            coefs=list(adpcm_info['coefficients']),
        )
        pcm_datas.append(pcm_data)
    return pcm_datas


class ParsedBFWAV:
    def __init__(self, header, info, pcm_datas):
        self.header = header
        self.info = info
        self.pcm_datas = pcm_datas

    @property
    def n_channels(self):
        return len(self.info['channel_infos'])

    @property
    def sample_rate(self):
        return int(self.info['sample_info']['sample_rate'])


def read_bfwav(fp):
    header = read_bfwav_header(fp)
    sec_infos = {si['flag']: (si['offset'], si['size']) for si in header['sections']}
    info_start, info_length = sec_infos[0x7000]
    fp.seek(info_start)
    info = parse_info_section(fp)
    data_start, data_length = sec_infos[0x7001]
    fp.seek(data_start)
    pcm_datas = decode_data(fp, info)
    return ParsedBFWAV(header=header, info=info, pcm_datas=pcm_datas)
