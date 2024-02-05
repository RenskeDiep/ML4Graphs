import os
import codecs
from typing import List


class CompletionResult:
    def __init__(self, triple):
        self.triple = triple
        self.head_results = []
        self.tail_results = []

    def add_head_results(self, heads, k):
        if k > 0:
            self.add_results(heads, self.head_results, k)
        else:
            self.add_results(heads, self.head_results)

    def add_tail_results(self, tails, k):
        if k > 0:
            self.add_results(tails, self.tail_results, k)
        else:
            self.add_results(tails, self.tail_results)

    def add_results(self, candidates, results, k):
        for c in candidates:
            if c != "":
                results.append(c)
                k -= 1
                if k == 0:
                    return

    def get_heads(self):
        return self.head_results

    def get_tails(self):
        return self.tail_results


class ResultSet:
    apply_threshold = False
    threshold = 0.0

    def __init__(self, name, file_path, contains_confidences, k):
        print("* loading result set at " + file_path)
        self.contains_confidences = contains_confidences
        self.name = name
        self.results = {}
        try:
            with codecs.open(file_path, 'r', 'utf-8') as file:
                for triple_line in file:
                    if len(triple_line) < 3:
                        continue
                    cr = CompletionResult(triple_line)
                    head_line = file.readline()
                    tail_line = file.readline()
                    temp_line = ""
                    if head_line.startswith("Tails:"):
                        print("reversed")
                        temp_line = head_line
                        head_line = tail_line
                        tail_line = temp_line
                    if not ResultSet.apply_threshold:
                        cr.add_head_results(self.get_results_from_line(head_line[7:]), k)
                        cr.add_tail_results(self.get_results_from_line(tail_line[7:]), k)
                    else:
                        cr.add_head_results(self.get_thresholded_results_from_line(head_line[7:]), k)
                        cr.add_tail_results(self.get_thresholded_results_from_line(tail_line[7:]), k)
                    self.results[triple_line.split("\t")[0]] = cr
        except IOError as e:
            print(e)

    def get_thresholded_results_from_line(self, r_line):
        if not self.contains_confidences:
            return r_line.split("\t")
        else:
            t = ""
            c_s = ""
            token = r_line.split("\t")
            token_x = []
            for i in range(0, len(token)//2):
                t = token[i*2]
                c_s = token[i*2 + 1]
                c = float(c_s)
                if c > ResultSet.threshold:
                    token_x.append(t)
                else:
                    break
            return token_x

    def get_results_from_line(self, r_line):
        if not self.contains_confidences:
            return r_line.split("\t")
        else:
            token = r_line.split("\t")
            token_x = [token[i*2] for i in range(len(token)//2)]
            return token_x

    def get_head_candidates(self, triple):
        try:
            cr = self.results[triple]
            return cr.get_heads()
        except KeyError:
            return []

    def get_tail_candidates(self, triple):
        try:
            cr = self.results[triple]
            return cr.get_tails()
        except KeyError:
            return []

    def get_name(self):
        return self.name
