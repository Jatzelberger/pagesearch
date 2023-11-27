from pagesearch import PageSearch
from pathlib import Path

cli_doc = """PageSearch Command Line Tool

Usage:
    pagesearch.py (-h | --help)
    pagesearch.py (-v | --version)
    pagesearch.py (-c | --console) [-r | --recursive] SEARCH INPUT [CONFIG]
    pagesearch.py [-r | --recursive] SEARCH INPUT OUTPUT [CONFIG]

Arguments:
    SEARCH              Search text file
    INPUT               Input directory path
    OUTPUT              Output directory path
    CONFIG              Custom config file                       

Options:
    -h --help           Show this screen.
    -v --version        Show version.
    -c --console        Print output on console without file copy
    -r --recursive      Recursive search in input directory

GitHub:
    https://github.com/Jatzelberger/pagesearch

ZPD:
    Developed at Zentrum für Philologie und Digitalität at the Julius-Maximilians-Universität of Würzburg.
"""


def parse(args: dict[str, any]) -> None:
    """
    Parsing cli arguments and run pagesearch based on input

    :param args: docopt dictionary
    :return: None
    """
    if args.get('CONFIG') is None:
        ps = PageSearch(
            input_dir=Path(args.get('INPUT')).absolute(),
            output_dir=None if args.get('OUTPUT') is None else Path(args.get('OUTPUT')).absolute(),
            recursive=args.get('--recursive')
        )
    else:
        ps = PageSearch(
            input_dir=Path(args.get('INPUT')).absolute(),
            output_dir=None if args.get('OUTPUT') is None else Path(args.get('OUTPUT')).absolute(),
            recursive=args.get('--recursive'),
            config=Path(args.get('CONFIG')).absolute()
        )
    ps.search(Path(args.get('SEARCH')).absolute(), console=args.get('--console'))
