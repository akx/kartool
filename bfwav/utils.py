import struct
import wave


def write_16_bit_wav(filename, sample_rate, pcm_data):
    with wave.open(filename, 'w') as wf:
        wf.setframerate(sample_rate)
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2)  # 16-bit
        data = struct.pack('h' * len(pcm_data), *pcm_data)
        wf.writeframes(data)
        wf.close()
