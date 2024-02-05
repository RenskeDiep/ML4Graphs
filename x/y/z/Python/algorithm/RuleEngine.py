import sys
import time
from collections import defaultdict
from typing import List, Set, Dict, Tuple
from x.y.z.Python.algorithm.data.Triple import Triple
from x.y.z.Python.algorithm.data.TripleSet import TripleSet
from x.y.z.Python.algorithm.structure import Rule, LinkedHashMapK
from x.y.z.Python.algorithm.structure.ScoreTree import ScoreTree
from x.y.z.Python.algorithm.io import RuleReader

class RuleEngine:
    COMBINATION_RULE_ID = 1
    EPSILON = 0.0001

    @classmethod
    def apply_rules_arx(cls, rules, test_set: TripleSet, training_set: TripleSet,
                        validation_set: TripleSet, k: int, results_writer):
        print("* Applying rules")
        relation2rules = cls.create_ordered_rule_index(rules)
        print(f"* Set up index structure covering rules for {len(relation2rules)} different relations")

        filter_set = TripleSet()
        filter_set.add_triple_set(training_set)
        filter_set.add_triple_set(validation_set)
        filter_set.add_triple_set(test_set)
        print(f"* Constructed filter set with {len(filter_set.triples)} triples")

        if len(filter_set.triples) == 0:
            print("WARNING: Using an empty filter set!")

        #head_candidate_cache = defaultdict(LinkedHashMapK)
        #tail_candidate_cache = defaultdict(LinkedHashMapK)
        head_candidate_cache = defaultdict(lambda: defaultdict(float))
        tail_candidate_cache = defaultdict(lambda: defaultdict(float))

        counter = 0
        start_time = time.time()
        current_time = 0

        ScoreTree.LOWER_BOUND = k
        ScoreTree.UPPER_BOUND = ScoreTree.LOWER_BOUND
        ScoreTree.EPSILON = cls.EPSILON

        for triple in test_set.triples:
            if counter % 50 == 0:
                print(f"* #{counter} Trying to guess the tail/head of {triple}")
                current_time = time.time()
                print(f"Elapsed (s) = {(current_time - start_time)}")

            counter += 1
            relation = triple.relation
            head = triple.head
            tail = triple.tail

            t_question = (relation, head)
            h_question = (relation, tail)

            k_tail_tree = ScoreTree()
            k_head_tree = ScoreTree()

            if relation in relation2rules:
                relevant_rules = relation2rules[relation]

                if t_question not in tail_candidate_cache:
                    for rule in relevant_rules:
                        if not k_tail_tree.fine():
                            tail_candidates = rule.compute_tail_results(head, training_set)
                            f_tail_candidates = cls.get_filtered_entities(filter_set, test_set, triple, tail_candidates, True)
                            k_tail_tree.add_values(rule.applied_confidence, f_tail_candidates)
                        else:
                            break

                if h_question not in head_candidate_cache:
                    for rule in relevant_rules:
                        if not k_head_tree.fine():
                            head_candidates = rule.compute_head_results(tail, training_set)
                            f_head_candidates = cls.get_filtered_entities(filter_set, test_set, triple, head_candidates, False)
                            k_head_tree.add_values(rule.applied_confidence, f_head_candidates)
                        else:
                            break

            k_tail_candidates = k_tail_tree.get_as_linked_list()
            k_head_candidates = k_head_tree.get_as_linked_list()

            k_tail_candidates = cls.sort_by_value(k_tail_candidates)
            k_head_candidates = cls.sort_by_value(k_head_candidates)

            cls.write_top_k_candidates(triple, test_set, k_head_candidates, k_tail_candidates, results_writer, k)

    @classmethod
    def create_ordered_rule_index(cls, rules):
        relation2rules = defaultdict(list)
        print("Rules: ,", rules)
        for rule in rules:
            print(rule)
            relation = rule.target_relation
            relation2rules[relation].append(rule)

        for relation, rules_list in relation2rules.items():
            rules_list.sort(key=lambda x: x.applied_confidence, reverse=True)

        return relation2rules

    @classmethod
    def get_filtered_entities(cls, filter_set: TripleSet, test_set: TripleSet, triple: Triple,
                              candidate_entities: Set[str], tail_not_head: bool) -> Set[str]:
        filtered_entities = set()

        for entity in candidate_entities:
            if not tail_not_head:
                if not filter_set.is_true(entity, triple.relation, triple.tail):
                    filtered_entities.add(entity)

                if test_set.is_true(entity, triple.relation, triple.tail):
                    if entity == triple.head:
                        filtered_entities.add(entity)

            if tail_not_head:
                if not filter_set.is_true(triple.head, triple.relation, entity):
                    filtered_entities.add(entity)

                if test_set.is_true(triple.head, triple.relation, entity):
                    if entity == triple.tail:
                        filtered_entities.add(entity)

        return filtered_entities

    @classmethod
    def write_top_k_candidates(cls, triple: Triple, test_set: TripleSet,
                               k_head_candidates: Dict[str, float], k_tail_candidates: Dict[str, float],
                               writer, k: int):
        writer.write(f"{triple}\n")

        writer.write("Heads: ")
        i = 0
        for candidate, confidence in k_head_candidates.items():
            if triple.head == candidate or not test_set.is_true(candidate, triple.relation, triple.tail):
                writer.write(f"{candidate}\t{confidence}\t")
                i += 1

            if i == k:
                break

        writer.write("\n")

        i = 0
        writer.write("Tails: ")
        for candidate, confidence in k_tail_candidates.items():
            if triple.tail == candidate or not test_set.is_true(triple.head, triple.relation, candidate):
                writer.write(f"{candidate}\t{confidence}\t")
                i += 1

            if i == k:
                break

        writer.write("\n")
        writer.flush()

    @classmethod
    def sort_by_value(cls, map: Dict[str, float]) -> Dict[str, float]:
        return dict(sorted(map.items(), key=lambda item: item[1], reverse=True))


if __name__ == "__main__":
    rules_file = "path/to/rules-file.txt"  # Provide the actual path to the rules file
    output_file = "path/to/output-file.txt"  # Provide the actual path to the output file

    rules = RuleReader.read(rules_file)
    test_set = TripleSet()  # Provide the test set
    training_set = TripleSet()  # Provide the training set
    validation_set = TripleSet()  # Provide the validation set

    k_value = 10  # Provide the desired value of k

    with open(output_file, "w") as results_writer:
        RuleEngine.apply_rules_arx(rules, test_set, training_set, validation_set, k_value, results_writer)
