import os
from typing import List
import time
from x.y.z.Python.algorithm.data.TripleSet import TripleSet
from x.y.z.Python.algorithm.io.IOHelper import IOHelper
from x.y.z.Python.algorithm.io.RuleReader import RuleReader
from x.y.z.Python.algorithm.structure.Rule import Rule
from x.y.z.Python.algorithm.RuleEngine import RuleEngine


#CONFIG_FILE = "config-apply.properties"


THRESHOLD_CORRECT_PREDICTIONS = 2
THRESHOLD_CONFIDENCE = 0.00001




PREDICTION_TYPE = "aRx"
PATH_TRAINING = "C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/train.txt"
PATH_TEST = "C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/test.txt"
PATH_VALID = "C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/valid.txt"
PATH_RULES = "C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/rules-10"
PATH_OUTPUT = "C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/rules-predictions.txt"
TOP_K_OUTPUT = 10
UNSEEN_NEGATIVE_EXAMPLES = 5
DISCRIMINATION_BOUND = 1000
TRIAL_SIZE = 100000
COMBINATION_RULE = "maxplus"
FILTER = True


def main():
    global CONFIG_FILE, PREDICTION_TYPE, PATH_TRAINING, PATH_TEST, PATH_VALID, PATH_OUTPUT, PATH_RULES, \
        TOP_K_OUTPUT, UNSEEN_NEGATIVE_EXAMPLES, DISCRIMINATION_BOUND, TRIAL_SIZE, COMBINATION_RULE, FILTER

    if PREDICTION_TYPE == "aRx":

        if COMBINATION_RULE == "multiplication":
            RuleEngine.COMBINATION_RULE_ID = 1
        elif COMBINATION_RULE == "maxplus":
            RuleEngine.COMBINATION_RULE_ID = 2
        elif COMBINATION_RULE == "max":
            RuleEngine.COMBINATION_RULE_ID = 3

        values = get_multiprocessing(PATH_RULES)
        log_file = None
        if values[0] == 0:
            log_file = open(PATH_RULES + "_plog", "w")
        else:
            log_file = open(PATH_OUTPUT.replace("|", "") + "_plog", "w")

        log_file.write("Logfile\n")
        log_file.write("~~~~~~~\n\n")
        log_file.write(IOHelper.get_params())
        log_file.flush()

        for value in values:
            start_time = int(time.time() * 1000)

            path_output_used = None
            path_rules_used = None

            if value == 0:
                path_output_used = PATH_OUTPUT
                path_rules_used = PATH_RULES
            elif value > 0:
                path_output_used = PATH_OUTPUT.replace("|.*|", str(value))
                path_rules_used = PATH_RULES.replace("|.*|", str(value))

            log_file.write("rules:   " + path_rules_used + "\n")
            log_file.write("output: " + path_output_used + "\n")
            log_file.flush()

            pw = open(path_output_used, "w")
            training_set = TripleSet(PATH_TRAINING)
            test_set = TripleSet(PATH_TEST)
            valid_set = TripleSet(PATH_VALID)
            rr = RuleReader()
            rules = rr.read(path_rules_used)
            print("* read rules", len(rules), "from file")
            rules_size = len(rules)
            RuleEngine.apply_rules_arx(rules, test_set, training_set, valid_set, TOP_K_OUTPUT, pw)

            end_time = int(time.time() * 1000)
            print("* evaluated", rules_size, "rules to propose candidates for", len(test_set.get_triples()) * 2, "completion tasks")
            print("* finished in", end_time - start_time, "ms.\n")

            log_file.write("finished in " + str((end_time - start_time) / 1000) + "s.\n\n")
            log_file.flush()

        log_file.close()

    else:
        print("The prediction type", PREDICTION_TYPE, "is not yet supported.")
        os.sys.exit(1)


def show_rules_stats(rules: List[Rule]):
    xy_counter = 0
    x_counter = 0
    y_counter = 0

    for rule in rules:
        if rule.is_xy_rule():
            xy_counter += 1
        if rule.is_x_rule():
            x_counter += 1
        if rule.is_y_rule():
            y_counter += 1

    print("XY =", xy_counter, "X =", x_counter, "Y =", y_counter)


def get_multiprocessing(path1: str) -> List[int]:
    token = path1.split("|")

    if len(token) < 2:
        return [0]
    else:
        numbers = token[1].split(",")
        return [int(n) for n in numbers]


if __name__ == "__main__":
    main()
