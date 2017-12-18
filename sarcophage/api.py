import io

from sarcophage.fsar import get_fsar_file_entries
from sarcophage.sarc import get_sarc_file_entries
from sarcophage.yaz0 import decompress_yaz0


def get_file_entries(fp):
    magic = fp.read(4)

    if magic == b"Yaz0":
        fp.seek(0)
        data = fp.read()
        fp.close()
        fp = io.BytesIO(decompress_yaz0(data))

    fp.seek(0)

    if magic == b"FSAR":
        yield from get_fsar_file_entries(fp)
    elif magic == b"SARC":
        yield from get_sarc_file_entries(fp.read())
    else:
        raise NotImplementedError('Unrecognized magic %s' % magic)
