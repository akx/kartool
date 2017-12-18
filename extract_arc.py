import argparse
import os

from sarcophage.sarc import get_sarc_file_entries
from sarcophage.yaz0 import decompress_yaz0


def main():
    ap = argparse.ArgumentParser(prog='extract_arc')
    ap.add_argument('--directory', '-d', default=None)
    ap.add_argument('file')
    args = ap.parse_args()

    if not args.directory:
        args.directory = os.path.splitext(args.file)[0]

    with open(args.file, 'rb') as f:
        data = f.read()

    magic = data[0:4]
    if magic == b"Yaz0":
        data = decompress_yaz0(data)
    magic = data[0:4]
    if magic == b"SARC":
        file_entries = get_sarc_file_entries(data)
    else:
        raise NotImplementedError('Unrecognized magic %s' % magic)
    for fent in file_entries:
        dest_name = os.path.join(args.directory, fent.name)
        dest_dir = os.path.dirname(dest_name)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        with open(dest_name, 'wb') as outf:
            outf.write(fent.data)
            print(dest_name)


if __name__ == "__main__":
    main()
