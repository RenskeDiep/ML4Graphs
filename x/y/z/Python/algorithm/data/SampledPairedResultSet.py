class SampledPairedResultSet:
    def __init__(self):
        self.value_counter = 0
        self.values = {}
        self.sampling = False
        self.current_key = ""

    def add_key(self, key):
        self.current_key = key
        if key not in self.values:
            self.values[key] = set()

    def get_values(self):
        return self.values

    def used_sampling(self):
        return self.sampling

    def add_value(self, value):
        self.values[self.current_key].add(value)
        self.value_counter += 1

    def size(self):
        return self.value_counter

