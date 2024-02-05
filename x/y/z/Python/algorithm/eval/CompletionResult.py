class CompletionResult:
    def __init__(self, triple):
        self.triple = triple
        self.head_results = []
        self.tail_results = []

    def add_head_results(self, heads, k):
        if k > 0:
            self._add_results(heads, self.head_results, k)
        else:
            self._add_results(heads, self.head_results)

    def add_tail_results(self, tails, k):
        if k > 0:
            self._add_results(tails, self.tail_results, k)
        else:
            self._add_results(tails, self.tail_results)

    def _add_results(self, candidates, results, k=None):
        for c in candidates:
            if c != "":
                results.append(c)
                if k is not None:
                    k -= 1
                    if k == 0:
                        return

    def get_heads(self):
        return self.head_results

    def get_tails(self):
        return self.tail_results
