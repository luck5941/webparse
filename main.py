import sys
import os
import urllib.request
import urllib.error
import urllib.parse
import pathlib
import json
import datetime

from . import html_tree
from . import document_creation
from ..mongo_driver import MongoDriver


def makerequest(url, cachefile):
    fake_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Chrome/47.0.2526.106 Safari/537.36"}
    req = urllib.request.Request(url, headers=fake_headers)
    with urllib.request.urlopen(req) as response:
        response = response.read()
    try:
        text = response.decode("UTF-8")
    except UnicodeDecodeError:
        text = response.decode("latin-1")
    with open(cachefile, "r+", encoding="UTF-8") as webcontent:
        cachedata = webcontent.read()
        if len(cachedata) == 0:
            cachedata = "{}"
        jsoncontent = json.loads(cachedata)
        jsoncontent[url] = text
        webcontent.seek(0)
        webcontent.write(json.dumps(jsoncontent))
        return text


def main(url, use_cache, keyword = "officialDocuments"):
    home = str(pathlib.Path.home())
    cache = f"{home}/.cache/webscrapper"
    filepath = f"{cache}/webscrapper.cache"
    if not os.path.isdir(cache):
        os.mkdir(cache)

    if os.path.isfile(filepath) and use_cache:
        with open(filepath, "r", encoding="UTF-8") as webcontent:
            cachedata = webcontent.read()
            if len(cachedata) == 0:
                cachedata = "{}"
            jsoncontent = json.loads(cachedata)
            text = jsoncontent.get("url", "")
            if len(text) == 0:
                text = makerequest(url, filepath)
    else:
        text = makerequest(url, filepath)
    tree = html_tree.HtmlTree(text)
    try:
        tree.generatetree()
        tree.cleantree(tree.blacklist)
        document_creation.delnodes(tree)
        result_text = document_creation.tree2text(tree)
    except RecursionError:
        print(f"stop recursion at level {len(tree)}")

    mongodriver = MongoDriver(database=os.environ.get("DATABASE", None))
    data = {
            "url": url,
            "originaltext": text,
            "text": result_text,
            "resultree": json.dumps(tree.serialize()),
            "date": datetime.datetime.now()
            }
    mongodriver.insert([data], keyword, "url")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        sys.exit(-1)
    elif len(args) == 1:
        args.append("False")
    elif len(args) == 2:
        args[1] = args[1] == "y"
    main(args[0], args[1])
