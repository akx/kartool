import argparse
import os

from io import BytesIO

from bfwav.excs import MultiChannelFile
from bfwav.parsing import read_bfwav
from bfwav.utils import write_16_bit_wav
from sarcophage.api import get_file_entries


def main():
    ap = argparse.ArgumentParser(prog='extract_arc')
    ap.add_argument('--directory', '-d', default=None)
    ap.add_argument('--dry-run', '-n', default=False, action='store_true')
    ap.add_argument('--convert-bfwav', default=False, action='store_true')
    ap.add_argument('file')
    args = ap.parse_args()

    if not args.directory:
        args.directory = os.path.splitext(args.file)[0]

    fp = open(args.file, 'rb')
    file_entries = get_file_entries(fp)
    for fent in file_entries:
        name = fent.name
        data = fent.data
        if args.convert_bfwav and name.endswith('.bfwav'):
            try:
                with BytesIO(fent.data) as infp, BytesIO() as outfp:
                    parsed_bfwav = read_bfwav(infp)
                    write_16_bit_wav(
                        outfp,
                        sample_rate=parsed_bfwav.sample_rate,
                        pcm_datas=parsed_bfwav.pcm_datas,
                    )
                    data = outfp.getvalue()
                name = name.replace('.bfwav', '.wav')
            except MultiChannelFile as mcf:
                print('{}: not converted: {}'.format(name, mcf))

        dest_name = os.path.join(args.directory, name)
        dest_dir = os.path.dirname(dest_name)
        if args.dry_run:
            print(dest_name)
            continue
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

        with open(dest_name, 'wb') as outf:
            outf.write(data)
            print(dest_name)


if __name__ == "__main__":
    main()
