import os
from typing import List, Set, Dict, Any
from decimal import Decimal
from datetime import datetime
from random import randint
from structure.Rule import Rule
from x.y.z.Python.algorithm.structure.Path import Path
from PathSampler import PathSampler
from x.y.z.Python.algorithm.data.TripleSet import TripleSet
from x.y.z.Python.algorithm.io.IOHelper import IOHelper


class Learn:
    timeStamp = 0
    #CONFIG_FILE = "config-learn.properties"
    PATH_TRAINING = "x/y/z/Python/data/FB15/train.txt"
    PATH_OUTPUT = "x/y/z/Python/data/FB15/rules"
    SNAPSHOTS_AT = [10, 100]
    MAX_LENGTH_CYCLIC = 3
    MAX_LENGTH_ACYCLIC = 2
    SAMPLE_SIZE = 500
    TRIAL_SIZE = 1000000
    BATCH_TIME = 1000
    SATURATION = 0.99
    THRESHOLD_CORRECT_PREDICTIONS = 2
    THRESHOLD_CONFIDENCE = 0.00001

    @staticmethod
    def showElapsedMoreThan(duration, message):
        now = datetime.now().timestamp() * 1000
        elapsed = now - Learn.timeStamp
        if elapsed > duration:
            print(message + " required " + str(elapsed) + " millis!")

    @staticmethod
    def takeTime():
        Learn.timeStamp = datetime.now().timestamp() * 1000

    @staticmethod
    def store_rules(path, snapshot_counter, rules, log, last_cc, last_ac, elapsed_seconds):
        max_body_size = 10
        acyclic_counter = [0] * max_body_size
        cyclic_counter = [0] * max_body_size

        try:
            rule_file = open(f"{path}-{snapshot_counter}", "w")

            log.write("\n")
            log.write(f"rule file: {os.path.abspath(rule_file.name)}\n")
            print(f">>> Storing rules in file {os.path.abspath(rule_file.name)}")

            for rrules in rules:
                for r in rrules:
                    if r.bodysize() < max_body_size:
                        if r.is_xy_rule():
                            cyclic_counter[r.bodysize() - 1] += 1
                        else:
                            acyclic_counter[r.bodysize() - 1] += 1
                    rule_file.write(str(r) + "\n")

            rule_file.close()

            log.write("cyclic: ")
            for i in range(max_body_size):
                if cyclic_counter[i] == 0:
                    break
                log.write(f"{cyclic_counter[i]} | ")
            log.write(f"{last_cc * 100:.1f}%\n")

            log.write("acyclic: ")
            for i in range(max_body_size):
                if acyclic_counter[i] == 0:
                    break
                log.write(f"{acyclic_counter[i]} | ")
            log.write(f"{last_ac * 100:.1f}%\n")

            log.write(f"time planned: {snapshot_counter}s\n")
            log.write(f"time elapsed: {elapsed_seconds}s\n\n")
            log.flush()

        except IOError as e:
            print(f"Error while writing to file: {e}")

    @staticmethod
    def main(args):
        global PATH_TRAINING, PATH_OUTPUT#, CONFIG_FILE
        PATH_OUTPUT = "C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/rules"
        PATH_TRAINING = "C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/train.txt"

        prop = {}
        input_stream = None


        log = open(PATH_OUTPUT + "_log", "w")
        log.write("Logfile\n")
        log.write("~~~~~~~\n\n")

        index_start_time = datetime.now().timestamp() * 1000

        ts = TripleSet(PATH_TRAINING)
        ts.index_triples()
        ps = PathSampler(ts)

        path_counter = 0
        batch_counter = 0

        batch_previously_found_rules = 0
        batch_new_useful_rules = 0
        batch_rules = 0

        mine_cyclic_not_acyclic = False

        all_useful_rules = [set()]

        snapshot_index = 0

        rule_size_cyclic = 0
        rule_size_acyclic = 0

        last_cyclic_coverage = 0.0
        last_acyclic_coverage = 0.0

        index_end_time = datetime.now().timestamp() * 1000
        log.write("indexing dataset: " + PATH_TRAINING + "\n")
        log.write("time elapsed: " + str(index_end_time - index_start_time) + "ms\n\n")
        log.write(str(IOHelper.get_params()) + "\n")
        log.flush()

        start_time = datetime.now().timestamp() * 1000

        while True:
            rule_size = rule_size_cyclic if mine_cyclic_not_acyclic else rule_size_acyclic
            useful_rules = all_useful_rules[rule_size]

            time = datetime.now().timestamp() * 1000
            elapsed_seconds = int((time - start_time) / 1000)

            if elapsed_seconds > Learn.SNAPSHOTS_AT[snapshot_index]:
                Learn.store_rules(PATH_OUTPUT, Learn.SNAPSHOTS_AT[snapshot_index], all_useful_rules, log,
                                  last_cyclic_coverage, last_acyclic_coverage, elapsed_seconds)

                snapshot_index += 1
                print("CREATED SNAPSHOT " + str(snapshot_index) + " after " + str(elapsed_seconds) + " seconds")
                if snapshot_index == len(Learn.SNAPSHOTS_AT):
                    log.flush()
                    log.close()
                    print("Bye, bye")
                    exit(1)

            batch_start_time = datetime.now().timestamp() * 1000
            current_time = 0

            while True:
                current_time = datetime.now().timestamp() * 1000
                if current_time - batch_start_time > Learn.BATCH_TIME:
                    break

                path_counter += 1
                p = ps.sample_path(rule_size + 2, mine_cyclic_not_acyclic)

                if p is not None and p.is_valid():
                    #print(p)
                    pr = Rule(p)
                    #print("rule:", pr)
                    pr.path_to_atoms(p)
                    rules = pr.get_generalizations(mine_cyclic_not_acyclic)
                    #print("Gen rules: ", rules)

                    for r in rules:
                        #print("gen rs", r)
                        #print("head", r.head)
                        #print("body", r.body[0].left, r.body[0].relation, r.body[0].right)
                        if r.is_trivial():
                            continue

                        batch_rules += 1

                        if r not in useful_rules:
                            r.compute_scores(ts)
                            #print("Confidence", r.get_confidence())
                            if r.get_confidence() >= Learn.THRESHOLD_CONFIDENCE and \
                                    r.get_correctly_predicted() >= Learn.THRESHOLD_CORRECT_PREDICTIONS:
                                batch_new_useful_rules += 1
                                useful_rules.add(r)
                        else:
                            batch_previously_found_rules += 1

            batch_counter += 1
            type_str = "CYCLIC" if mine_cyclic_not_acyclic else "ACYCLIC"
            print(">>> ****** Batch [" + type_str + " " + str(rule_size + 1) + "] " + str(batch_counter) +
                  " (sampled " + str(path_counter) + " paths) *****")
            print("OLD", batch_previously_found_rules)
            print("NEW", batch_new_useful_rules)
            current_coverage = batch_previously_found_rules / (batch_new_useful_rules + batch_previously_found_rules)
            print(">>> fraction of previously seen rules within useful rules in this batch: " +
                  str(current_coverage) + " NEW=" + str(batch_new_useful_rules) + " PREV=" +
                  str(batch_previously_found_rules) + " ALL=" + str(batch_rules))
            print(">>> stored rules: " + str(len(useful_rules)))

            if mine_cyclic_not_acyclic:
                last_cyclic_coverage = current_coverage
            else:
                last_acyclic_coverage = current_coverage

            if current_coverage > Learn.SATURATION and batch_previously_found_rules > 1:
                rule_size += 1
                if mine_cyclic_not_acyclic:
                    rule_size_cyclic = rule_size
                else:
                    rule_size_acyclic = rule_size

                print(">>> ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
                print(">>> INCREASING RULE SIZE OF " + type_str + " RULE TO " + str(rule_size + 1))
                print(">>> ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                log.write("increasing rule size of " + type_str + " rules to " + str(rule_size + 1) +
                          " after " + str((start_time - datetime.now().timestamp() * 1000) / 1000) + "s\n\n")
                log.flush()
                all_useful_rules.append(set())

        batch_new_useful_rules = 0
        batch_rules = 0
        batch_previously_found_rules = 0

        mine_cyclic_not_acyclic = not mine_cyclic_not_acyclic

        if mine_cyclic_not_acyclic and rule_size_cyclic + 1 > Learn.MAX_LENGTH_CYCLIC:
            mine_cyclic_not_acyclic = False


if __name__ == "__main__":
    Learn.main([])
