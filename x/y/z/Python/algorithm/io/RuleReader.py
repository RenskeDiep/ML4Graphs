import re
from ..structure.Atom import Atom
from ..structure.Rule import Rule


class RuleReader:
    def read(self, filepath):
        rules = []
        ids2rules = {}
        print(filepath)
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                print("line", line)
                if not line or line.startswith("#"):
                    continue
                rule = self.get_rule(line, ids2rules)
                if rule:
                    rules.append(rule)
        return rules


    def get_rule(self, line: str, id2rules: dict) -> Rule:
        tokens = line.strip().split("\t")
        if len(tokens) != 4:
            return None

        rule_id, length, score = map(int, tokens[:3])
        rule = Rule(rule_id, length, score)

        atoms = tokens[3].split(" ")
        rule.set_head(Atom(atoms[0]))
        for i in range(2, len(atoms)):
            rule.add_body_atom(Atom(atoms[i]))

        return rule



