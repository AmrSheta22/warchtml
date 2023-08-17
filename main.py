import json_creator_from_all as jcf
import warc_extract as we
import argparse

# create an argument parser
parser = argparse.ArgumentParser(description="Extract HTML content from WARC files")
# add arguments to the parser
parser.add_argument(
    "-d")
# parse the arguments
args = parser.parse_args()
# store the arguments


def main():
    warc_path = args.d
    # call the function
    dir_path = we.warc_to_html(warc_path)
    # process dir with json creator
    jcf.json_creater(dir_path)

if __name__ == "__main__":
    main()