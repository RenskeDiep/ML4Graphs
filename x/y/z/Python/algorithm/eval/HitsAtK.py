from typing import List, Tuple, Dict
import math
import numpy as np
from ..data.Triple import Triple
from ..data.TripleSet import TripleSet


class HitsAtK:
    def __init__(self):
        self.filter_sets = []
        self.at_k_max = 100

        self.hits_adn_tail = np.zeros(self.at_k_max)
        self.hits_adn_tail_filtered = np.zeros(self.at_k_max)
        self.counter_tail = 0
        self.counter_tail_covered = 0

        self.head_ranks = []
        self.tail_ranks = []

        self.hits_adn_head = np.zeros(self.at_k_max)
        self.hits_adn_head_filtered = np.zeros(self.at_k_max)
        self.counter_head = 0
        self.counter_head_covered = 0

    def reset(self):
        # reset head
        self.hits_adn_head = np.zeros(self.at_k_max)
        self.hits_adn_head_filtered = np.zeros(self.at_k_max)
        self.counter_head = 0
        self.counter_head_covered = 0
        # reset tail
        self.hits_adn_tail = np.zeros(self.at_k_max)
        self.hits_adn_tail_filtered = np.zeros(self.at_k_max)
        self.counter_tail = 0
        self.counter_tail_covered = 0

        self.head_ranks = []
        self.tail_ranks = []

    def get_hits_at_k(self, k):
        hits_at_k = (self.hits_adn_head_filtered[k] + self.hits_adn_tail_filtered[k]) / (self.counter_head + self.counter_tail)
        return f"{hits_at_k:.4f}"

    def get_hits_at_k_double(self, k):
        return (self.hits_adn_head_filtered[k] + self.hits_adn_tail_filtered[k]) / (self.counter_head + self.counter_tail)

    def evaluate_head(self):
        self.counter_head += 1

    def evaluate_tail(self):
        self.counter_tail += 1

    def evaluate_head_candidates(self, candidates: List[str], triple) -> int:
        found_at = -1
        self.counter_head += 1
        if candidates:
            self.counter_head_covered += 1

        filter_count = 0
        for rank, candidate in enumerate(candidates[:self.at_k_max]):
            if candidate == triple.get_head():
                for index in range(rank, self.at_k_max):
                    self.hits_adn_head[index] += 1
                    self.hits_adn_head_filtered[index - filter_count] += 1
                found_at = rank + 1
                break
            else:
                for filter_set in self.filter_sets:
                    if filter_set.is_true(candidate, triple.get_relation(), triple.get_tail()):
                        filter_count += 1
                        break

        counter = 0
        ranked = False
        for candidate in candidates:
            counter += 1
            if candidate == triple.get_head():
                self.head_ranks.append(counter)
                ranked = True
                break
        if not ranked:
            self.head_ranks.append(-1)

        return found_at

    def evaluate_tail_candidates(self, candidates: List[str], triple) -> int:
        found_at = -1
        self.counter_tail += 1
        if candidates:
            self.counter_tail_covered += 1

        filter_count = 0
        for rank, candidate in enumerate(candidates[:self.at_k_max]):
            if candidate == triple.get_tail():
                for index in range(rank, self.at_k_max):
                    self.hits_adn_tail[index] += 1
                    self.hits_adn_tail_filtered[index - filter_count] += 1
                found_at = rank + 1
                break
            else:
                for filter_set in self.filter_sets:
                    if filter_set.is_true(triple.get_head(), triple.get_relation(), candidate):
                        filter_count += 1
                        break

        counter = 0
        ranked = False
        for candidate in candidates:
            counter += 1
            if candidate == triple.get_tail():
                self.tail_ranks.append(counter)
                ranked = True
                break
        if not ranked:
            self.tail_ranks.append(-1)

        return found_at

    def __str__(self):
        result = "evaluation result\n"
        result += "hits@k\traw\t\t\tfilter\n"
        result += "hits@k\ttail\thead\ttotal\ttail\thead\ttotal\n"

        for i in range(self.at_k_max):
            result += f"{i + 1}\t"
            result += f"{self._format_fraction(self.hits_adn_tail[i], self.counter_tail)}\t"
            result += f"{self._format_fraction(self.hits_adn_head[i], self.counter_head)}\t"
            result += f"{self._format_fraction(self.hits_adn_head[i] + self.hits_adn_tail[i], self.counter_head + self.counter_tail)}\t"
            result += f"{self._format_fraction(self.hits_adn_tail_filtered[i], self.counter_tail)}\t"
            result += f"{self._format_fraction(self.hits_adn_head_filtered[i], self.counter_head)}\t"
            result += f"{self._format_fraction(self.hits_adn_head_filtered[i] + self.hits_adn_tail_filtered[i], self.counter_head + self.counter_tail)}\n"

        result += f"counterHead={self.counter_head} counterTail={self.counter_tail} hits@10Tail={self.hits_adn_tail[self.at_k_max - 1]} hits@10Head={self.hits_adn_head[self.at_k_max - 1]}\n"
        result += f"counterHead={self.counter_head} counterTail={self.counter_tail} hits@10TailFiltered={self.hits_adn_tail_filtered[self.at_k_max - 1]} hits@10HeadFiltered={self.hits_adn_head_filtered[self.at_k_max - 1]}\n"
        result += f"fraction of head covered by rules  = {self.counter_head_covered / self.counter_head:.4f}\n"
        result += f"fraction of tails covered by rules = {self.counter_tail_covered / self.counter_tail:.4f}\n"

        return result

    @staticmethod
    def _format_fraction(numerator, denominator):
        return f"{numerator / denominator:.4f}" if denominator != 0 else "N/A"

    @staticmethod
    def f(value):
        return f"{value:.4f}"

    @staticmethod
    def sort_by_value(d: Dict):
        return dict(sorted(d.items(), key=lambda item: item[1], reverse=True))


