import struct
import wave
from itertools import chain


def interleave(iters):
    return list(chain(*zip(*iters)))


def write_16_bit_wav(filename, sample_rate, pcm_datas):
    with wave.open(filename, 'w') as wf:
        wf.setframerate(sample_rate)
        wf.setnchannels(len(pcm_datas))
        wf.setsampwidth(2)  # 16-bit
        interleaved_pcm_data = interleave(pcm_datas)

        data = struct.pack('h' * len(interleaved_pcm_data), *interleaved_pcm_data)
        wf.writeframes(data)
        wf.close()
