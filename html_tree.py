# -*- coding: utf-8 -*-
import re
from warnings import warn

from . import htmltools
from .node import Node
from .tree import Tree


class HtmlTree(Tree):
    def __init__(self, text):
        self.blacklist = ["script", "style", "svg",  "obj", "input"]
        Tree.__init__(self)
        self.text = text
        self.root = Node(tag="body", content="")
        self.opened = []
        self._skip_blacklist = False

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if not isinstance(text, str):
            raise TypeError
        self._text = htmltools.get_body(text).group(2)
        self._text = htmltools.clean_text(self._text)

    @property
    def skip_blacklist(self):
        return self._skip_blacklist

    @skip_blacklist.setter
    def skip_blacklist(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("skip_blacklist must be boolean")
        if value:
            warn(
                "\03393mWarning: This options could skip other open tag " +
                "equals of the current tag if they are inside. This option " +
                "is not recommended\033[0m")
        self._skip_blacklist = value

    def _generatetree(self, node, text):
        while len(text) > 0:
            text = text.strip()
            opentag = re.search(rf"<\s*(\w+)\s?{htmltools.REGEX}*/?>", text)
            closetag = re.search(r"</\s*(\w+)\s*>", text)
            if opentag:
                tag = opentag.group(1)
                if opentag.start(0) == 0:
                    if tag in self.blacklist and self._skip_blacklist:
                        close_blacklist = re.search(rf"</\s*{tag}\s*>", text)
                        text = text[close_blacklist.end(0):]
                        continue
                    new_node = Node(tag, "", node)
                    node = new_node
                    if self.deep < new_node.deep:
                        self.deep = new_node.deep
                    text = text[opentag.end(0):]
                    if not htmltools.is_special(opentag):
                        self.opened.append(tag)
                elif opentag.start(0) < closetag.start(0):
                    node.content += text[:opentag.start(0)]
                    text = text[opentag.start(0):]
                else:
                    text = self.close_node(closetag, node, opentag, text)
                    node = node.parent
            else:
                text = self.close_node(closetag, node, opentag, text)
                node = node.parent

    def close_node(self, closetag, node, opentag, text):
        closed = htmltools.is_closed(opentag, closetag)
        tag = closetag.group(1)
        if closed == -1:
            raise SyntaxError(f"{tag} is open but never closed")
        if closed:
            oldtag = self.opened.pop()
            if tag != oldtag:
                parent_tag = self.opened.pop()
                if parent_tag != tag:
                    raise RuntimeError(f"Unexpected tag found {tag}!={oldtag}")
            rest_text = text[:closetag.start(0)]
            if len(rest_text) > 0:
                hextext = (
                        f"{hex(id(node.childs[-1]))} "
                        if len(node.childs) > 0 else "")
                node.content += (
                        f"{hextext}{rest_text}"
                        if hextext not in node.content else rest_text)
            text = text[closetag.end(0):]
        return text

    def generatetree(self):
        self._generatetree(self.root, self._text)
