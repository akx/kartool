import struct
from pprint import pprint
import wave

from construct import *

from dsp_adpcm import decode_adpcm

INFO_SECTION = Struct(
    'signature' / Const(b'INFO'),
    'size' / Int32ub,
    'encoding' / Int8ub,
    'loop' / Int8ub,
    'padding' / Int16ub,
    'sample_rate' / Int32ub,
    'loop_start' / Int32ub,
    'loop_end' / Int32ub,
    'loop_start_orig' / Int32ub,
)

CHANNEL_INFO = Struct(
    'signature' / Const(b'\x1F\x00'),
    'padding1' / Int16ub,
    'sound_data_offset' / Int32ub,
    'adpcm_info_flag' / Const(b'\x03\x00'),
    'padding2' / Int16ub,
    'adpcm_info_offset' / Int32ub,
    'reserved' / Int32ub,
)

ADPCM_INFO = Struct(
    'reserved' / Array(12, Int8ub),
    'coefficients' / Array(16, Int16sb),
    'pred_scale' / Int16ub,
    'yn1' / Int16ub,
    'yn2' / Int16ub,
    'loop_pred_scale' / Int16ub,
    'loop_yn1' / Int16ub,
    'loop_yn2' / Int16ub,
)


def readu16(fp):
    return struct.unpack('>H', fp.read(2))[0]


def readu32(fp):
    return struct.unpack('>I', fp.read(4))[0]


def read_bfwav_header(fp):
    s0 = fp.tell()
    header = fp.read(4)
    assert header == b'FWAV'
    assert fp.read(2) == b'\xFE\xFF'
    assert readu16(fp) == 0x40
    version = readu32(fp)
    file_size = readu32(fp)
    n_sections = readu16(fp)
    readu16(fp)  # padding
    for sec in range(n_sections):
        sec_flag = readu16(fp)
        readu16(fp)  # padding
        sec_offset = readu32(fp)
        sec_size = readu32(fp)
        yield (sec_flag, (sec_offset, sec_size))
    fp.read(20)


def parse_ref_table(fp):
    num_refs = readu32(fp)
    for ref in range(num_refs):
        flag = readu16(fp)
        readu16(fp)  # Padding
        offset = readu32(fp)
        yield (flag, offset)


def parse_info_section(fp):
    header = dict(INFO_SECTION.parse_stream(fp))
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
        'header': header,
        'channel_info': channel_info,
        'adpcm_info': adpcm_info,
    }


def convert(fp):
    sec_infos = dict(read_bfwav_header(fp))
    info_start, info_length = sec_infos[0x7000]
    fp.seek(info_start)
    info = parse_info_section(fp)
    data_start, data_length = sec_infos[0x7001]
    fp.seek(data_start)
    pcm_data = decode_data(fp, info)
    return {
        'info': info,
        'data': pcm_data,
    }



def decode_data(fp, info):
    assert fp.read(4) == b'DATA'
    data_length = readu32(fp)
    sound_data = fp.read(data_length)
    print(len(sound_data), data_length)
    pprint(info)
    n_samples = info['header']['loop_end'] - info['header']['loop_start']
    assert info['header']['encoding'] == 2  # "DSP ADPCM"
    adpcm_info = info['adpcm_info']
    pcm_data = decode_adpcm(
        sound_data,
        initial_hist1=adpcm_info['yn1'],
        initial_hist2=adpcm_info['yn2'],
        num_samples=n_samples,
        coefs=list(adpcm_info['coefficients']),
    )
    return pcm_data


def write_16_bit_wav(filename, sample_rate, pcm_data):
    with wave.open(filename, 'w') as wf:
        wf.setframerate(sample_rate)
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2)  # 16-bit
        data = struct.pack('h' * len(pcm_data), *pcm_data)
        wf.writeframes(data)
        wf.close()


if __name__ == '__main__':
    with open('./CPC-RG-BAD_05_TS0.85_amb.ny.32.dspadpcm.bfwav', 'rb') as infp:
        convert(infp)
