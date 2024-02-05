from typing import List, Set, Dict
from .Atom import Atom


class Rule:
    APPLICATION_MODE = False
    UNSEEN_NEGATIVE_EXAMPLES = 1

    def __init__(self, head=None):
        self.head = head
        self.body = []
        self.hashcode = 0
        self.hashcode_initialized = False
        self.predicted = 0
        self.correctly_predicted = 0
        self.confidence = 0.0
        self.next_free_variable = 0

    @classmethod
    def application_mode(cls):
        cls.APPLICATION_MODE = True

    def set_head(self, head):
        self.head = head

    def add_body_atom(self, atom):
        self.body.append(atom)

    def replace_nearly_all_constants_by_variables(self):
        counter = 0
        for atom in self.body:
            counter += 1
            if counter == len(self.body):
                break
            if atom.is_left_constant():
                c = atom.left
                self.replace_by_variable(c, Rule.variables[self.next_free_variable])
                self.next_free_variable += 1
            if atom.is_right_constant():
                c = atom.right
                self.replace_by_variable(c, Rule.variables[self.next_free_variable])
                self.next_free_variable += 1

    def replace_all_constants_by_variables(self):
        for atom in self.body:
            if atom.is_left_constant():
                c = atom.left
                self.replace_by_variable(c, Rule.variables[self.next_free_variable])
                self.next_free_variable += 1
            if atom.is_right_constant():
                c = atom.right
                self.replace_by_variable(c, Rule.variables[self.next_free_variable])
                self.next_free_variable += 1

    def create_copy(self):
        copy = Rule(self.head.create_copy())
        for body_literal in self.body:
            copy.body.append(body_literal.create_copy())
        copy.next_free_variable = self.next_free_variable
        return copy

    def replace_by_variable(self, constant, variable):
        count = self.head.replace_by_variable(constant, variable)
        for body_atom in self.body:
            bcount = body_atom.replace_by_variable(constant, variable)
            count += bcount
        return count

    def is_xy_rule(self):
        return not self.head.is_left_constant() and not self.head.is_right_constant()

    def is_x_rule(self):
        return self.is_xy_rule() or (not self.head.is_left_constant() if self.is_xy_rule() else False)

    def is_y_rule(self):
        return self.is_xy_rule() or (not self.head.is_right_constant() if self.is_xy_rule() else False)

    def __str__(self):
        sb = []
        sb.append(f"{self.predicted}\t")
        sb.append(f"{self.correctly_predicted}\t")
        sb.append(f"{self.confidence}\t")
        sb.append(str(self.head))
        sb.append(" <= ")
        for i, body_literal in enumerate(self.body[:-1]):
            sb.append(str(body_literal))
            sb.append(", ")
        sb.append(str(self.body[-1]))
        return "".join(sb)

    def __eq__(self, other):
        if not isinstance(other, Rule):
            return False
        if self.head == other.head:
            if len(self.body) == len(other.body):
                for i in range(len(self.body)):
                    if self.body[i] != other.body[i]:
                        return False
                return True
        return False

    def __hash__(self):
        if not self.hashcode_initialized:
            self.hashcode = self.calculate_hashcode()
            self.hashcode_initialized = True
        return self.hashcode

    def calculate_hashcode(self):
        prime = 31
        result = 1
        result = prime * result + hash(self.head)
        for atom in self.body:
            result = prime * result + hash(atom)
        return result


class RuleCreator:
    relations = []
    entity_number = 0
    variables = []

    @classmethod
    def initialize_variables(cls, max_variable):
        cls.variables = [f"V{i}" for i in range(max_variable + 1)]

    @classmethod
    def initialize_relations(cls, relations):
        cls.relations = relations

    @classmethod
    def initialize_entity_number(cls, entity_number):
        cls.entity_number = entity_number

    @classmethod
    def create_rule(cls, string):
        if string.startswith("xRule"):
            return RuleCreator.create_x_rule(string)
        elif string.startswith("yRule"):
            return RuleCreator.create_y_rule(string)
        elif string.startswith("xyRule"):
            return RuleCreator.create_xy_rule(string)
        return None

    @classmethod
    def create_x_rule(cls, string):
        parts = string.split("\t")
        head_str = parts[4]
        body_str = parts[6].strip()
        head = RuleCreator.create_atom(head_str)
        body_literals = RuleCreator.create_body_literals(body_str)
        return RuleCreator.create_rule_from_parts(head, body_literals)

    @classmethod
    def create_y_rule(cls, string):
        parts = string.split("\t")
        head_str = parts[4]
        body_str = parts[6].strip()
        head = RuleCreator.create_atom(head_str)
        body_literals = RuleCreator.create_body_literals(body_str)
        return RuleCreator.create_rule_from_parts(head, body_literals)

    @classmethod
    def create_xy_rule(cls, string):
        parts = string.split("\t")
        head_str = parts[5]
        body_str = parts[7].strip()
        head = RuleCreator.create_atom(head_str)
        body_literals = RuleCreator.create_body_literals(body_str)
        return RuleCreator.create_rule_from_parts(head, body_literals)

    @classmethod
    def create_rule_from_parts(cls, head, body_literals):
        rule = Rule(head)
        for body_literal in body_literals:
            rule.add_body_atom(body_literal)
        return rule

    @classmethod
    def create_atom(cls, string):
        parts = string.split(" ")
        left = parts[0]
        relation = parts[1]
        right = parts[2]
        left_constant = left.startswith("CONSTANT") or left.startswith("ENTITY")
        right_constant = right.startswith("CONSTANT") or right.startswith("ENTITY")
        return Atom(left, relation, right, left_constant, right_constant)

    @classmethod
    def create_body_literals(cls, string):
        literals = []
        parts = string.split(", ")
        for part in parts:
            literals.append(RuleCreator.create_atom(part))
        return literals
