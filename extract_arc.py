import argparse
import os

from sarcophage.api import get_file_entries


def main():
    ap = argparse.ArgumentParser(prog='extract_arc')
    ap.add_argument('--directory', '-d', default=None)
    ap.add_argument('--dry-run', '-n', default=False, action='store_true')
    ap.add_argument('file')
    args = ap.parse_args()

    if not args.directory:
        args.directory = os.path.splitext(args.file)[0]

    fp = open(args.file, 'rb')
    file_entries = get_file_entries(fp)
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
