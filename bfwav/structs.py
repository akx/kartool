from construct import Struct, Const, Int16ub, Int32ub, Int8ub, Array, Int16sb

HEADER = Struct(
    'signature' / Const(b'FWAV'),
    'bom' / Int16ub,
    'size' / Int16ub,
    'version' / Int32ub,
    'size' / Int32ub,
    'n_sections' / Const(Int16ub, 2),
    'padding' / Int16ub,
)

HEADER_BLK = Struct(
    'flag' / Int16ub,
    'padding' / Int16ub,
    'offset' / Int32ub,
    'size' / Int32ub,
)

SAMPLE_INFO = Struct(
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
