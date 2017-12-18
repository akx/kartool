import argparse
import os
import io

from bfwav.excs import MultiChannelFile
from bfwav.parsing import read_bfwav
from bfwav.utils import write_16_bit_wav
from sarcophage.api import get_file_entries
from sarcophage.file_entry import FileEntry


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--directory', '-d', default=None, required=True)
    ap.add_argument('--dry-run', '-n', default=False, action='store_true')
    ap.add_argument('files', nargs='+', metavar='FILE')
    args = ap.parse_args()
    for filename in args.files:
        if not os.path.isfile(filename):
            continue
        print('***', filename)
        with open(filename, 'rb') as fp:
            basename = os.path.basename(filename)
            if filename.endswith('.bfsar') or filename.endswith('.bars'):
                directory = os.path.join(args.directory, os.path.splitext(basename)[0])
                file_entries = get_file_entries(fp)
            elif filename.endswith('.bfwav'):
                directory = args.directory
                file_entries = [FileEntry(basename, fp.read())]
            else:
                raise NotImplementedError('...')
            for fent in file_entries:
                if not fent.name.endswith('.bfwav'):
                    continue
                try:
                    bfw_info = read_bfwav(io.BytesIO(fent.data))
                except MultiChannelFile as mcf:
                    print('[!]', mcf)
                    continue
                dest_name = os.path.join(directory, fent.name.replace('.bfwav', '.wav'))
                dest_dir = os.path.dirname(dest_name)
                if args.dry_run:
                    print(dest_name)
                    continue
                if not os.path.isdir(dest_dir):
                    os.makedirs(dest_dir)

                write_16_bit_wav(dest_name, bfw_info['info']['sample_info']['sample_rate'], bfw_info['data'])
                print('->', dest_name)


if __name__ == "__main__":
    main()
