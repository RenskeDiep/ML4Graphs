import sys
from typing import List
from x.y.z.Python.algorithm.data.TripleSet import TripleSet
from x.y.z.Python.algorithm.eval import HitsAtK, ResultSet

PREDICTION_TYPE = "aRx"
PATH_TRAINING = "C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/train.txt"
PATH_TEST = "C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/test.txt"
PATH_VALID = "C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/valid.txt"
PATH_OUTPUT = "C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/rules-predictions.txt"


def compute_scores(rs, gold, hits_at_k):
    for t in gold.get_triples():
        cand1 = rs.get_head_candidates(str(t))
        c1 = cand1[0] if cand1 else "-"
        hits_at_k.evaluate_head(cand1, t)
        cand2 = rs.get_tail_candidates(str(t))
        c2 = cand2[0] if cand2 else "-"
        hits_at_k.evaluate_tail(cand2, t)

def main():

    training_set = TripleSet(PATH_TRAINING)
    validation_set = TripleSet(PATH_VALID)
    test_set = TripleSet(PATH_TEST)

    rs = ResultSet(PATH_OUTPUT, True, 10)

    hits_at_k = HitsAtK()
    hits_at_k.add_filter_triple_set(training_set)
    hits_at_k.add_filter_triple_set(validation_set)
    hits_at_k.add_filter_triple_set(test_set)

    compute_scores(rs, test_set, hits_at_k)

    print("\nHits@1   Hits@3    Hits@10")
    print(hits_at_k.get_hits_at_k(0), hits_at_k.get_hits_at_k(2), hits_at_k.get_hits_at_k(9))


if __name__ == "__main__":
    main()
