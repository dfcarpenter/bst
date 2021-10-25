from collections import MutableMapping
import queue




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

    def __iter__(self):
        """Generate an iteration of the tree's elements."""
        for p in self.positions():                        # use same order as positions()
            yield p.element()            

    def depth(self, p):
        """Return the number of levels separating Position p from the root."""
        if self.is_root(p):
            return 0
        else:
            return 1 + self.depth(self.parent(p))

        
    
    def _height2(self, p):
        if self.is_leaf(p):
            return 0
        else:
            return 1 + max(self._height2(c) for c in self.children(p))
    
    

    def breadthfirst(self):
        """Generate a breadth-first iteration of the positions of the tree."""
        if not self.is_empty():
            q = queue.Queue()             # known positions not yet yielded
        q.enqueue(self.root())        # starting with the root
        while not q.is_empty():
            p = q.dequeue()             # remove from front of the queue
            yield p                          # report this position
            for c in self.children(p):
                q.enqueue(c)              # add children to back of queue


class BinaryTree(Tree):
    
    """Linked representation of a binary tree structure."""

  #-------------------------- nested _Node class --------------------------
    class _Node:
        """Lightweight, nonpublic class for storing a node."""
        __slots__ = '_element', '_parent', '_left', '_right' # streamline memory usage

        def __init__(self, element, parent=None, left=None, right=None):
            self._element = element
            self._parent = parent
            self._left = left
            self._right = right

    #-------------------------- nested Position class --------------------------
    class Position(BinaryTree.Position):
        """An abstraction representing the location of a single element."""

        def __init__(self, container, node):
            """Constructor should not be invoked by user."""
            self._container = container
            self._node = node

        def element(self):
            """Return the element stored at this Position."""
            return self._node._element

        def __eq__(self, other):
            """Return True if other is a Position representing the same location."""
            return type(other) is type(self) and other._node is self._node

    def sibling(self, p):
        """Return a Position representing p's sibling (or None if no sibling)."""
        parent = self.parent(p)
        if parent is None:                    # p must be the root
            return None                         # root has no sibling
        else:
            if p == self.left(parent):
                return self.right(parent)         # possibly None
            else:
                return self.left(parent)          # possibly None

    def children(self, p):
        """Generate an iteration of Positions representing p's children."""
        if self.left(p) is not None:
            yield self.left(p)
        if self.right(p) is not None:
            yield self.right(p)

    def inorder(self):
        """Generate an inorder iteration of positions in the tree."""
        if not self.is_empty():
            for p in self._subtree_inorder(self.root()):
                yield p

    def _subtree_inorder(self, p):
        """Generate an inorder iteration of positions in subtree rooted at p."""
        if self.left(p) is not None:          # if left child exists, traverse its subtree
            for other in self._subtree_inorder(self.left(p)):
                yield other
        yield p                               # visit p between its subtrees
        if self.right(p) is not None:         # if right child exists, traverse its subtree
            for other in self._subtree_inorder(self.right(p)):
                yield other

    # override inherited version to make inorder the default
    def positions(self):
        """Generate an iteration of the tree's positions."""
        return self.inorder()                 # make inorder the default
    def _validate(self, p):
        """Return associated node, if position is valid."""
        if not isinstance(p, self.Position):
            raise TypeError('p must be proper Position type')
        if p._container is not self:
            raise ValueError('p does not belong to this container')
        if p._node._parent is p._node:      # convention for deprecated nodes
            raise ValueError('p is no longer valid')
        return p._node

    def _make_position(self, node):
        """Return Position instance for given node (or None if no node)."""
        return self.Position(self, node) if node is not None else None

    #-------------------------- binary tree constructor --------------------------
    def __init__(self):
        """Create an initially empty binary tree."""
        self._root = None
        self._size = 0

    #-------------------------- public accessors --------------------------
    def __len__(self):
        """Return the total number of elements in the tree."""
        return self._size
    
    def root(self):
        """Return the root Position of the tree (or None if tree is empty)."""
        return self._make_position(self._root)

    def parent(self, p):
        """Return the Position of p's parent (or None if p is root)."""
        node = self._validate(p)
        return self._make_position(node._parent)

    def left(self, p):
        """Return the Position of p's left child (or None if no left child)."""
        node = self._validate(p)
        return self._make_position(node._left)

    def right(self, p):
        """Return the Position of p's right child (or None if no right child)."""
        node = self._validate(p)
        return self._make_position(node._right)

    def num_children(self, p):
        """Return the number of children of Position p."""
        node = self._validate(p)
        count = 0
        if node._left is not None:     # left child exists
            count += 1
        if node._right is not None:    # right child exists
            count += 1
        return count

    #-------------------------- nonpublic mutators --------------------------
    def _add_root(self, e):
        """Place element e at the root of an empty tree and return new Position.
        Raise ValueError if tree nonempty.
        """
        if self._root is not None:
            raise ValueError('Root exists')
        self._size = 1
        self._root = self._Node(e)
        return self._make_position(self._root)

    def _add_left(self, p, e):
        """Create a new left child for Position p, storing element e.
        Return the Position of new node.
        Raise ValueError if Position p is invalid or p already has a left child.
        """
        node = self._validate(p)
        if node._left is not None:
            raise ValueError('Left child exists')
        self._size += 1
        node._left = self._Node(e, node)                  # node is its parent
        return self._make_position(node._left)

    def _add_right(self, p, e):
        """Create a new right child for Position p, storing element e.
        Return the Position of new node.
        Raise ValueError if Position p is invalid or p already has a right child.
        """
        node = self._validate(p)
        if node._right is not None:
            raise ValueError('Right child exists')
        self._size += 1
        node._right = self._Node(e, node)                 # node is its parent
        return self._make_position(node._right)

    def _replace(self, p, e):
        """Replace the element at position p with e, and return old element."""
        node = self._validate(p)
        old = node._element
        node._element = e
        return old

    def _delete(self, p):
        """Delete the node at Position p, and replace it with its child, if any.
        Return the element that had been stored at Position p.
        Raise ValueError if Position p is invalid or p has two children.
        """
        node = self._validate(p)
        if self.num_children(p) == 2:
            raise ValueError('Position has two children')
        child = node._left if node._left else node._right  # might be None
        if child is not None:
            child._parent = node._parent   # child's grandparent becomes parent
        if node is self._root:
            self._root = child             # child becomes root
        else:
            parent = node._parent
        if node is parent._left:
            parent._left = child
        else:
            parent._right = child
        self._size -= 1
        node._parent = node              # convention for deprecated node
        return node._element
    
    def _attach(self, p, t1, t2):
        """Attach trees t1 and t2, respectively, as the left and right subtrees of the external Position p.
        As a side effect, set t1 and t2 to empty.
        Raise TypeError if trees t1 and t2 do not match type of this tree.
        Raise ValueError if Position p is invalid or not external.
        """
        node = self._validate(p)
        if not self.is_leaf(p):
            raise ValueError('position must be leaf')
        if not type(self) is type(t1) is type(t2):    # all 3 trees must be same type
            raise TypeError('Tree types must match')
        self._size += len(t1) + len(t2)
        if not t1.is_empty():         # attached t1 as left subtree of node
            t1._root._parent = node
        node._left = t1._root
        t1._root = None             # set t1 instance to empty
        t1._size = 0
        if not t2.is_empty():         # attached t2 as right subtree of node
            t2._root._parent = node
        node._right = t2._root
        t2._root = None             # set t2 instance to empty
        t2._size = 0



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


class BinarySearchTree(BinaryTree, MapBase):

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
    
    def __setitem__(self, k, v):
        if self.is_empty():
            leaf = self._add_root(self._Item(k,v))
        else:
            p = self._subtree_search(self.root(), k)
            if p.key() == k:
                p.element()._value = v
                self._rebalance_access(p)
                return
            else:
                item = self.Item(k,v)
                if p.key() < k:
                    leaf = self._add_right(p, item)
                else:
                    leaf = self._add_left(p, item)
        self._rebalance_insert(leaf)

    def __iter__(self):
        p = self.first()
        while p is not None:
            yield p.key()
            p = self.after(p)

    def delete(self, p):
        self._validate(p)
        if self.left(p) and self.right(p):
            replacement = self._subtree_last_position(self.left(p))
            self._replace(p, replacement.element())
            p = replacement 
        parent = self.parent(p)
        self._delete(p)
        self._rebalance_delete(parent)
    
    def __delitem__(self, k):
        if not self.is_empty():
            p = self._subtree.search(self.root(), k)
            if k == p.key():
                self.delete(p)
                return 
            self._rebalance_access(p)
        raise KeyError(f'Jey Error {repr(k)}')
    
    def _relink(self, parent, child, make_left_child):
        if make_left_child:
            parent._left = child
        else:
            parent._right = child
        if child is not None:
            child._parent = parent

    
    def _rotate(self, p):
        x = p._node
        y = x._parent
        z = y._parent
        if z is None:
            self._root = x
            x._parent = None
        else:
            self._relink(z,x,y == z._left)
        if x == y._left:
            self._relink(y,x, True)
            self._relink(x, y, False)
        else:
            self._relink(y, x._left, False)
            self._relink(x, y, True)

    def _restructure(self, x):
        y = self.parent(x)
        z = self.parent(y)
        if (x == self.right(y)) == (y == self.right(z)):
            self._rotate(y)
            return y
        else:
            self._rotate(x)
            self._rotate(x)
            return x
        
    def _rebalance_insert(self, p): pass
    def _rebalance_delete(self, p): pass
    def _rebalance_access(self, p): pass



class RedBlackTree(BinarySearchTree):
  """Sorted map implementation using a red-black tree."""

  #-------------------------- nested _Node class --------------------------
  class _Node(TreeMap._Node):
    """Node class for red-black tree maintains bit that denotes color."""
    __slots__ = '_red'     # add additional data member to the Node class

    def __init__(self, element, parent=None, left=None, right=None):
      super().__init__(element, parent, left, right)
      self._red = True     # new node red by default

  #------------------------- positional-based utility methods -------------------------
  # we consider a nonexistent child to be trivially black
  def _set_red(self, p): p._node._red = True
  def _set_black(self, p): p._node._red = False
  def _set_color(self, p, make_red): p._node._red = make_red
  def _is_red(self, p): return p is not None and p._node._red
  def _is_red_leaf(self, p): return self._is_red(p) and self.is_leaf(p)

  def _get_red_child(self, p):
    """Return a red child of p (or None if no such child)."""
    for child in (self.left(p), self.right(p)):
      if self._is_red(child):
        return child
    return None
  
  #------------------------- support for insertions -------------------------
  def _rebalance_insert(self, p):
    self._resolve_red(p)                         # new node is always red

  def _resolve_red(self, p):
    if self.is_root(p):
      self._set_black(p)                         # make root black
    else:
      parent = self.parent(p)
      if self._is_red(parent):                   # double red problem
        uncle = self.sibling(parent)
        if not self._is_red(uncle):              # Case 1: misshapen 4-node
          middle = self._restructure(p)          # do trinode restructuring
          self._set_black(middle)                # and then fix colors
          self._set_red(self.left(middle))
          self._set_red(self.right(middle))
        else:                                    # Case 2: overfull 5-node
          grand = self.parent(parent)            
          self._set_red(grand)                   # grandparent becomes red
          self._set_black(self.left(grand))      # its children become black
          self._set_black(self.right(grand))
          self._resolve_red(grand)               # recur at red grandparent
      
  #------------------------- support for deletions -------------------------
  def _rebalance_delete(self, p):
    if len(self) == 1:                                     
      self._set_black(self.root())  # special case: ensure that root is black
    elif p is not None:
      n = self.num_children(p)
      if n == 1:                    # deficit exists unless child is a red leaf
        c = next(self.children(p))
        if not self._is_red_leaf(c):
          self._fix_deficit(p, c)
      elif n == 2:                  # removed black node with red child
        if self._is_red_leaf(self.left(p)):
          self._set_black(self.left(p))
        else:
          self._set_black(self.right(p))

  def _fix_deficit(self, z, y):
    """Resolve black deficit at z, where y is the root of z's heavier subtree."""
    if not self._is_red(y): # y is black; will apply Case 1 or 2
      x = self._get_red_child(y)
      if x is not None: # Case 1: y is black and has red child x; do "transfer"
        old_color = self._is_red(z)
        middle = self._restructure(x)
        self._set_color(middle, old_color)   # middle gets old color of z
        self._set_black(self.left(middle))   # children become black
        self._set_black(self.right(middle))
      else: # Case 2: y is black, but no red children; recolor as "fusion"
        self._set_red(y)
        if self._is_red(z):
          self._set_black(z)                 # this resolves the problem
        elif not self.is_root(z):
          self._fix_deficit(self.parent(z), self.sibling(z)) # recur upward
    else: # Case 3: y is red; rotate misaligned 3-node and repeat
      self._rotate(y)
      self._set_black(y)
      self._set_red(z)
      if z == self.right(y):
        self._fix_deficit(z, self.left(z))
      else:
        self._fix_deficit(z, self.right(z))


class SplayTree(BinarySearchTree):
  """Sorted map implementation using a splay tree."""

  #--------------------------------- splay operation --------------------------------
  def _splay(self, p):
    while p != self.root():
      parent = self.parent(p)
      grand = self.parent(parent)
      if grand is None:
        # zig case
        self._rotate(p)
      elif (parent == self.left(grand)) == (p == self.left(parent)):
        # zig-zig case
        self._rotate(parent)             # move PARENT up
        self._rotate(p)                  # then move p up
      else:
        # zig-zag case
        self._rotate(p)                  # move p up
        self._rotate(p)                  # move p up again

  #---------------------------- override balancing hooks ----------------------------
  def _rebalance_insert(self, p):
    self._splay(p)

  def _rebalance_delete(self, p):
    if p is not None:
      self._splay(p)                     

  def _rebalance_access(self, p):
    self._splay(p)


        

    

        



    
        
            





                

                
        
    

