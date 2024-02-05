from typing import List, Set, Dict
from x.y.z.Python.algorithm.structure.Atom import Atom
from x.y.z.Python.algorithm.data.SampledPairedResultSet import SampledPairedResultSet
from x.y.z.Python.algorithm.structure.Counter import Counter
from x.y.z.Python.algorithm.data.Triple import Triple
from x.y.z.Python.algorithm.data.TripleSet import TripleSet
#from x.y.z.Python.algorithm.io.RuleReader import RuleReader

class Rule:
    def __init__(self, head=None):
        self.head = head
        self.body = []
        self.hashcode = 0
        self.hashcode_initialized = False
        self.predicted = 0
        self.correctly_predicted = 0
        self.confidence = 0.0
        self.application_mode = False
        self.variables = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"]
        self.next_free_variable = 0
        self.APPLICATION_MODE = False

    def path_to_atoms(self, p):
        #print(p)
        #print("markers:", p.markers)
        if p.markers[0] == '+':
            self.head = Atom(p.nodes[0], p.nodes[1], p.nodes[2], True, True)
        else:
            self.head = Atom(p.nodes[2], p.nodes[1], p.nodes[0], True, True)

        for i in range(1, len(p.markers)):
            if p.markers[i] == '+':
                self.body.append(Atom(p.nodes[i * 2], p.nodes[i * 2 + 1], p.nodes[i * 2 + 2], True, True))
            else:
                self.body.append(Atom(p.nodes[i * 2 + 2], p.nodes[i * 2 + 1], p.nodes[i * 2], True, True))

    def set_head(self, head):
        self.head = head

    def add_body_atom(self, atom):
        self.body.append(atom)

    def replace_all_constants_by_variables(self):
        for atom in self.body:
            if atom.is_left_c():
                c = atom.left
                self.replace_by_variable(c, self.variables[self.next_free_variable])
                self.next_free_variable += 1
            if atom.is_right_c():
                c = atom.right
                self.replace_by_variable(c, self.variables[self.next_free_variable])
                self.next_free_variable += 1

    def replace_nearly_all_constants_by_variables(self):
        counter = 0
        for atom in self.body:
            counter += 1
            if counter == len(self.body):
                break
            if atom.is_left_c():
                c = atom.left
                self.replace_by_variable(c, Rule.variables[self.next_free_variable])
                self.next_free_variable += 1
            if atom.is_right_c():
                c = atom.right
                self.replace_by_variable(c, Rule.variables[self.next_free_variable])
                self.next_free_variable += 1

    def get_left_generalization(self):
        left_g = self.create_copy()
        left_constant = left_g.head.left
        x_count = left_g.replace_by_variable(left_constant, "X")
        if x_count < 2:
            left_g = None
        return left_g

    def get_right_generalization(self):
        right_g = self.create_copy()
        right_constant = right_g.head.right
        y_count = right_g.replace_by_variable(right_constant, "Y")
        if y_count < 2:
            right_g = None
        return right_g

    def get_left_right_generalization(self):
        lr_g = self.create_copy()
        left_constant = lr_g.head.left
        x_count = lr_g.replace_by_variable(left_constant, "X")
        right_constant = lr_g.head.right
        y_count = lr_g.replace_by_variable(right_constant, "Y")
        if x_count < 2 or y_count < 2:
            lr_g = None
        return lr_g

    def create_copy(self):
        copy = Rule(self.head.create_copy() if self.head else None)
        copy.body = [atom.create_copy() for atom in self.body]
        copy.next_free_variable = self.next_free_variable
        return copy

    def replace_by_variable(self, constant, variable):
        count = self.head.replace_by_variable(constant, variable)
        for body_literal in self.body:
            b_count = body_literal.replace_by_variable(constant, variable)
            count += b_count
        return count

    def is_xy_rule(self):
        return not self.head.is_left_c() and not self.head.is_right_c()

    def is_x_rule(self):
        if self.is_xy_rule():
            return False
        else:
            return not self.head.is_left_c()

    def is_y_rule(self):
        if self.is_xy_rule():
            return False
        else:
            return not self.head.is_right_c()

    def is_trivial(self):
        if len(self.body) == 1:
            if self.head == self.body[0]:
                return True
        return False

    def get_confidence(self):
        return self.confidence

    def get_correctly_predicted(self):
        return self.correctly_predicted

    def get_cyclic(self, current_variable, last_variable, value, body_index, direction, triples, previous_values,
                   final_results, count=None):
        from x.y.z.Python.algorithm.Apply import DISCRIMINATION_BOUND, TRIAL_SIZE
        from x.y.z.Python.algorithm.Learn import Learn
        if self.APPLICATION_MODE and len(final_results) >= DISCRIMINATION_BOUND:
            final_results.clear()
            return final_results

        if count:
            count.inc()
            if count.get() >= Learn.TRIAL_SIZE or count.get() >= TRIAL_SIZE:
                return final_results

        if not self.APPLICATION_MODE and len(final_results) >= Learn.SAMPLE_SIZE:
            return final_results

        # check if the value has been seen before as grounding of another variable
        atom = self.body[body_index]
        head_not_tail = atom.left == current_variable

        if value in previous_values:
            return final_results

        # the current atom is the last
        if (direction and len(self.body) - 1 == body_index) or (not direction and body_index == 0):
            # get groundings
            final_results.update(triples.get_entitiesm(atom.relation, value, head_not_tail))
            return final_results

        # the current atom is not the last
        else:
            results = triples.get_entities(atom.relation, value, head_not_tail)
            next_variable = atom.right if head_not_tail else atom.left
            current_values = previous_values.copy()
            current_values.add(value)

            for i, next_value in enumerate(results):
                if not Rule.APPLICATION_MODE and i >= Learn.SAMPLE_SIZE:
                    break

                updated_body_index = body_index + 1 if direction else body_index - 1
                self.get_cyclic(next_variable, last_variable, next_value, updated_body_index, direction, triples,
                                current_values, final_results, count)
            return final_results


    def ground_body_cyclic(self, first_variable, last_variable, triples, sampling_on):
        from x.y.z.Python.algorithm.Learn import Learn
        groundings = SampledPairedResultSet()
        atom = self.body[0]
        #print("atom", atom)
        #print("end atom")
        head_not_tail = atom.get_left() == first_variable
        #print("TRiple_relation: ", atom.get_relation())
        rtriples = triples.get_triples_by_relation(atom.get_relation())
        counter = 0
        count = Counter()

        for t in rtriples:
            counter += 1
            last_variable_groundings = set()

            last_variable_groundings = self.get_cyclic(first_variable, last_variable, t.get_value(head_not_tail), 0, True, triples, set(), last_variable_groundings, count)
            if last_variable_groundings:
                if first_variable == "X":
                    groundings.add_key(t.get_value(head_not_tail))
                    for last_variable_value in last_variable_groundings:
                        groundings.add_value(last_variable_value)
                else:
                    for last_variable_value in last_variable_groundings:
                        groundings.add_key(last_variable_value)
                        groundings.add_value(t.get_value(head_not_tail))

            if (counter > Learn.SAMPLE_SIZE or groundings.size() > Learn.SAMPLE_SIZE) and sampling_on:
                break
            if not self.APPLICATION_MODE and count.get() >= Learn.TRIAL_SIZE:
                break
        #print("GRoundings: ", groundings.values)
        return groundings

    def ground_body_acyclic(self, first_variable, last_variable, triples, sampling_on):
        from x.y.z.Python.algorithm.Learn import Learn
        groundings = SampledPairedResultSet()

        # Retrieve the first atom in the body
        atom = self.body[0]
        head_not_tail = atom.get_left() == first_variable
        rtriples = triples.get_triples_by_relation(atom.get_relation())

        counter = 0
        count = Counter()

        # Iterate over triples
        for t in rtriples:
            counter += 1
            last_variable_groundings = set()

            # Iterate over the remaining atoms in the path
            for body_index in range(1, len(self.body)):
                current_atom = self.body[body_index]
                current_variable = current_atom.left if head_not_tail else current_atom.right

                # Get groundings for the current atom
                results = triples.get_entities(current_atom.relation, t.get_value(head_not_tail), not head_not_tail)

                # Update last variable groundings for the next iteration
                last_variable_groundings = results

            # Add groundings to the result set
            if first_variable == "X":
                groundings.add_key(t.get_value(head_not_tail))
                for last_variable_value in last_variable_groundings:
                    groundings.add_value(last_variable_value)
            else:
                for last_variable_value in last_variable_groundings:
                    groundings.add_key(last_variable_value)
                    groundings.add_value(t.get_value(head_not_tail))

            # Break conditions
            if counter > Learn.SAMPLE_SIZE or groundings.size() > Learn.SAMPLE_SIZE:
                break
            if not self.APPLICATION_MODE and count.get() >= Learn.TRIAL_SIZE:
                break

        return groundings

    def compute_scores(self, triples):
        if self.is_xy_rule():
            #print("XY")
            # X is given in the first body atom
            xypairs = self.ground_body_cyclic("X", "Y", triples, sampling_on=True) if "X" in self.body else self.ground_body_cyclic("Y", "X", triples, sampling_on=True)
            # Body groundings
            correctly_predicted = 0
            predicted = 0
            for key, values in xypairs.get_values().items():
                for value in values:
                    predicted += 1
                    if triples.is_true(key, self.head.get_relation(), value):
                        correctly_predicted += 1

            self.predicted = predicted
            self.correctly_predicted = correctly_predicted
            self.confidence = correctly_predicted / predicted if predicted != 0 else 0.0

        if self.is_x_rule():
            #print("X")
            #print("GROUNDINGS")
            xvalues = set()
            xvalues = self.compute_values_reversed("X", xvalues, triples)
            predicted = 0
            correctly_predicted = 0
            for xvalue in xvalues:
                predicted += 1
                if triples.is_true(xvalue, self.head.get_relation(), self.head.get_right()):
                    correctly_predicted += 1

            self.predicted = predicted
            self.correctly_predicted = correctly_predicted
            self.confidence = correctly_predicted / predicted if predicted != 0 else 0.0

        if self.is_y_rule():
            #print("RULE:", self.head, self.body)
            #print(self.head.get_left())
            #print(self.head.get_relation())
            #print("Y")
            yvalues = set()
            #print("GROUNDINGS")
            yvalues = self.compute_values_reversed("Y", yvalues, triples)
            #print("Y_VALUES:", yvalues)
            predicted = 0
            correctly_predicted = 0
            for yvalue in yvalues:
                #print("YVALUE", yvalue)
                predicted += 1
                #print("THINGY:", self.head.get_left(), self.head.get_relation(), yvalue)
                if triples.is_true(self.head.get_left(), self.head.get_relation(), yvalue):
                    correctly_predicted += 1
                    #print("PLUS 1")
            #print("PRED", predicted)
            self.predicted = predicted
            self.correctly_predicted = correctly_predicted
            self.confidence = self.correctly_predicted / predicted if predicted != 0 else 0.0

    def compute_values_reversed(self, target_variable, target_values, ts):
        from x.y.z.Python.algorithm.Learn import Learn
        from x.y.z.Python.algorithm.Apply import DISCRIMINATION_BOUND
        atom_index = len(self.body) - 1
        #print(self.body, atom_index)
        last_atom = self.body[atom_index]
        #print("ATOM:", last_atom.left, last_atom.right)
        #print("2", last_atom.is_left_c())
        #print(last_atom)
        unbound_variable = self.get_unbound_variable()
        #print("VAR", unbound_variable)
        if unbound_variable is None:
            next_var_is_left = not last_atom.is_left_c()
            constant = last_atom.get_lr(not next_var_is_left)
            #print("Constant:", constant)
            next_variable = last_atom.get_lr(next_var_is_left)
            #print("next var", next_variable)
            #print("Test", last_atom.relation, constant, not next_var_is_left)
            values = ts.get_entitiesm(last_atom.relation, constant, not next_var_is_left)
            #print("ENTITIES: ", values)
            previous_values = {constant}
            #print("Values: ", values)
            for value in values:
                target_values = self.forward_reversed(next_variable, value, atom_index - 1, target_variable, target_values, ts,
                                 previous_values)
                #print("target:", target_values)
                if not self.application_mode and len(target_values) >= Learn.SAMPLE_SIZE:
                    return target_values

                if self.application_mode and len(target_values) >= DISCRIMINATION_BOUND:
                    target_values.clear()
                    return target_values
        else:
            next_var_is_left = not (last_atom.left == unbound_variable)
            next_variable = last_atom.get_lr(next_var_is_left)
            #print("next var left", next_var_is_left)
            #print("next var", next_variable)
            triples = ts.get_triples_by_relation(last_atom.relation)
            for triple in triples:
                value = triple.get_value(next_var_is_left)
                #print("Triple value", value)
                #print("TARGET VALUES:", target_values)
                previous_values = {triple.get_value(not next_var_is_left)}
                if value not in target_values:
                    #target_values.add(value)
                    target_values = self.forward_reversed(next_variable, value, atom_index - 1, target_variable, target_values, ts,
                                     previous_values)
                    #print("TARGET values", target_values)
        #print("TARGET VALUES", target_values)
        return target_values

    def forward_reversed(self, current_variable, current_value, atom_index, target_variable, target_values, triple_set,
                         previous_values):
        if atom_index < 0:
            #if current_variable == target_variable:
            target_values.add(current_value)
            return target_values

        else:
            atom = self.body[atom_index]
            if atom.is_left_c():
                self.forward_reversed(atom.left, current_value, atom_index - 1, target_variable, target_values,
                                       triple_set, previous_values)
            elif atom.is_right_c():
                self.forward_reversed(atom.right, current_value, atom_index - 1, target_variable, target_values,
                                       triple_set, previous_values)
            else:
                if atom.left == current_variable:
                    next_var_is_left = not atom.is_left_c()
                    constant = atom.get_lr(not next_var_is_left)
                    #print("Constant", constant)
                    next_variable = atom.get_lr(next_var_is_left)
                    if constant not in previous_values:
                        previous_values.add(constant)
                        values = triple_set.get_entitiesm(atom.relation, constant, not next_var_is_left)
                        for value in values:
                            target_values = self.forward_reversed(next_variable, value, atom_index - 1, target_variable, target_values,
                                                   triple_set, previous_values)
                            if not self.application_mode and len(target_values) >= 100:
                                return
                elif atom.right == current_variable:
                    next_var_is_left = not atom.is_right_c()
                    constant = atom.get_lr(not next_var_is_left)
                    next_variable = atom.get_lr(next_var_is_left)
                    if constant not in previous_values:
                        previous_values.add(constant)
                        values = triple_set.get_entitiesm(atom.relation, constant, not next_var_is_left)
                        for value in values:
                            target_values = self.forward_reversed(next_variable, value, atom_index - 1, target_variable, target_values,
                                                   triple_set, previous_values)
                            if not self.application_mode and len(target_values) >= 100:
                                return target_values
            return target_values

    def get_unbound_variable(self):
        if self.body[-1].is_left_c() or self.body[-1].is_right_c():
            return None

        counter = {}
        for atom in self.body:
            if atom.left != "X" and atom.left != "Y":
                counter[atom.left] = counter.get(atom.left, 0) + 1
            if atom.right != "X" and atom.right != "Y":
                counter[atom.right] = counter.get(atom.right, 0) + 1

        for variable, count in counter.items():
            if count == 1:
                return variable

        return None

    def get_generalizations(self, only_xy):
        generalizations = set()
        #print("Body: ",self.body)
        #print(self.head)
        #self.path_to_atoms(self.head)
        #print(self.head)

        # Cyclic rule
        leftright = self.get_left_right_generalization()
        if leftright is not None:
            leftright.replace_all_constants_by_variables()
            generalizations.add(leftright)

        if only_xy:
            return generalizations

        # Acyclic rule
        left = self.get_left_generalization()
        if left is not None:
            left_free = left.create_copy()
            if leftright is None:
                left_free.replace_all_constants_by_variables()
            left.replace_nearly_all_constants_by_variables()
            generalizations.add(left)

            if leftright is None:
                generalizations.add(left_free)

        right = self.get_right_generalization()
        if right is not None:
            right_free = right.create_copy()
            if leftright is None:
                right_free.replace_all_constants_by_variables()
            right.replace_nearly_all_constants_by_variables()
            generalizations.add(right)

            if leftright is None:
                generalizations.add(right_free)
        return generalizations

    def bodysize(self):
        return len(self.body)



    def __str__(self):
        body_str = ', '.join(str(atom) for atom in self.body)
        return f"Rule({self.head} :- {body_str})"
