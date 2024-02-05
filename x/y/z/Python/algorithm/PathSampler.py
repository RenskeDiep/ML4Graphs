import random
from x.y.z.Python.algorithm.data.TripleSet import TripleSet
from structure.Path import Path
from x.y.z.Python.algorithm.structure.Rule import Rule


class PathSampler:
    def __init__(self, triple_set):
        self.triple_set = triple_set
        self.rand = random.Random()

    def sample_path(self, steps, cyclic):
        nodes = [None] * (1 + steps * 2)
        markers = [''] * steps

        dice = self.rand.randint(0, len(self.triple_set.get_triples()) - 1)
        triple = self.triple_set.get_triples()[dice]

        if triple.head == triple.tail:
            return None

        if self.rand.random() < 0.5:
            markers[0] = '+'
            nodes[0] = triple.head
            nodes[1] = triple.relation
            nodes[2] = triple.tail
        else:
            markers[0] = '-'
            nodes[2] = triple.head
            nodes[1] = triple.relation
            nodes[0] = triple.tail

        index = 1
        while index < steps:
            if self.rand.random() < 0.5:
                candidate_triples = [t for t in self.triple_set.get_triples() if t.head == nodes[index * 2]]
                if not candidate_triples:
                    return None

                next_triple = random.choice(candidate_triples) if not cyclic or index + 1 != steps \
                    else random.choice([t for t in candidate_triples if t.tail == nodes[0]])

                nodes[index * 2 + 1] = next_triple.relation
                nodes[index * 2 + 2] = next_triple.tail
                markers[index] = '+'
            else:
                candidate_triples = [t for t in self.triple_set.get_triples() if t.tail == nodes[index * 2]]
                if not candidate_triples:
                    return None

                next_triple = random.choice(candidate_triples) if not cyclic or index + 1 != steps \
                    else random.choice([t for t in candidate_triples if t.head == nodes[0]])

                nodes[index * 2 + 1] = next_triple.relation
                nodes[index * 2 + 2] = next_triple.head
                markers[index] = '-'

            index += 1

        path = Path(nodes, markers)
        # Check if the path is valid (implement validation logic if needed)

        return path


# Main part
if __name__ == "__main__":
    ts = TripleSet("C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/train.txt")
    ps = PathSampler(ts)

    some_paths = set()

    for _ in range(1000):
        p = ps.sample_path(2, True)
        if p is not None:  # assuming validation logic is implemented in sample_path
            some_paths.add(p)

    print()
    print(f" *** Sampled {len(some_paths)} valid paths.")
    print()

