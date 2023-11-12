import csv

from docopt import docopt
from pathlib import Path


cli_doc = """CSVtoTXT Command Line Tool
Extracts the first column of a .csv file and writes it to a .txt file

Usage:
    csv_to_txt.py (-h | --help)
    csv_to_txt.py (-v | --version)
    csv_to_txt.py INPUT OUTPUT
    
Arguments:
    INPUT       Input csv file with extension
    OUTPUT      Output txt file with extension
    
Options:
    -h --help           Show this screen.
    -v --version        Show version.
    
Github:
    https://github.com/Jatzelberger/csvtotxt
"""


def run(in_fp: Path, out_fp: Path) -> None:
    """
    Extracts first column from csv file to txt file

    :param in_fp: Path to csv file
    :param out_fp: Path to txt file (overrides existing file)
    :return: None
    """

    cells = []
    with open(in_fp.as_posix(), 'r', encoding='utf-8') as f:
        stream = csv.reader(f, delimiter=',')
        for row in stream:
            if row[0]:
                cells.append(row[0])

    with open(out_fp.as_posix(), 'w', encoding='utf-8') as f:
        f.write('\n'.join(cells))


if __name__ == '__main__':
    args = docopt(cli_doc, help=True, version='CSVtoTXT v1.0', options_first=False)
    if args.get('INPUT') and args.get('OUTPUT'):
        run(Path(args.get('INPUT')), Path(args.get('OUTPUT')))
