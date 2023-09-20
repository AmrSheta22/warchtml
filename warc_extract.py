from warcio.archiveiterator import ArchiveIterator
import os
from bs4 import BeautifulSoup
import html
import json
from multiprocessing import Pool
import zipfile
from functools import partial
import warnings

# ignore warnings
warnings.filterwarnings("ignore")


def create_dump(html_content, santized_name, extracted_number):
    name = f"extracted_dump{extracted_number-1}/{santized_name[-100:]}"
    with open(name, "w", encoding="utf-8") as f:
        f.write(html_content)


def contains_html(html_content):
    if "html" in html_content or "div" in html_content or "DOCTYPE" in html_content:
        return True
    else:
        return False


def name_is_valid(sanitized_name):
    if not (
        sanitized_name.lower().endswith("jpg")
        or sanitized_name.lower().endswith("png")
        or sanitized_name.lower().endswith("gif")
        or sanitized_name.lower().endswith("js")
        or sanitized_name.lower().endswith("css")
        or sanitized_name.lower().endswith("txt")
        or sanitized_name.find("css") + 1
    ):
        return True
    else:
        return False


def is_html_file(record, extracted_number, zipped, extract, dump):
    # read content and decode it with utf-8
    record_content = record[0]
    raw_name = record[1]
    html_content = record_content.decode("utf-8", "replace")
    # get the url and santize it to be able to  read it
    # here the code loops over the characters in the name and and checks it's not a special character, if it is, it replaces it with an underscore
    sanitized_name = "".join(
        c if c.isalnum() or c in ("-", "_") else "_" for c in raw_name
    )
    # fiter extracted3non html files
    if (
        name_is_valid(sanitized_name)
        and filter_html_pages(html_content, extracted_number-1)
        and contains_html(html_content)
    ):
        # create a file with the name of the url and write the html content in it, the santized name stops at 100 characters to avoid long names
        name = f"extracted{extracted_number-1}/{sanitized_name[:100]}.html"
        # write the url in a file to be able to access it later
        with open("allfileurls" + str(extracted_number - 1) + ".txt", "a") as f:
            f.write(sanitized_name)
            f.write("\n")
        # write the html content in the file
        with open(name, "w", encoding="utf-8") as f:
            f.write(html_content)
        # add file to zipped file
        if zipped:
            with zipfile.ZipFile(
                "extracted{}.zip".format(extracted_number - 1), "a"
            ) as zip:
                os.chdir("extracted" + str(extracted_number - 1))
                zip.write(f"{sanitized_name[:100]}.html")
                os.chdir("..")
        # delete the file
        if not extract:
            os.remove(name)
    else:
        # store the files that are not html content in a different folder
        if dump:
            create_dump(html_content, sanitized_name, extracted_number)


# create
# a function that takes a warc file and outputs all files in text format
def warc_to_html(warc_file_path, zipped=True, extracted=True, multi=True, dump=False):
    # create directory extracted{n+1} if extracted{n} was found
    extracted_number = 0
    while "extracted" + str(extracted_number) in os.listdir("."):
        extracted_number += 1
    os.makedirs("extracted" + str(extracted_number))
    # same here but with extracted_dump, here we store things we don't need
    while "extracted_dump" + str(extracted_number) in os.listdir("."):
        extracted_number += 1
    os.makedirs("extracted_dump" + str(extracted_number))
    # same here but with extracted_dump, here we store things we don't need
    while "extracted_dump" + str(extracted_number) in os.listdir("."):
        extracted_number += 1

    with open("extracted{}.json".format(extracted_number - 1), "w") as f:
        f.write("[\n")
    # use multiprocessing to speed up the process
    partial_func = partial(
        is_html_file,
        extracted_number=extracted_number,
        zipped=zipped,
        extract=extracted,
        dump=dump,
    )
    with open(warc_file_path, "rb") as warc_file:

        def stream_data(warc_file):
            for record in ArchiveIterator(warc_file):
                try:
                    if (
                        record.rec_type == "response"
                        and record.rec_headers.get_header("Content-Type") != "text/dns"
                    ):
                        x = (
                            record.content_stream().read(),
                            record.rec_headers.get_header("WARC-Target-URI"),
                        )
                        yield x
                except Exception as e:
                    print(e)

        if multi:
            with Pool(2) as p:
                for i in stream_data(warc_file):
                    p.apply_async(partial_func, args=(i,))
        else:
            for i in stream_data(warc_file):
                partial_func(i)
        # for i in stream_data(warc_file):
        #     is_html_file(i, extracted_number)
    # partial_func = partial(is_html_file, extracted_number=extracted_number)
    # print("i am here")
    # with open(warc_file_path, "rb") as warc_file:
    #     with futures.ThreadPoolExecutor() as executor:
    #         executor.map(
    #             partial_func,
    #             ArchiveIterator(warc_file),
    #         )

    with open("extracted{}.json".format(extracted_number - 1), "r+") as f:
        f.seek(0, os.SEEK_END)
        pos = f.tell() - 1
        f.seek(pos, os.SEEK_SET)
        f.seek(pos - 1, os.SEEK_SET)
        f.truncate()
        f.write("\n]")
    # delete the unwanted directory
    if not extracted:
        os.rmdir("extracted" + str(extracted_number-1))
    if not dump:
        os.rmdir("extracted_dump" + str(extracted_number-1))
    return "extracted" + str(extracted_number - 1)


def in_bad_words(paragraph):
    bad_words = [
        "Could not find file",
        "404",
        "Invalid URL",
        "Page can't be found",
        "Page not found",
        "Page not available",
        "Page cannot be found",
        "Page cannot be displayed",
        "Page you are looking for could not be found",
        "Page you are looking for cannot be found",
        "Page you are looking for is not available",
        "It seems that we can't find what you're looking for",
        "Sorry, this entry is only available",
    ]
    for word in bad_words:
        # paragraph.find return -1 if it didn't find the word
        if paragraph.find(word)+1:
            return True
    return False

def a_tag_or_no_tag(soup, tag): 
    """that's the question—Whether 'tis nobler in the mind
    to suffer The slings and arrows of outrageous fortune, 
    Or to take arms against a sea of troubles, And, by opposing, end them 
    """
    if soup.find(tag) is None:
        tag = ""
    else:
        tag = html.unescape(soup.find(tag).text)
    

def filter_html_pages(html_content, extracted_number):
    # read the html file
    try:
        soup = BeautifulSoup(html_content, "html.parser")
    except:
        print("holy shit this is alot")
        return False
    # find all the paragraphs in the html file
    paragraphs = soup.find_all("p")
    headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    p_and_h = paragraphs.copy()
    # extend the list with the headers
    p_and_h.extend(headers)
    # create a list to store the pargraph or head  text
    paragraphs_list = []
    for paragraph in p_and_h:
        paragraphs_list.append(paragraph.text)
    # create a string to store the paragraphs (this is done to minimize time since using join will iterate over the paragraphs again)
    paragraphs_string = ""
    for paragraph in paragraphs_list:
        if in_bad_words(paragraph):
            return False
        paragraphs_string += paragraph

    # if all paragraph is too short, the page has failed us    
    if len(paragraphs_string) < 300:
        return False
    else:
        filtered_p_tags = filter_tags(paragraphs)
        filtered_h_tags = filter_tags(headers)
        # get the title of the page
        title = a_tag_or_no_tag(soup, "title")
        head = a_tag_or_no_tag(soup, "head")
        # create a dictionary of data
        data = {
            "title": title,
            "head": head,
            "p_tags": filtered_p_tags,
            "h_tags": filtered_h_tags,
        }
        # dump it inside the json file
        with open("extracted{}.json".format(extracted_number), "a") as f:
            json_record = json.dumps(data, indent=4)
            f.write(json_record)
            f.write(",\n")
        return True


def filter_tags(tags):
    filtered_tags = []
    for tag in tags:
        for a in tag.find_all("a"):
            a.replace_with("")
        for noscript in tag.find_all("noscript"):
            noscript.replace_with("")
        if tag.text != "":
            filtered_tags.append(html.unescape(tag.text))
    return filtered_tags
