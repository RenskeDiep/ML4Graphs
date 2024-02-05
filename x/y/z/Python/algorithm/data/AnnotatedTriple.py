from Triple import Triple

class AnnotatedTriple(Triple):
    def __init__(self, head, relation, tail):
        super().__init__(head, relation, tail)
        self.confidence = 0.0

    def set_confidence(self, confidence):
        self.confidence = confidence

    def get_confidence(self):
        return self.confidence

    def __eq__(self, other):
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()

    def __str__(self):
        return f"{super().__str__()} {self.confidence}"

    def __lt__(self, that):
        if self.confidence > that.confidence:
            return 1
        elif self.confidence == that.confidence:
            return 0
        else:
            return -1

    def __le__(self, that):
        return self.confidence <= that.confidence

    def __gt__(self, that):
        return self.confidence > that.confidence

    def __ge__(self, that):
        return self.confidence >= that.confidence