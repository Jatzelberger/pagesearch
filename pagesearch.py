from pagesearch import cli
from docopt import docopt

if __name__ == '__main__':
    args = docopt(cli.cli_doc, help=True, version='pagesearch v1.0', options_first=False)
    cli.parse(args)
