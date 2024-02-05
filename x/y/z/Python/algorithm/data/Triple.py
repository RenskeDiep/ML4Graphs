class Triple:
    def __init__(self, head, relation, tail):
        self.head = head
        self.relation = relation
        self.tail = tail
        self.h = 0
        self.h_set = False

    def get_head(self):
        return self.head

    def get_tail(self):
        return self.tail

    def get_value(self, head_not_tail):
        if head_not_tail:
            return self.head
        else:
            return self.tail

    def get_relation(self):
        return self.relation

    def __str__(self):
        return f"{self.head} {self.relation} {self.tail}"

    def __eq__(self, other):
        if isinstance(other, Triple) or isinstance(other, AnnotatedTriple):
            that_triple = other
            return self.head == that_triple.head and self.tail == that_triple.tail and self.relation == that_triple.relation
        return False

    def __hash__(self):
        if not self.h_set:
            self.h = hash(self.head) + hash(self.tail) + hash(self.relation)
        return self.h