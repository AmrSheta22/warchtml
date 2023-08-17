from warcio.archiveiterator import ArchiveIterator
import os
from bs4 import BeautifulSoup


# a function that takes a warc file and outputs all files in text format
def warc_to_html(warc_file_path, all=False, number_of_files=70000):
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
    for file in os.listdir(warc_file_path):

        with open("{}/{}".format(warc_file_path, file), "rb") as warc_file:
            # a variable to keep track of the user input number_of_files
            count = 0
            # a variable to count the number of iterations done (debugging)
            count1 = 0

            for record in ArchiveIterator(warc_file):
                count1 += 1
                # check the record type, if it's not response then it can't contain html
                if record.rec_type == "response":
                    # Access the response content

                    # Convert response content to UTF-8 and parse as HTML
                    try:
                        # check that it's not just a dns number, if it's not, then it can contain html
                        if record.rec_headers.get_header("Content-Type") != "text/dns":
                            # read content and decode it with utf-8
                            response_content = record.content_stream().read()
                            html_content = response_content.decode("utf-8", "replace")
                            # get the url and santize it to be able to  read it
                            raw_name = record.rec_headers.get_header("WARC-Target-URI")
                            # here the code loops over the characters in the name and and checks it's not a special character, if it is, it replaces it with an underscore
                            sanitized_name = "".join(
                                c if c.isalnum() or c in ("-", "_") else "_"
                                for c in raw_name
                            )
                            # fiter non html files
                            if not (
                                sanitized_name.lower().endswith("jpg")
                                or sanitized_name.lower().endswith("png")
                                or sanitized_name.lower().endswith("gif")
                                or sanitized_name.lower().endswith("js")
                                or sanitized_name.lower().endswith("css")
                                or sanitized_name.lower().endswith("txt")
                                or sanitized_name.find("css") + 1
                            ):
                                # check html file has content and is not empty
                                if (
                                    "html" in html_content
                                    or "div" in html_content
                                    or "DOCTYPE" in html_content
                                ) and filter_html_pages(html_content):
                                    # create a file with the name of the url and write the html content in it, the santized name stops at 100 characters to avoid long names
                                    name = f"extracted{extracted_number-1}/{sanitized_name[:100]}.html"
                                    # write the url in a file to be able to access it later
                                    with open(
                                        "allfileurls" + str(extracted_number-1) + ".txt", "a"
                                    ) as f:
                                        f.write(name[11:])
                                        f.write("\n")
                                    # write the html content in the file
                                    with open(name, "w", encoding="utf-8") as f:
                                        f.write(html_content)
                                        count += 1
                                    # check if the user wants all the files or just a certain number
                                    if all != True:
                                        if count == number_of_files:
                                            print(
                                                "created "
                                                + str(number_of_files)
                                                + " directories"
                                            )
                                            break
                                else:
                                    # store the files that are not html content in a different folder
                                    name = f"extracted_dump{extracted_number-1}/{sanitized_name[:100]}.txt"
                                    with open(name, "w", encoding="utf-8") as f:
                                        f.write(html_content)
                    except UnicodeDecodeError:
                        print("Error decoding HTML content")
        print(count1)
    return "extracted" + str(extracted_number-1)


def filter_html_pages(html_content):
    # read the html file
    try:
        soup = BeautifulSoup(html_content, "html.parser")
    except:
        return False
    # find all the paragraphs in the html file
    paragraphs = soup.find_all("p")
    # create a list to store the paragraphs
    paragraphs_list = []
    # loop over the paragraphs and append them to the list
    for paragraph in paragraphs:
        paragraphs_list.append(paragraph.text)
    # create a string to store the paragraphs
    paragraphs_string = ""
    # loop over the list and add the paragraphs to the string
    for paragraph in paragraphs_list:
        if (
            (paragraph.find("Could not find file") + 1)
            or (paragraph.find("404") + 1)
            or (paragraph.find("Invalid URL") + 1)
            or (paragraph.lower().find("page can't be found") + 1)
            or (paragraph.lower().find("page not found") + 1)
            or (paragraph.lower().find("page not available") + 1)
            or (paragraph.lower().find("page cannot be found") + 1)
            or (paragraph.lower().find("page cannot be displayed") + 1)
            or (paragraph.lower().find("page you are looking for could not be found") + 1)
        ):
            return False
        paragraphs_string += paragraph
    # return the string
    if len(paragraphs_string) < 300:
        return False
    else:
        return True
