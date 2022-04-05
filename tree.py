import re
from .node import Node


class Tree:
    def __init__(self):
        self.root = None
        self.deep = 0
        self._default_print = 0
        self._current_node = self.root
        self._is_iter = False

    @property
    def default_print(self):
        if self._default_print == 0:
            return "bfs"
        if self._default_print == 1:
            return "dfs"
        raise RuntimeError("There isnt a valid print configuration")

    @default_print.setter
    def default_print(self, value):
        values = "bfs", "dfs"
        if value.lower() not in values:
            raise RuntimeError("There isnt a valid print configuration")
        self._default_print = values.index(value.lower())

    def addnode(self, tag, content, parent):
        new_node = Node(tag, content, parent)
        if new_node.deep > self.deep:
            self.deep = new_node.deep

    def _bfs(self, blacklist=None):
        queue = [self.root]
        while len(queue) > 0:
            node = queue.pop(0)
            if blacklist and node.tag in blacklist:
                self.delete(node)
                continue
            queue.extend(node.childs)
            yield node

    def _dfs(self, merge=False):
        stack = [self.root]
        while len(stack) > 0:
            node = stack.pop()
            if merge:
                self.cleantags(node)
            stack.extend(node.childs[::-1])
            yield node

    def cleantags(self, node):
        tags = re.findall(
              re.compile(r"0x[0-9a-f]+\s", re.IGNORECASE), node.content)
        dellist = []
        for tag in tags:
            for child in node.childs:
                if hex(id(child)) == tag[0:-1]:
                    if len(child.childs) > 0:
                        self.cleantags(child)
                    node.content = node.content.replace(tag, child.content)
                    dellist.append(node.childs.index(child))
            while len(dellist) > 0:
                node.childs.pop(dellist.pop())

    @property
    def bfs(self):
        return self._bfs()

    @property
    def dfs(self):
        return self._dfs()

    def cleantree(self, blacklist):
        inital_len = self.deep
        self.deep = len(tuple(_ for _ in self._bfs(blacklist)))
        return inital_len - self.deep

    def __len__(self):
        return self.deep

    def __str__(self):
        return_s = ""
        nodes = self.bfs if self._default_print == 0 else self.dfs
        for node in nodes:
            return_s += str(node) + "\n"
        return return_s

    def __iter__(self):
        self._current_node = self.root
        return self

    def __next__(self):
        next_node = self.bfs if self.default_print == 0 else self.dfs
        if next_node is not None:
            return next_node
        raise StopIteration

    def delete(self, del_node):
        text = hex(id(del_node)) + " "
        del_node.parent.content = del_node.parent.content.replace(text, "")
        del_node.parent.childs.pop(del_node.parent.childs.index(del_node))
        if del_node.deep == self.deep:
            self.recalldeep()

    def delbranch(self, node):
        self.delete(node)

    def mergenodes(self):
        return self._dfs(True)

    def recalldeep(self):
        pass

    def serialize(self, tree=None, node=None):
        if node is None:
            node = self.root
        if tree is None:
            tree = {}
        _id = hex(id(node))
        tree[_id] = {"content": node.content, "tag": node.tag, "childs": {}}
        for child in node.childs:
            self.serialize(tree[_id]["childs"], child)
        return tree
