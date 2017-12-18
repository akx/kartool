from sarcophage.fsar.file import parse_file_section
from sarcophage.fsar.fsar import parse_fsar_header
from sarcophage.fsar.info import parse_info_section
from sarcophage.fsar.strg import parse_strg_section
from .structs import FSAR_HEADER


def get_fsar_file_entries(fp):
    header = parse_fsar_header(fp)
    sections = {si['id']: si for si in header['section_infos']}
    strings = parse_strg_section(fp, sections[0x2000]['offset'])
    info_sec = parse_info_section(fp, sections[0x2001]['offset'])
    file_section = parse_file_section(fp, sections[0x2002]['offset'], file_infos=info_sec['file_infos'])
    return []
