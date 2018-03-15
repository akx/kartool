# http://www.metroid2002.com/retromodding/wiki/DSP_(File_Format)
import io

nibble_to_s8 = [0, 1, 2, 3, 4, 5, 6, 7, -8, -7, -6, -5, -4, -3, -2, -1]


def clamp(val):
    if val < -32768:
        return -32768
    if val > 32767:
        return 32767
    return val


def decode_adpcm(src_data, initial_hist1, initial_hist2, num_samples, coefs):
    hist1 = initial_hist1
    hist2 = initial_hist2
    samples = []
    data_sio = io.BytesIO(src_data)
    read_byte = lambda: data_sio.read(1)[0]
    BYTES_PER_FRAME = tuple(range(7))

    while len(samples) < num_samples:
        # Each frame, we need to read the header byte and use it to set the scale and coefficient values:
        header = read_byte()
        scale = 1 << (header & 0xF)
        coef_index = (header >> 4) & 0xF
        coef1 = coefs[coef_index * 2 + 0]
        coef2 = coefs[coef_index * 2 + 1]

        for b in BYTES_PER_FRAME:  # 7 bytes per frame
            byte = read_byte()
            for adpcm_nibble in (nibble_to_s8[(byte >> 4) & 0xF], nibble_to_s8[byte & 0xF]):  # 2 samples per byte
                sample = clamp(((adpcm_nibble * scale) << 11) + 1024 + ((coef1 * hist1) + (coef2 * hist2)) >> 11)
                hist2 = hist1
                hist1 = sample
                samples.append(sample)
    return samples[:num_samples]
