from typing import List
from x.y.z.Python.algorithm.structure.Rule import Rule
from x.y.z.Python.algorithm import Apply

class RuleConfidenceComparator:
    def compare(self, o1: Rule, o2: Rule) -> int:
        prob1 = o1.getCorrectlyPredicted() / (o1.getPredicted() + Apply.UNSEEN_NEGATIVE_EXAMPLES)
        prob2 = o2.getCorrectlyPredicted() / (o2.getPredicted() + Apply.UNSEEN_NEGATIVE_EXAMPLES)

        if prob1 < prob2:
            return 1
        elif prob1 > prob2:
            return -1
        return 0


