class Atom:
    def __init__(self, left, relation, right, leftC, rightC):
        self.relation = relation
        self.left = left
        self.right = right
        self.leftC = leftC
        self.rightC = rightC
        self.hashcode = 0
        self.hashcode_initialized = False

    def get_atom_representation(self, atom_representation):
        t1 = atom_representation.split("(", 1)
        t2 = t1[1].split(",")
        relation = t1[0]
        left = t2[0]
        right = t2[1][:-1]  # Remove the last character which is ")"
        if right.endswith(")"):
            right = right[:-1]
        self.relation = relation
        self.left = left
        self.right = right
        self.leftC = False if len(self.left) == 1 else True
        self.rightC = False if len(self.right) == 1 else True

    def get_relation(self):
        return self.relation

    def set_relation(self, relation):
        self.relation = relation

    def get_left(self):
        return self.left

    def set_left(self, left):
        self.left = left

    def get_right(self):
        return self.right

    def set_right(self, right):
        self.right = right

    def is_left_c(self):
        return self.leftC

    def set_left_c(self, leftC):
        self.leftC = leftC

    def is_right_c(self):
        return self.rightC

    def set_right_c(self, rightC):
        self.rightC = rightC

    def __str__(self):
        return f"{self.relation}({self.left},{self.right})"

    def __eq__(self, that_object):
        if isinstance(that_object, Atom):
            that = that_object
            if self.get_relation() == that.get_relation() and self.get_left() == that.get_left() and self.get_right() == that.get_right():
                return True
        return False

    def __hash__(self):
        if not self.hashcode_initialized:
            self.hashcode = hash(str(self))
            self.hashcode_initialized = True
        return self.hashcode

    def create_copy(self):
        copy = Atom(self.left, self.relation, self.right, self.leftC, self.rightC)
        return copy

    def replace_by_variable(self, constant, variable):
        i = 0
        if self.leftC and self.left == constant:
            self.leftC = False
            self.left = variable
            i += 1
        if self.rightC and self.right == constant:
            self.rightC = False
            self.right = variable
            i += 1
        return i

    def uses(self, constant_or_variable):
        if self.get_left() == constant_or_variable or self.get_right() == constant_or_variable:
            return True
        return False

    def is_lrc(self, left_not_right):
        if left_not_right:
            return self.is_left_c()
        else:
            return self.is_right_c()

    def get_lr(self, left_not_right):
        if left_not_right:
            return self.get_left()
        else:
            return self.get_right()

    def contains(self, term):
        if self.left == term or self.right == term:
            return True
        return False
