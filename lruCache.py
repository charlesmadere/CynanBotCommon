from typing import Dict


class LinkedNode():

    def __init__(self, key: str):
        if key is None:
            raise ValueError(f'key argument is malformed: \"{key}\"')

        self.key: str = key
        self.next: LinkedNode = None
        self.prev: LinkedNode = None


class LRUCache():

    def __init__(self, capacity: int):
        if capacity < 0:
            raise ValueError(f'capacity argument is out of bounds: {capacity}')

        self.capacity = capacity
        self.lookup: Dict[str, LinkedNode] = dict()
        self.dummy = LinkedNode("dummy")
        self.head = self.dummy.next
        self.tail = self.dummy.next

    def __append_new_node(self, new_node: LinkedNode):
        """  add the new node to the tail end
        """
        if not self.tail:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = self.tail.next

    def contains(self, key: str) -> bool:
        if key is None or key not in self.lookup:
            return False

        node = self.lookup[key]

        if node is not self.tail:
            self.__unlink_cur_node(node)
            self.__append_new_node(node)

        return True

    def put(self, key: str):
        if key is None:
            raise ValueError(f'key argument is malformed: \"{key}\"')

        if key in self.lookup:
            self.contains(key)
            return

        if len(self.lookup) == self.capacity:
            # remove head node and corresponding key
            self.lookup.pop(self.head.key)
            self.__remove_head_node()

        # add new node and hash key
        new_node = LinkedNode(key = key)
        self.lookup[key] = new_node
        self.__append_new_node(new_node)

    def __remove_head_node(self):
        if not self.head:
            return
        prev = self.head
        self.head = self.head.next
        if self.head:
            self.head.prev = None
        del prev

    def __unlink_cur_node(self, node: LinkedNode):
        """ unlink current linked node
        """
        if self.head is node:
            self.head = node.next
            if node.next:
                node.next.prev = None
            return

        # removing the node from somewhere in the middle; update pointers
        prev, nex = node.prev, node.next
        prev.next = nex    
        nex.prev = prev
