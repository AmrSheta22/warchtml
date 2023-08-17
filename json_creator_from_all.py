import json
import os
from bs4 import BeautifulSoup as bs
import html
# this code is for creating json file from all the html files in a directory
def json_creater(directory):
    all_json = []
    for i in os.listdir(directory):
        with open("{}/{}".format(directory, i), "r", encoding="utf-8") as f:
            content = f.read()
            soup = bs(content, "html.parser")
            # get all <p> tags
            p_tags = soup.find_all("p")
            filtered_p_tags = filter_tags(p_tags)
            # get all <h{n}> tags
            h_tags = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            filtered_h_tags = filter_tags(h_tags)
            # get the title of the page
            if soup.find("title") is None:
                title = ""
            else:
                title = html.unescape(soup.find("title").text)
            # get the head of the page
            if soup.find("head") is None:
                head = ""
            else:
                head = html.unescape(soup.find("head").text)
            # create a dictionary
            data = {
                "title": title,
                "head": head,
                "p_tags": filtered_p_tags,
                "h_tags": filtered_h_tags
            }
            all_json.append({i: data})
    # create a json file
    with open("{}.json".format(directory), "w") as f:
        
        json.dump(all_json, f, indent=4)
            

# filter the <p> and <h{n}> tags by removing text that is hyperlinked, then get the text
def filter_tags(tags):
    filtered_tags = []
    for tag in tags:
        for a in tag.find_all("a"):
            a.replace_with("")
        if tag.text != "":
            filtered_tags.append(html.unescape(tag.text))
    return filtered_tags
