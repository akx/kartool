import argparse
import os
import io

from sarcophage.fsar import get_fsar_file_entries
from sarcophage.sarc import get_sarc_file_entries
from sarcophage.yaz0 import decompress_yaz0


def main():
    ap = argparse.ArgumentParser(prog='extract_arc')
    ap.add_argument('--directory', '-d', default=None)
    ap.add_argument('--dry-run', '-n', default=False, action='store_true')
    ap.add_argument('file')
    args = ap.parse_args()

    if not args.directory:
        args.directory = os.path.splitext(args.file)[0]

    fp = open(args.file, 'rb')
    magic = fp.read(4)

    if magic == b"Yaz0":
        fp.seek(0)
        data = fp.read()
        fp.close()
        fp = io.BytesIO(decompress_yaz0(data))

    fp.seek(0)

    if magic == b"FSAR":
        file_entries = get_fsar_file_entries(fp)
    elif magic == b"SARC":
        file_entries = get_sarc_file_entries(fp.read())
    else:
        raise NotImplementedError('Unrecognized magic %s' % magic)

    for fent in file_entries:
        dest_name = os.path.join(args.directory, fent.name)
        dest_dir = os.path.dirname(dest_name)
        if args.dry_run:
            print(dest_name)
            continue
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        with open(dest_name, 'wb') as outf:
            outf.write(fent.data)
            print(dest_name)


if __name__ == "__main__":
    main()
