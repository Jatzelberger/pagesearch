# PageSearch

Search PageXML files for character sequences, copy matching files to folder with summary file

---

## Usage

```
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
```

### Search

Text file containing symbols and substrings to be searched (Separated by new line):
`./search/<search_name>.txt`

### Settings

Configure search parameters, example provided in:
`./pagesearch/config.cfg`

### Example

#### Output results on console

```
$ python pagesearch.py -c -r .\search.txt '\home\someuser\input\'
```

#### Output results in .csv file and copies matching files to output folder

```
$ python pagesearch.py -r .\search.txt '\home\someuser\input\' '\home\someuser\output\'
```

Output example (for each found query):

```csv
search,out_file,line,text,original_file
,00001,24,Ir getruwet deſter wur ir man,eval/eval/b_welscher-2/pages/rem/0053
```

## ZPD

Developed at [Zentrum für Philologie und Digitalität](https://www.uni-wuerzburg.de/en/zpd/startseite/) at the [Julius-Maximilians-Universität of Würzburg](https://www.uni-wuerzburg.de/en/home/)