from typing import List, Dict, Set
from Atom import Atom
from Rule import Rule
import io

class RuleFilter:
    countOneElement = 0
    countMoreElement = 0
    countConst = 0
    countVar = 0

    @staticmethod
    def filter(ruleList: List[Rule], log: io.TextIOBase) -> List[Rule]:
        print(">>> removing redundant rules ")
        allRules: Dict[Atom, List[Rule]] = {}

        for r1 in ruleList:
            if r1.isXRule() or r1.isYRule():
                b = []
                allRules[r1.head] = b

        for r1 in ruleList:
            if r1.head in allRules:
                allRules[r1.head].append(r1)

        rulesFiltered = RuleFilter.removeConst(allRules)
        filteredRules = [rule for ruleSet in rulesFiltered.values() for rule in ruleSet]

        for r in ruleList:
            if r.isXYRule():
                filteredRules.append(r)

        print(f"* before={len(ruleList)}   after={len(filteredRules)}")
        log.write(f"filtering: before={len(ruleList)}   after={len(filteredRules)}\n")
        log.flush()

        return filteredRules

    @staticmethod
    def removeConst(allRules: Dict[Atom, List[Rule]]) -> Dict[Atom, Set[Rule]]:
        newRules: Dict[Atom, Set[Rule]] = {}
        ergOld = 0
        ergNew = 0

        for h in allRules.keys():
            ergOld += len(allRules[h])
            rulesN = set()

            for i in range(len(allRules[h])):
                inside = False
                for j in range(len(allRules[h])):
                    if i != j:
                        if RuleFilter.special(allRules[h][j], allRules[h][i]):
                            if allRules[h][i].bodysize() > 1 and not inside:
                                RuleFilter.countMoreElement += 1
                            if allRules[h][i].bodysize() == 1 and not inside:
                                RuleFilter.countOneElement += 1
                            if allRules[h][i].hasConstantInBody():
                                RuleFilter.countConst += 1
                            else:
                                RuleFilter.countVar += 1
                            inside = True
                            break
                if not inside:
                    rulesN.add(allRules[h][i])

            newRules[h] = rulesN

        for a in newRules.keys():
            ergNew += len(newRules[a])

        return newRules

    @staticmethod
    def special(r1: Rule, r2: Rule) -> bool:
        if r1.bodysize() > r2.bodysize():
            return False

        if r1.hasConstantInBody():
            return False

        if r1.getAppliedConfidence() < r2.getAppliedConfidence():
            return False

        if r1.bodysize() == r2.bodysize():
            for i in range(r2.bodysize() - 1):
                if r1.body[i] != r2.body[i]:
                    return False

            if r1.body[-1].getRelation() == r2.body[-1].getRelation():
                if r1.body[-1].getLeft() != r2.body[-1].getLeft() and r1.body[-1].getRight() != r2.body[-1].getRight():
                    return False
            elif r1.body[-1].getRelation() != r2.body[-1].getRelation():
                return False
        elif r1.bodysize() < r2.bodysize():
            for i in range(r1.bodysize()):
                if r1.body[i] != r2.body[i]:
                    return False

        return True

    @staticmethod
    def sameRel(regel: Set[Rule]) -> int:
        s1 = set()
        for r in regel:
            for a in r.body:
                s1.add(a.getRelation())
        return len(s1)

    @staticmethod
    def sameRel(regel: List[Rule]) -> int:
        s1 = set()
        for r in regel:
            for a in r.body:
                s1.add(a.getRelation())
        return len(s1)

    @staticmethod
    def zweierRegel(regel: List[Rule]) -> bool:
        for r in regel:
            if r.bodysize() > 1:
                return True
        return False

    @staticmethod
    def zweierRegel(regel: Set[Rule]) -> bool:
        for r in regel:
            if r.bodysize() > 1:
                return True
        return False
