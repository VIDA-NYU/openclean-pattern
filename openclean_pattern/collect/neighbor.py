# This file is part of the Pattern and Anomaly Detection Library (openclean_pattern).
#
# Copyright (C) 2021 New York University.
#
# openclean_pattern is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Collector class which clusters similar tokens and returns the clusters"""

from openclean_pattern.collect.base import Collector
from openclean_pattern.align.distance.factory import DistanceFactory
from openclean_pattern.align.distance.tree_edit import DISTANCE_TED
from openclean_pattern.align.base import Sequence
from openclean_pattern.align.needlemanwunsch import NeedlemanWunschAligner
from openclean.function.token.base import Token

import numpy as np
from skbio.tree import TreeNode
from skbio.io.format.newick import _tokenize_newick, NewickFormatError
from skbio import DistanceMatrix
from skbio.tree import nj

from typing import List, Optional, Dict, Tuple

COLLECT_NEIGHBOR = "neighbor"


def serialize(obj: TreeNode) -> str:
    """converts a skbio TreeNode to a str

    Parameters
    ----------
    obj: TreeNode
        the node to convert to a string
    """
    operators = set(",:_;()[]")
    current_depth = 0
    nodes_left = [(obj, 0)]
    fh = ''
    while len(nodes_left) > 0:
        entry = nodes_left.pop()
        node, node_depth = entry
        if node.children and node_depth >= current_depth:
            fh += '('
            nodes_left.append(entry)
            nodes_left += ((child, node_depth + 1) for child in
                           reversed(node.children))
            current_depth = node_depth + 1
        else:
            if node_depth < current_depth:
                fh += ')'
                current_depth -= 1

            # Note we don't check for None because there is no way to represent
            # an empty string as a label in Newick. Therefore, both None and ''
            # are considered to be the absence of a label.
            lblst = []
            if node.support is not None:  # prevents support of NoneType
                lblst.append(str(node.support))
            if node.name:  # prevents name of NoneType
                lblst.append(node.name)
            label = ':'.join(lblst)
            if label:
                escaped = "%s" % label.replace("'", "''")
                if any(t in operators for t in label):
                    fh += "'"
                    fh += escaped
                    fh += "'"
                else:
                    fh += escaped.replace(" ", "_")
            if nodes_left and nodes_left[-1][1] == current_depth:
                fh += ','

    fh += ';\n'
    return fh


def deserialize(st: str, words: Optional[List] = None, convert_underscores: bool = True) -> Tuple[TreeNode, List]:
    """read str to TreeNode and get nested list of operation order

    Parameters
    ----------
    st: str
        The string to recreate the tree from and extract an order of neighbors to be used as the guide tree. The
        guide tree is in the form of list of lists and tuples where an internal list represents an inner node and a
        tuple represents a pair to combine, e.g.:
            [['abc', ('aab','aac')],'xyz']
        for the tree:
                        --- 'xyz'
                    ---|     --- 'abc'
                        --- |   --- 'aab'
                            ---|
                                --- 'aac'
    words: list
        If the serialized tree was created using indices instead of labels, the original column can be passed in to return the
        exact values inside the order array
    convert_underscores: bool (default = True)
        flag to convert underscores as per the newick tokenizer
    """
    tree_stack = []
    current_depth = 0
    last_token = ''
    root = TreeNode()
    tree_stack.append((root, current_depth))
    next_is_distance = False

    combo = []
    my_stack = []
    my_stack.append((combo, current_depth))

    for token in _tokenize_newick(st, convert_underscores=convert_underscores):
        # Check for a label
        if last_token not in '(,):':
            val = Sequence(words[int(last_token)]) if words else int(last_token)
            if not next_is_distance:
                tree_stack[-1][0].name = val if last_token else None
            else:
                next_is_distance = False
            if last_token:
                my_stack[-1][0].append(val)
            else:
                my_stack[-1][0].append(None)

            # Check for a distance
        if token == ':':
            next_is_distance = True
        elif last_token == ':':
            try:
                tree_stack[-1][0].length = float(token)
            except ValueError:
                raise NewickFormatError("Could not read length as numeric type"
                                        ": %s." % token)
        elif token == '(':
            current_depth += 1
            tree_stack.append((TreeNode(), current_depth))
            my_stack.append((list(), current_depth))
        elif token == ',':
            tree_stack.append((TreeNode(), current_depth))
            my_stack.append((list(), current_depth))
        elif token == ')':
            if len(tree_stack) < 2:
                raise NewickFormatError("Could not parse file as newick."
                                        " Parenthesis are unbalanced.")
            children = []
            my_children = []
            # Pop all nodes at this depth as they belong to the remaining
            # node on the top of the stack as children.
            while current_depth == tree_stack[-1][1]:
                node, _ = tree_stack.pop()
                children.insert(0, node)
                nc, _ = my_stack.pop()
                [my_children.insert(0, c) for c in nc]
            parent = tree_stack[-1][0]
            my_parent = my_stack[-1][0]

            if parent.children:
                raise NewickFormatError("Could not parse file as newick."
                                        " Contains unnested children.")
            # This is much faster than TreeNode.extend
            for child in children:
                child.parent = parent
            parent.children = children

            my_parent.append(my_children)

            current_depth -= 1
        elif token == ';':
            if len(tree_stack) == 1:
                return root, my_stack
            break

        last_token = token

    raise NewickFormatError("Could not parse file as newick."
                            " `(Parenthesis)`, `'single-quotes'`,"
                            " `[comments]` may be unbalanced, or tree may be"
                            " missing its root.")


class NeighborJoin(Collector):
    """This collector creates groups based on the clustering of similarly distanced tokens"""

    def __init__(self):
        """intializes the collector object
        """
        super(NeighborJoin, self).__init__(COLLECT_NEIGHBOR)
        self.distance = DistanceFactory.create(DISTANCE_TED)
        self.distance.strict = False

    def _compute_pairwise_distance(self, column: List[List[Token]]) -> np.array:
        """Computes the levenshtein distance between aligned elements in the column
        output format:

        , A, B, C, D, E, F
        A, 0, 5, 4, 7, 6, 8
        B, 5, 0, 7,10, 9,11
        C, 4, 7, 0, 7, 6, 8
        D, 7,10, 7, 0, 5, 9
        E, 6, 9, 6, 5, 0, 8
        F, 8,11, 8, 9, 8, 0

        Parameters
        ----------
        column: list
            input values

        Returns
        -------
            matrix of pairwise distances in the form above

        """
        pairwise = NeedlemanWunschAligner()
        l = len(column)
        distances = np.empty((l, l))
        for u in range(l):
            # compute only half of the distances
            for v in range(u, l):
                au, av = pairwise.align([column[u], column[v]])  # get aligned
                distances[u][v] = distances[v][u] = self.distance.compute(au, av)

        return distances

    def get_tree_and_order(self, words: List[List[Token]]) -> Tuple[TreeNode, List]:
        """creates a nearest neighbor tree and returns a list of tuples in the form:
        [s1, (s2, s3), s4]
        depicting the different order of how they should be aligned

        Parameters
        ----------
        words: list
            list of inputs

        Returns
        -------
            tuple of TreeNode and Order
        """

        distances = self._compute_pairwise_distance(words)

        # create the tree with the indices of the rows instead of the actual values
        nw = list()
        [nw.append(str(i)) for i in range(len(words))]

        dm = DistanceMatrix(distances, nw)
        tree = nj(dm)

        tree, order = deserialize(serialize(tree), words)

        return tree, order[0]

    def collect(self, column: List[List[Token]]) -> Dict:
        """the collect method takes in a list of Tokens and collects the closest ones together. The returned
        object is a dict of lists with each inner list representing the tree of indices of nearest neighbors
         in the format for e.g. [[2, (3, 1)], 0]
        to represent the tree:
                        --- 0
                    ---|     --- 2
                        --- |   --- 3
                            ---|
                                --- 1

        Parameters
        ----------
        column: list of list[Token]
            the column to align

        Returns
        -------
             a dict of lists with key 'n' representing the cluster and each inner list representing row_indices of groups
             with n tokens / row_index of part of the cluster
       """
        distances = self._compute_pairwise_distance(column)

        # create the tree with the indices of the rows instead of the actual values
        nw = list()
        [nw.append(i) for i in range(len(column))]

        dm = DistanceMatrix(distances, nw)
        tree = nj(dm)

        _, order = deserialize(serialize(tree))

        return {0: order[0]}
