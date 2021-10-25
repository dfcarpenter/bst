from collections import MutableMapping

class Tree:

    class Position:
        def element(self):
            raise NotImplementedError('must be implemented by subclass')

        def __eq__(self, other):
            raise NotImplementedError('must be implemented by subclass')

        def __ne__(self, other):
            return not (self == other)
    
    def root(self):
        raise NotImplementedError('must be implemented by subclass')
    
    def parent(self, p):
        raise NotImplementedError('must be implemented by subclass')

    def num_children(self, p):
        raise NotImplementedError('must be implemented by subclass')
    
    def children(self, p):
        raise NotImplementedError('must be implemented by subclass')
    
    def __len__(self):
        raise NotImplementedError('must be implemented by subclass')
    
    def is_root(self, p):
        return self.root() == p
    
    def is_leaf(self, p):
        return self.num_children(p) == 0
    
    def is_empty(self):
        return len(self) == 0
    
    def _height2(self, p):
        if self.is_leaf(p):
            return 0
        else:
            return 1 + max(self._height2(c) for c in self.children(p))

def BinaryTree(Tree):
    
    def left(self, p):
        raise NotImplementedError("must be implemented by subclass")

    def right(self, p):
        raise NotImplementedError("must be implemented by subclass")

    def sibling(self, p):
        parent = self.parent(p)
        if parent is None:
            return None
        else:
            if p == self.left(parent):
                return self.right(parent)
            else:
                return self.left(parent)
    
    def children(self, p):
        if self.left(p) is not None:
            yield self.left(p)
        if self.right(p) is not None:
            yield self.right(p)



class LinkedBinaryTree(BinartTree):

    class Node:
        __slots__ = '_data', '_parent', '_left', '_right'

        def __init__(self, data, parent=None, left=None, right=None):
            self._data = data
            self._parent = parent
            self._left = left
            self._right = right
        
    class Position(BinaryTree.Position):

        def __init__(self, container, node):
            self._container = container
            self._node = node
        
        def data(self):
            return self._node._data
        
        def __eq__(self, other):
            return type(other) is type(self) and other._node is self._node 

    def _validate(self, p):
        if not isinstance(p, self.Position):
            raise TypeError('p must be proper position type')
        if p._container is not self:
            raise ValueError('p does not belong to this container')
        if p._node._parent is p._node:
            raise ValueError('p is no longer valid')
    
    def _make_position(self, node: Node) -> Position:
        return self.Position(self, node) if node is not None else None

    # ---- Binary tree constructor 
    def __init__(self):
        self._root = None
        self._size = 0

    def __len__(self):
        return self._size
    
    def root(self):
        return self._make_position(self._root)
    
    def parent(self, p):
        node = self._validate(p)
        return self._make_position(node._parent)
    
    def left(self, p):
        node = self._validate(p)
        return self._make_position(node._left)
    
    def right(self, p):
        node = self._validate(p)
        return self._make_position(node._right)
    
    def num_children(self, p):
        node = self._validate(p)
        count = 0
        if node._left is not None:
            count += 1
        if node._right is not None:
            count += 1
        return count
    

    def _add_root(self, data):
        if self._root is not None: raise ValueError('Root exists')
        self._size = 1
        self._root = self._Node(data)
        return self._make_position(self._root)
    
    def _add_left(self, p: Position, data):
        node = self._validate(p)
        if node._left is not None: raise ValueError('Left child exists')
        self._size += 1
        node._left = self._Node(data, node)
        return self._make_position(node._left)

    def _add_right(self, p: Position, data):
        node = self._validate(p)
        if node._right is not None: raise ValueError('Right child exists')
        self._size += 1
        node._right = self._Node(data, node)
        return self._make_position(node._right)
    
    def _replace(self, p: Position, data):
        node = self._validate(p)
        old = node._data
        node._data = data
        return old 

    
class MapBase(MutableMapping):
    class _Item:
        __slots__ = '_key', '_value'

        def __init__(self, k, v):
            self._key = k
            self._value = v

        def __eq__(self, other):
            return self._key == other._key
        
        def __ne__(self, other):
            return not (self == other)
        
        def __lt__(self, other):
            return self._key < other._key


class TreeMap(LinkedBinaryTree, MapBase):

    class Position(LinkedBinaryTree.Position):
        def key(self):
            return self.element()._key
        
        def value(self):
            return self.element()._value

    
    def _subtree_search(self, p, k):

        if k == p.key():
            return p
        elif k < p.key():
            if self.left(p) is not None:
                return self._subtree_search(self.left(p), k)
        else:
            if self.right(p) is not None:
                return self._subtree_search(self.right(p), k)
        return p 
    
    def _subtree_first_position(self, p):
        walk = p
        while self.left(walk) is not None:
            walk = self.left(walk)
        return walk
    
    def _subtree_last_position(self, p):

        walk = p
        while self.right(walk) is not None:
            walk = self.right(walk)
        return walk 
    
    def first(self):
        return self._subtree_first_position(self.root()) if len(self) > 0 else None

    def last(self):
        return self._subtree_last_position(self.root()) if len(self) > 0 else None
    
    def before(self, p):

        self._validate(p)
        if self.left(p):
            return self._subtree_last_position(self.left(p))
        else:
            # walk upward
            walk = p
            above = self.parent(walk)
            while above is not None and walk == self.left(above):
                walk = above
                above = self.parent(walk)
            return above

    
    def after(self, p):

        self._validate(p)
        
        if self.right(p):
            return self._subtree_last_position(self.right(p))
        else:
            # walk upward
            walk = p
            above = self.parent(walk)
            while above is not None and walk == self.right(above):
                walk = above
                above = self.parent(walk)
            return above
    
    
    def find_position(self, k):
        if self.is_empty():
            return None
        else:
            p = self._subtree_search(self.root(), k)
            self._rebalance_access(p)
            return p
    
    def find_min(self):
        if self.is_empty():
            return None
        else:
            p = self.first()
            return (p.key(), p.value())
    
    def find_ge(self, k):

        if self.is_empty():
            return None
        else:
            p = self.find_position(k)
            if p.key() < k:
                p = self.after(p)
            return (p.key(), p.value()) if p is not None else None

    def find_range(self, start, stop):
        """
        Iterate all (key,value) pairs such that start <= key < stop

        """

        if not self.is_empty():
            if start is None:
                p = self.first()
            else:
                p = self.find_position(start)
                if p.key() < start:
                    p = self.after(p)
            while p is not None and (stop is None or p.key() < stop):
                yield (p.key(), p.value())
                p = self.after()
            
    def __getitem__(self, k):

        if self.is_empty():
            raise KeyError(f'Key Error: {repr(k)}')
        else:
            p = self._subtree_search(self.root(), k)
            self._rebalance_access(p)
            if k != p.key():
                raise KeyError(f'Key Error: {repr(k)}')
            return p.value()
    

        



    
        
            





                

                
        
    

