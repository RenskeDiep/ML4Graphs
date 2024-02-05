def compute_values_reversed(self, target_variable, target_values, triple_set):
    atom_index = len(self.body) - 1
    last_atom = self.body[atom_index]
    unbound_variable = self.get_unbound_variable()

    if unbound_variable is None:
        next_var_is_left = not last_atom.is_left_c()
        constant = last_atom.get_lr(not next_var_is_left)
        next_variable = last_atom.get_lr(next_var_is_left)
        values = triple_set.get_entitiesm(last_atom.relation, constant, not next_var_is_left)
        previous_values = {constant}

        for value in values:
            self.forward_reversed(next_variable, value, atom_index - 1, target_variable, target_values, triple_set,
                                  previous_values)
            if not self.application_mode and len(target_values) >= 100:
                return

            if self.application_mode and len(target_values) >= Apply.DISCRIMINATION_BOUND:
                target_values.clear()
                return
    else:
        next_var_is_left = not last_atom.left == unbound_variable
        next_variable = last_atom.get_lr(next_var_is_left)
        triples = triple_set.get_triples_by_relation(last_atom.relation)

        for triple in triples:
            value = triple.get_value(next_var_is_left)
            previous_values = {triple.get_value(not next_var_is_left)}
            if value not in target_values:
                self.forward_reversed(next_variable, value, atom_index - 1, target_variable, target_values,
                                      triple_set, previous_values)


def compute_values_reversed(self, target_variable, target_values, triple_set):
    atom_index = len(self.body) - 1
    last_atom = self.body[atom_index]
    unbound_variable = self.get_unbound_variable()

    goal_values = set()  # Initialize an empty set to store values

    if unbound_variable is None:
        next_var_is_left = not last_atom.is_left_c()
        constant = last_atom.get_lr(not next_var_is_left)
        next_variable = last_atom.get_lr(next_var_is_left)
        values = triple_set.get_entities(last_atom.relation, constant, not next_var_is_left)
        previous_values = {constant}

        for value in values:
            self.forward_reversed(next_variable, value, atom_index - 1, target_variable, target_values, triple_set,
                                  previous_values)
            if not self.application_mode and len(target_values) >= 100:
                break

            if self.application_mode and len(target_values) >= Apply.DISCRIMINATION_BOUND:
                target_values.clear()
                break
    else:
        next_var_is_left = not last_atom.left == unbound_variable
        next_variable = last_atom.get_lr(next_var_is_left)
        triples = triple_set.get_triples_by_relation(last_atom.relation)

        for triple in triples:
            value = triple.get_value(next_var_is_left)
            previous_values = {triple.get_value(not next_var_is_left)}
            if value not in target_values:
                self.forward_reversed(next_variable, value, atom_index - 1, target_variable, target_values,
                                      triple_set, previous_values)

    return goal_values