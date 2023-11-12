import csv
import os
import bs4
import shutil
import configparser

from glob import glob
from lxml import etree
from pathlib import Path


DEFAULT_CONFIG = Path("./pagesearch/config.cfg")
CSV_HEADER = ['search', 'file', 'line', 'text', 'original']
CSV_FILE = 'results.csv'


class PageSearch:
    def __init__(
            self,
            input_dir: Path,
            output_dir: Path = None,
            recursive: bool = True,
            config: Path = DEFAULT_CONFIG
    ) -> None:
        """
        Loads all .xml files from a folder based on arguments and makes them searchable

        :param input_dir: input directory root path
        :param output_dir: output directory (will be created if not existent)
        :param recursive: search all folders recursively
        :param config: change default config file path
        """
        self.__input_dir: Path = input_dir
        self.__output_dir: Path = output_dir
        self.__recursive: bool = recursive
        self.__config: Path = config

        self.__excluded = []  # excluded from search
        self.__included = []  # file extensions to copy
        self.__modify_extension = ''  # Modify file name in xml file
        self.__load_config()

        self.files: list[Path] = []
        self.__load_files()

    def __load_config(self) -> None:
        """
        Loads config file with argparse

        :return: None
        """
        cfg = configparser.ConfigParser(converters={
            'list': lambda x: [i.strip() for i in x.splitlines() if i != ''],
        })
        cfg.read(DEFAULT_CONFIG.as_posix())
        self.__excluded = cfg.getlist('Blacklist', 'excluded')
        self.__included = cfg.getlist('Whitelist', 'copy')
        self.__modify_extension = cfg.get('Whitelist', 'modify_extension')

    def __load_files(self) -> None:
        """
        loads all .xml paths

        :return: None
        """
        self.files = glob(self.__input_dir.joinpath('**', '*.xml').as_posix(), recursive=self.__recursive)
        self.files = list(filter(lambda p: Path(p).name not in self.__excluded, self.files))  # apply blacklist
        self.files.sort()

    def __parse_search(self, fp: Path) -> list[str]:
        """
        parse search file and returns list of char sequences

        :param fp: path to file
        :return: list of file content
        """
        with open(fp.as_posix(), 'r', encoding='utf-8') as f:
            data = f.readlines()
        return [x.strip() for x in data if x.strip() != '' and not x.startswith('#')]

    def __get_line_text(self, text_line: bs4.PageElement) -> str:
        """
        extracts text from a TextLine elements, returns empty string if nothing found

        :param text_line:
        :return:
        """
        equiv = text_line.find('TextEquiv', recursive=False)
        if equiv is None:
            return ''
        line = equiv.find('Unicode')
        if line is None:
            return ''
        return line.text

    def __print_results(self, results: dict) -> None:
        """
        Prints results of search in readable format

        :param results: results dictionary from search method
        :return: None
        """
        for key, val in results.items():
            print(key)
            for hits in val:
                print(f'\tFound {hits["search"]} in line {hits["line_number"]}: "{hits["line_text"]}"')

    def __copy_results(self, results: dict) -> Path:
        """
        Copy and rename files specified in config.cfg to output folder and creates results.csv in output folder

        :param results: results dictionary from search method
        :return: path to results.csv file
        """
        if not self.__output_dir.exists():
            os.mkdir(self.__output_dir)

        csv_content = []
        file_counter = 1
        for key, val in results.items():
            f_path = Path(key)
            f_name = f_path.name.replace('.xml', '')
            for extension in self.__included:
                orig = f_path.parent.joinpath(f_name + extension)
                new = self.__output_dir.joinpath(f'{file_counter:05d}{extension}')
                shutil.copy(orig, new)
                if self.__modify_extension.strip() and '.xml' in extension:
                    self.__fix_xml(new, f'{file_counter:05d}{self.__modify_extension}')
            for appearance in val:
                csv_content.append(
                    [
                        appearance['search'],
                        f'{file_counter:05d}',
                        appearance['line_number'],
                        appearance['line_text'],
                        f_path.parent.relative_to(self.__input_dir).joinpath(f_name).as_posix()
                    ]
                )
            file_counter += 1
        csv_file = self.__write_csv(csv_content)
        return csv_file

    def __write_csv(self, content: list[list]) -> Path:
        """
        Writes a nested list to a csv file, name specified in global variables

        :param content: nested list of data
        :return: path to csv file
        """
        fp = Path(self.__output_dir.joinpath(CSV_FILE))
        with open(fp.as_posix(), 'w', encoding='utf-8', newline='') as f:
            stream = csv.writer(f)
            stream.writerow(CSV_HEADER)
            stream.writerows(content)
        return fp

    def __fix_xml(self, xml_path: Path, filename: str) -> None:
        """
        Tries to change imageFilename in pageXML file

        :param xml_path: path to xml file
        :param filename: new filename
        :return: None
        """
        root = etree.parse(xml_path).getroot()
        if root is None:
            return
        try:
            page = root.find(".//{*}Page")
            page.set('imageFilename', filename)
            with open(xml_path, "w", encoding='utf-8') as outfile:
                outfile.write(etree.tostring(root, encoding="unicode", pretty_print=True))
        except Exception as e:
            print(e)

    def search(self, search_fp: Path, console: bool = False) -> None:
        """
        searches for char sequences from search text file and outputs results in csv file in output folder.
        copies affected files to output folder (numerated file names) if specified in config.cfg.
        Outputs results only on console if console set to True.

        :param search_fp: path to search text file
        :param console: output results only on console
        :return: None
        """
        search = self.__parse_search(search_fp)
        if not search:
            print('Search empty!')
            return

        if not console and not self.__output_dir:
            print('No output directory set!')
            return

        result: dict = {}  # key: file path, value: list of found data

        for fp in self.files:
            with open(fp, 'r', encoding='utf-8') as f:
                stream = f.read()
                bs = bs4.BeautifulSoup(stream, 'xml')

            line_counter = 1
            for iter_line in bs.find_all('TextLine'):
                line_text = self.__get_line_text(iter_line)
                if line_text == '':
                    continue  # filter empty lines
                for s in search:
                    if s in line_text:
                        if fp not in result:
                            result[fp] = []
                        result[fp].append({
                            'line_number': line_counter,
                            'line_text': line_text,
                            'search': s,
                        })
                line_counter += 1
        if result:
            if console:
                self.__print_results(result)
            else:
                csv_file = self.__copy_results(result)
                print(f'Done! ({csv_file})')  # TODO: add statistics
        else:
            print('Nothing found!')
            return
