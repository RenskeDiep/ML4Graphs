from typing import List
from collections import Counter

class Path:
    def __init__(self, nodes: List[str], markers: List[str]):
        self.nodes = nodes
        self.markers = markers

    def __str__(self):
        path_str = " -> ".join(self.marked_node_to_string(i) for i in range(len(self.nodes)))
        return path_str

    def marked_node_to_string(self, i):
        if i % 2 == 1:
            return f"{self.markers[(i-1) // 2]}{self.nodes[i]}"
        else:
            return self.nodes[i]

    def __eq__(self, other):
        if not isinstance(other, Path):
            return False
        return self.nodes == other.nodes and self.markers == other.markers

    def __hash__(self):
        return hash((tuple(self.nodes), tuple(self.markers)))

    def is_valid(self):
        xconst = self.nodes[0]
        yconst = self.nodes[2]
        visited_entities = set()

        for i in range(4, len(self.nodes)-2, 2):
            if self.nodes[i] == xconst or self.nodes[i] == yconst:
                return False

        for i in range(2, len(self.nodes), 2):
            if self.nodes[i] in visited_entities:
                return False
            visited_entities.add(self.nodes[i])

        return True

    def is_cyclic(self):
        return self.nodes[-1] == self.nodes[0] or self.nodes[-1] == self.nodes[2]

