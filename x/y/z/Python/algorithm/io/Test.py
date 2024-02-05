from rdflib import Graph, URIRef, Literal
from ..data.TripleSet import TripleSet


class Test:
    def main(self):
        training_set = TripleSet("../RuleN18/data/FB15-237/test.txt")

        print(len(training_set.get_entities()))
