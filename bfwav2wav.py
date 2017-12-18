import argparse

import os

from bfwav.parsing import read_bfwav
from bfwav.utils import write_16_bit_wav


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--directory', '-d', default='.')
    ap.add_argument('input_files', nargs='+', metavar='FILE')
    args = ap.parse_args()
    os.makedirs(args.directory, exist_ok=True)
    for input_filename in args.input_files:
        with open(input_filename, 'rb') as infp:
            print('<-o  ', input_filename)
            bfw_info = read_bfwav(infp)
            output_filename = os.path.join(args.directory, os.path.basename(infp.name.replace('.bfwav', '.wav')))
            print('  o->', output_filename)
            write_16_bit_wav(output_filename, bfw_info['info']['sample_info']['sample_rate'], bfw_info['data'])


if __name__ == '__main__':
    main()
