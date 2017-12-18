from sarcophage.file_entry import FileEntry
from sarcophage.fsar.file import parse_file_section
from sarcophage.fsar.fsar import parse_fsar_header
from sarcophage.fsar.info import parse_info_section
from sarcophage.fsar.strg import parse_strg_section
from sarcophage.fsar.warc import extract_warc


def get_fsar_file_entries(fp):
    header = parse_fsar_header(fp)
    sections = {si['id']: si for si in header['section_infos']}
    strings = parse_strg_section(fp, sections[0x2000]['offset'])
    info_sec = parse_info_section(fp, sections[0x2001]['offset'])
    file_sec_offset = sections[0x2002]['offset']
    for warc in info_sec['warcs']:
        file = info_sec['file_infos'][warc['file_id']]
        if file['offset'] == 0xFFFFFFFF:  # ???
            continue
        warc_name = strings[warc['name_string_id']]['data'].strip(b'\x00').decode()
        for i, wav in enumerate(extract_warc(fp, file_sec_offset=file_sec_offset, file_info=file)):
            name = '%s__%05d.b%s' % (warc_name, i, wav[:4].decode().lower())
            yield FileEntry(name, data=wav)
