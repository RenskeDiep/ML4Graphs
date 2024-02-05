from .Triple import Triple
class TripleSet:
    def __init__(self, filepath=None):
        self.triples = []
        self.head_to_list = {}
        self.tail_to_list = {}
        self.relation_to_list = {}
        self.head_relation2tail = {}
        self.head_tail2relation = {}
        self.tail_relation2head = {}
        self.frequent_relations = set()

        if filepath:
            self.read_triples(filepath)
            self.index_triples()

    def add_triple_set(self, ts):
        for triple in ts.get_triples():
            self.add_triple(triple)

    def add_triple(self, triple):
        self.triples.append(triple)
        self.add_triple_to_index(triple)

    def index_triples(self):
        for triple in self.triples:
            self.add_triple_to_index(triple)
        print("* set up index for", len(self.relation_to_list), "relations,",
              len(self.head_to_list), "head entities, and", len(self.tail_to_list), "tail entities")

    def add_triple_to_index(self, t):
        head = t.head
        tail = t.tail
        relation = t.relation

        # index head
        if head not in self.head_to_list:
            self.head_to_list[head] = []
        self.head_to_list[head].append(t)

        # index tail
        if tail not in self.tail_to_list:
            self.tail_to_list[tail] = []
        self.tail_to_list[tail].append(t)

        # index relation
        if relation not in self.relation_to_list:
            self.relation_to_list[relation] = []
        self.relation_to_list[relation].append(t)

        # index head-relation => tail
        if head not in self.head_relation2tail:
            self.head_relation2tail[head] = {}
        if relation not in self.head_relation2tail[head]:
            self.head_relation2tail[head][relation] = set()
        self.head_relation2tail[head][relation].add(tail)

        # index tail-relation => head
        if tail not in self.tail_relation2head:
            self.tail_relation2head[tail] = {}
        if relation not in self.tail_relation2head[tail]:
            self.tail_relation2head[tail][relation] = set()
        self.tail_relation2head[tail][relation].add(head)

        # index headTail => relation
        if head not in self.head_tail2relation:
            self.head_tail2relation[head] = {}
        if tail not in self.head_tail2relation[head]:
            self.head_tail2relation[head][tail] = set()
        self.head_tail2relation[head][tail].add(relation)

    def read_triples(self, filepath):
        with open(filepath, 'r', encoding='UTF-8') as file:
            line_counter = 0
            for line in file:
                line_counter += 1
                if line_counter % 1000000 == 0:
                    print(">>> parsed", line_counter, "lines")

                if len(line) <= 2:
                    continue

                tokens = line.split("\t")
                if len(tokens) < 3:
                    tokens = line.split(" ")

                if len(tokens) == 3:
                    triple = Triple(tokens[0], tokens[1], tokens[2])
                elif len(tokens) == 4:
                    if tokens[3] == ".":
                        triple = Triple(tokens[0], tokens[1], tokens[2])
                    else:
                        try:
                            triple = AnnotatedTriple(tokens[0], tokens[1], tokens[2])
                            triple.set_confidence(float(tokens[3]))
                        except ValueError:
                            print("could not parse line", line)
                            triple = None
                else:
                    print("problem in parsing line", line_counter, ":", line)
                    triple = None

                if triple:
                    self.triples.append(triple)

        print("* read", len(self.triples), "triples")

    def get_triples(self):
        return self.triples

    def get_triples_by_head(self, head):
        return self.head_to_list.get(head, [])

    def get_n_triples_by_head(self, head, n):
        if head in self.head_to_list:
            if len(self.head_to_list[head]) <= n:
                return self.head_to_list[head]
            else:
                chosen = random.sample(self.head_to_list[head], n)
                return chosen
        else:
            return []

    def get_triples_by_tail(self, tail):
        return self.tail_to_list.get(tail, [])

    def get_n_triples_by_tail(self, tail, n):
        if tail in self.tail_to_list:
            if len(self.tail_to_list[tail]) <= n:
                return self.tail_to_list[tail]
            else:
                chosen = random.sample(self.tail_to_list[tail], n)
                return chosen
        else:
            return []

    def get_triples_by_relation(self, relation):
        return self.relation_to_list.get(relation, [])

    def get_relations(self):
        return self.relation_to_list.keys()

    def get_head_entities(self, relation, tail):
        print("REl", relation)
        print("tail", tail)
        print("DICTIONARY")
        dictionary = open("C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/rules_dict", "w")
        dictionary.write(str(self.head_relation2tail))
        if tail in self.tail_relation2head:
            print("part1")
        if tail in self.tail_relation2head and relation in self.tail_relation2head[tail]:
            print("YESSSSS")
            print(self.tail_relation2head[tail][relation])
            return self.tail_relation2head[tail][relation]
        return set()

    def get_tail_entities(self, relation, head):
        #print("dict:", self.head_relation2tail)
        print("DICTIONARY")
        dictionary = open("C:/Users/rensk/Documents/Amsterdam/Year 2 (M)/Period 3/ML4Graphs/anyburl-sources/x/y/z/Python/data/FB15/rules_dict", "w")
        dictionary.write(str(self.head_relation2tail))
        if head in self.head_relation2tail:
            print("part2")
        if head in self.head_relation2tail and relation in self.head_relation2tail[head]:
            return self.head_relation2tail[head][relation]
        return set()

    def get_entitiesm(self, relation, value, head_not_tail):
        print(relation, value)
        if head_not_tail:
            print("Head")
            return self.get_tail_entities(relation, value)
        else:
            print("Tail")
            print("entities", self.get_head_entities(relation, value))
            return self.get_head_entities(relation, value)

    def get_relations_by_head_tail(self, head, tail):
        return self.head_tail2relation.get(head, {}).get(tail, set())

    def is_true(self, head, relation, tail):
        return tail in self.head_relation2tail.get(head, {}).get(relation, set())

    def is_true_for_triple(self, triple):
        return self.is_true(triple.head, triple.relation, triple.tail)

    def compare_to(self, that, this_id, that_id):
        print("* Comparing two triple sets")
        counter = 0
        for triple in self.triples:
            if that.is_true_for_triple(triple):
                counter += 1

        print("* size of", this_id + ":", len(self.triples))
        print("* size of", that_id + ":", len(that.triples))
        print("* size of intersection:", counter)

    def get_intersection_with(self, that):
        ts = TripleSet()
        for triple in self.triples:
            if that.is_true_for_triple(triple):
                ts.add_triple(triple)
        return ts

    def minus(self, that):
        ts = TripleSet()
        for triple in self.triples:
            if not that.is_true_for_triple(triple):
                ts.add_triple(triple)
        return ts

    def get_num_of_entities(self):
        return len(self.head_to_list) + len(self.tail_to_list)

    def determine_frequent_relations(self, coverage):
        relation_counter = {}
        all_counter = 0

        for triple in self.triples:
            all_counter += 1
            r = triple.relation

            if r in relation_counter:
                relation_counter[r] += 1
            else:
                relation_counter[r] = 1

        counts = sorted(relation_counter.values())
        count_up = 0
        border = 0

        for c in counts:
            count_up += c

            if (all_counter - count_up) / all_counter < coverage:
                border = c
                break

        for r in relation_counter:
            if relation_counter[r] > border:
                self.frequent_relations.add(r)

    def is_frequent_relation(self, relation):
        return relation in self.frequent_relations

    def exists_path(self, x, y, path_length):
        if path_length == 1:
            if self.get_relations_by_head_tail(x, y):
                return True
            if self.get_relations_by_head_tail(y, x):
                return True
            return False

        if path_length == 2:
            hop1x = set()
            for hx in self.get_triples_by_head(x):
                hop1x.add(hx.tail)
            for tx in self.get_triples_by_tail(x):
                hop1x.add(tx.head)

            for hy in self.get_triples_by_head(y):
                if hy.tail in hop1x:
                    return True
            for ty in self.get_triples_by_tail(y):
                if ty.head in hop1x:
                    return True
            return False

        if path_length > 2:
            print("checking the existence of a path longer than 2 is not supported yet")
            exit(-1)

        return False

    def get_entities(self):
        entities = set()
        entities.update(self.head_to_list.keys())
        entities.update(self.tail_to_list.keys())
        return entities

    def write(self, filepath):
        with open(filepath, 'w') as file:
            for triple in self.triples:
                file.write(str(triple) + '\n')
        return self.triples