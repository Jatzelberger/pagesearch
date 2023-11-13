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

        self.__xml_config = ''
        self.__copy_config = []
        self.__xml_update = ''
        self.__ex_files = []
        self.__ex_folders = []
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
            'map': lambda x: [i.replace(' ', '').split('>') for i in x.splitlines() if i != ''],
        })
        cfg.read(DEFAULT_CONFIG.as_posix())
        self.__xml_config = cfg.get('EXTENSIONS', 'xml')
        self.__copy_config = cfg.getmap('EXTENSIONS', 'copy')
        self.__xml_update = cfg.get('EXTENSIONS', 'xml_update')
        self.__ex_files = cfg.getlist('EXCLUDED', 'files')
        self.__ex_folders = cfg.getlist('EXCLUDED', 'folders')

    def __load_files(self) -> None:
        """
        loads all .xml paths

        :return: None
        """
        self.files = glob(self.__input_dir.joinpath('**', f'*{self.__xml_config}').as_posix(), recursive=self.__recursive)
        self.files = list(filter(lambda p: Path(p).name not in self.__ex_files, self.files))  # remove excluded files
        self.files = list(filter(lambda p: not any(folder in Path(p).relative_to(self.__input_dir).as_posix() for folder in self.__ex_folders), self.files))  # remove excluded folders
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
                print(f'\tFound {hits["search"]} in line {hits["line"]}: "{hits["text"]}"')

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

    def __copy_results(self, results: dict) -> Path:
        """
        Copy and rename files specified in config.cfg to output folder and creates results.csv in output folder

        :param results: results dictionary from search method
        :return: path to results.csv file
        """
        if not self.__output_dir.exists():
            os.mkdir(self.__output_dir)

        csv_content = []
        fc = 1  # file counter
        for path, hits in results.items():
            orig_xml_path = Path(path)
            orig_name = orig_xml_path.name.replace(self.__xml_config, '')  # removes xml file extension
            for ext_index in range(len(self.__copy_config)):
                # generate paths and filenames
                orig_path = orig_xml_path.parent.joinpath(f'{orig_name}{self.__copy_config[ext_index][0]}')
                new_path = self.__output_dir.joinpath(f'{fc:05d}{self.__copy_config[ext_index][1]}')
                if orig_path.exists():
                    shutil.copy(orig_path, new_path)
                    # update xml if needed
                    if self.__copy_config[ext_index][0] == self.__xml_config and self.__xml_update:
                        self.__fix_xml(new_path, f'{fc:05d}{self.__xml_update}')
                else:
                    print('FileNotFound (skip):', orig_path.as_posix())
            # prepare data for csv file
            for hit in hits:
                csv_content.append([
                    hit['search'],
                    f'{fc:05d}',
                    hit['line'],
                    hit['text'],
                    orig_xml_path.parent.relative_to(self.__input_dir).joinpath(orig_name).as_posix()
                ])
            fc += 1
        return self.__write_csv(csv_content)

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
                            'line': line_counter,
                            'text': line_text,
                            'search': s,
                        })
                line_counter += 1

        if result:
            if console:
                self.__print_results(result)
            else:
                csv_file = self.__copy_results(result)
                print(f'Done! ({csv_file})')
        else:
            print('Nothing found!')
            return
