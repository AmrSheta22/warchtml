# html-at-WARC
This project is for machine learning purposes on WARC files. It converts a directory containing WARC files to the html files containing valuable data, then converts all htmls into a json data structure containing the p, h, title, header tags inside it.

## Usage
This project is built with python3 and the requirments for the project are stored in requirments.txt
```
pip install -r requirments
```
Then you can run the code as follows:
```
python3 main.py -d {your_directory}
```
it will then output 4 things, two files and two folders. "extracted{n}" folder contains the htmls, "extracted_dump{n}" folder contains the data around html files like css, javascript and image files etc, "extracted{n}.json" file contains json file containing all data, "allfileurls{n}.txt" which contains all urls extracted from the html file.
