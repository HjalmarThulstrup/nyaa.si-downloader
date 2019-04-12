import re

def get_search_url(search_str):
    search = re.sub(r"[^a-zA-Z0-9]+", '+', search_str)
    return "https://nyaa.si/?f=0&c=1_2&q=" + search + "&s=seeders&o=desc"