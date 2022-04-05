#!/usr/bin/env python
from warnings import warn
from .html_tree import HtmlTree
from .node import Node


def tree2text(html_tree: HtmlTree):
    if not isinstance(html_tree, HtmlTree):
        raise TypeError("html_tree argument must be HtmlTree type")
    nodes = html_tree.mergenodes()
    last_tag = ""
    text = ""
    for node in nodes:
        if node.content == "" and len(node.childs) == 0:
            warn(f"\033[93mThe tree was not clean. Tag {node.tag}\033[0m")
        if node.tag == last_tag:
            text = f"{text}\n"
        if node.content != "":
            if "h" in node.tag:
                text = f"{text}\t{node.content}\n"
            elif node.tag == last_tag:
                text = f"{text}{node.content}\n"
            else:
                text = f"{text}{node.content}"
            last_tag = node.tag
    return text


def delnodes(html_tree: HtmlTree):
    stack = [html_tree.root]
    while len(stack) > 0:
        node = stack.pop(0)
        start = len(node.childs)
        if node.content == "":
            if start == 0:
                node = delbranch(node)
                html_tree.delbranch(node)
                continue
            if start == 1:
                text = hex(id(node)) + " "
                while len(node.childs) == 1 and node.content == "":
                    parent = node.parent
                    pos = parent.childs.index(node)
                    parent.childs.pop(pos)
                    node = node.childs[0]
                    parent.childs.insert(pos, node)
                    node.setparent(parent)
                if len(node.childs) == 0 and node.content == "":
                    node = delbranch(node)
                    html_tree.delbranch(node)
                    continue

                new_text = hex(id(node)) + " "
                parent.content = parent.content.replace(text, new_text)
        stack.extend(node.childs[::-1])


def delbranch(node: Node):
    parent = node.parent
    while len(parent.childs) == 1 and parent.content == "":
        node = parent
        parent = node.parent
    return node
