class Node:
    def __init__(self, tag, content, parent=None):
        self._parent = None
        self.parent = parent
        self.childs = []
        self.tag = tag
        self.content = content
        self.deep = parent.deep + 1 if parent is not None else 0

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        if self.setparent(parent):
            parent.addchild(self)

    def setparent(self, parent):
        if parent is not None:
            if not isinstance(parent, Node):
                raise TypeError
            self._parent = parent
            return True
        return False

    @property
    def haschild(self):
        return len(self.childs) > 0

    def addchild(self, child):
        if not isinstance(child, Node):
            raise TypeError
        self.childs.append(child)

    def __str__(self):
        empty = "\"\""
        return (f"({self.tag}, {self.deep}, "
                f"{self.parent.tag if self.parent else empty}, "
                f"{self.content})")
