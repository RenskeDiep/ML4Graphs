from typing import List, Set, Dict
from collections import OrderedDict

class ScoreTree:
    LOWER_BOUND = 10
    UPPER_BOUND = 10
    EPSILON = 0.0001

    def __init__(self):
        self.children = []
        self.score = 0.0
        self.stored_values = None
        self.num_of_values = 0
        self.index = 0
        self.root = True
        self.closed = False

    def __str__(self, indent=""):
        rep = ""
        closing_sign = "X" if self.closed else ""
        rep += f"{indent}{closing_sign} {self.score} [{self.index}]({self.num_of_values}) -> {{ "
        if self.stored_values:
            rep += ", ".join(self.stored_values)
        rep += "}\n"
        for child in self.children:
            rep += child.__str__(indent + "   ")
        return rep

    def print_set(self, ss, value_set):
        print(f"{ss}: {', '.join(value_set)}")

    def fine(self):
        if self.root and self.children and self.children[-1].index >= ScoreTree.LOWER_BOUND <= ScoreTree.UPPER_BOUND:
            return self.is_first_unique()
        return False

    def is_first_unique(self):
        tree = self
        while tree.children:
            tree = tree.children[0]
        return tree.closed

    def get_as_linked_list(self, score_map=None, ps=0, level=0):
        if self.children:
            for child in self.children:
                ps_updated = ps + ScoreTree.EPSILON ** (level - 1) * self.score if not self.root else 0
                child.get_as_linked_list(score_map, ps_updated, level + 1)

        if not self.root:
            ps_updated = ps + ScoreTree.EPSILON ** (level - 1) * self.score
            for v in self.stored_values:
                score_map[v] = ps_updated

    def add_values(self, score, values):
        self._add_values(score, values, 0)

    def _add_values(self, score, values, counter):
        for child in self.children:
            child._add_values(score, values, 0)

        touched = set()
        untouched = set()
        if not self.root:
            for stored_value in self.stored_values:
                if stored_value in values:
                    touched.add(stored_value)
                else:
                    untouched.add(stored_value)
            values.difference_update(touched)

        if touched and self.stored_values and len(touched) < len(self.stored_values):
            child_index = self.index - len(untouched)
            if child_index >= ScoreTree.LOWER_BOUND:
                self.stored_values = touched
                self.index = child_index
                self.num_of_values -= len(untouched)
            else:
                self.stored_values = untouched
                self.add_child(score, touched, child_index)

        if self.root and values and self.num_of_values < ScoreTree.LOWER_BOUND:
            self.add_child(score, values, self.num_of_values + len(values))
            self.num_of_values += len(values)

        if self.stored_values is None or len(self.stored_values) <= 1:
            c = all(child.closed for child in self.children)
            self.closed = c

    def add_child(self, score, values, child_index):
        child = ScoreTree()
        child.score = score
        child.stored_values = set(values)
        child.index = child_index
        self.children.append(child)

