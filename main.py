import warc_extract as we
import argparse
import os
import multiprocessing
# create an argument parser
def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
    
parser = argparse.ArgumentParser(description="Extract HTML content from WARC files")
# add arguments to the directory
parser.add_argument(
    "-d",
    type=str,
    help="the directory of the warc files that you want to extract",
    )
# add arguments to if you want to zipped file
parser.add_argument(
    "-getzip",
    type=str2bool,
    nargs='?',
    const=True,
    default=True,
    help= "if you want the code to get all the output files in a zipped file",
    )
# add argement to if you want the extracted files
parser.add_argument(
    "-multi",
    type=str2bool,
    nargs='?',
    const=True,
    default=True,
    help= "if you want the code to use multiprocessing to speed up the process",
    )
parser.add_argument(
    "-getextracted",
    type=str2bool,
    nargs='?',
    const=True,
    default=True,
    help= "if you want the code to get all the output files in a folder",
    )
parser.add_argument(
    "-getdump",
    type=str2bool,
    nargs='?',
    const=True,
    default=False,
    help= "if you want the code to get all the output files that are not html content in a folder",
    )
# parse the arguments
args = parser.parse_args()
# store the arguments


def main():
    multiprocessing.set_start_method('spawn')
    warc_path = args.d
    zipped_b = args.getzip
    extracted_b = args.getextracted
    multi = args.multi
    dump = args.getdump
    for i in os.listdir(warc_path):
        print(os.path.join(warc_path, i))
        we.warc_to_html(os.path.join(warc_path, i), zipped=zipped_b, extracted=extracted_b, multi=multi, dump=dump)

if __name__ == "__main__":
    main()