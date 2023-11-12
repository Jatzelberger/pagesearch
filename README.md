# PageSearch

Search PageXML files for character sequences, copy matching files to folder with summary file

---

## PageSearch
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
`./search.txt`

### Settings
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

## CSVtoTXT
```
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
```