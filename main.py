#!/usr/bin/env python

import sys
import os
import urllib.request
import urllib.error
import urllib.parse
import json
import datetime

from .appdirectory import UserDirs
from . import html_tree
from . import document_creation


def makerequest(url):
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
    return text


def preparefile(filepath, get_inode = False):
    if os.path.isfile(filepath):
        webcontent = open(filepath, "r+", encoding="UTF-8")
    else:
        webcontent = open(filepath, "w+", encoding="UTF-8")

    webcontent.seek(0)
    cachedata = webcontent.read()
    if len(cachedata) == 0:
        cachedata = "{}"
    jsoncontent = json.loads(cachedata)
    if not get_inode:
        webcontent.close()
        return jsoncontent
    return jsoncontent, webcontent

def storecache(jsonobject,key, value, inode):
    jsonobject[key] = value
    inode.seek(0)
    inode.write(json.dumps(jsonobject))
    inode.close()

def main(url, use_cache):
    if use_cache:
        appname = os.getenv("appname", "webscrapper")
        version = os.getenv("version", "1.0")
        userdirs = UserDirs(appname, version)
        cachedir = userdirs.usercachedir
        filepath = os.path.join(cachedir, "webscrapper.cache")
        if not os.path.isdir(cachedir):
            os.mkdir(cachedir)

        jsoncontent, webcontent = preparefile(filepath, True)
        text = jsoncontent.get("url", "")
        if len(text) == 0:
            text = makerequest(url)
            storecache(jsoncontent, url, text, webcontent)
    else:
        text = makerequest(url)

    tree = html_tree.HtmlTree(text)
    try:
        tree.generatetree()
        tree.cleantree(tree.blacklist)
        document_creation.delnodes(tree)
        result_text = document_creation.tree2text(tree)
    except RecursionError:
        print(f"stop recursion at level {len(tree)}")

    data = {
            "url": url,
            "originaltext": text,
            "text": result_text,
            "resultree": json.dumps(tree.serialize()),
            "date": datetime.datetime.now()
            }
    return data


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        sys.exit(-1)
    elif len(args) == 1:
        args.append("False")
    elif len(args) == 2:
        args[1] = args[1] == "y"
    main(args[0], args[1])
