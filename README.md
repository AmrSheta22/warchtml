# WARCHTML
This project is for machine learning purposes on WARC files. It converts a directory containing WARC files to the html files containing valuable data, then converts all htmls into a json data structure containing the p, h, title, header tags inside it.
It's the first python script that uses multiprocessing to iterate over all records faster.

## Usage
This project is built with python3 and the requirments for the project are stored in requirments.txt .
```
pip install -r requirments.txt
```
An example of how to use the script:
```
python3 main.py -d copied_warc -getextracted false -getdump false -multi true
```
By default it will output 4 things, three files and one folders. "extracted{n}" folder contains the htmls, "extracted{n}.json" file contains json file containing all data, "allfileurls{n}.txt" which contains all urls extracted from the html file, a zipped file containing all htmls.
It can also output "extracted_dump{n}" which is a folder containing the data that is not html files, like css or javascipt or jpg etc. by modifiying <code>-getdump</code> argument to be true.
