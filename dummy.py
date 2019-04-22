from collections import defaultdict
from itertools import combinations

class Dummy():
    def __init__(self, min_sup, min_conf, D):
        self.min_sup = min_sup # 最低支持度
        self.min_conf = min_conf # 最低置信度
        self.D = D # 事务集
        self.transactions = list() # 去除事务内重复项的事务集
        self.itemsets = set() # 物品集
        self.frequent_itemsets = set() # 频繁项集
        self.frequent_patterns = set() # 频繁项和对应支持度集
        for transaction in D:
            for item in transaction:
                self.itemsets.add(frozenset([item]))
            self.transactions.append(frozenset(transaction))
        self.patterns_count = defaultdict(float)

    # 遍历事务集获得支持度
    def get_support(self, itemsets):
        if not self.patterns_count[itemsets] == 0:
            return self.patterns_count[itemsets]
        count = 0
        for transaction in self.transactions:
            if itemsets.issubset(transaction):
                count += 1
        self.patterns_count[itemsets] = count * 1.0 / len(self.D)
        return count * 1.0 / len(self.D)

    # 回溯法遍历
    def recur(self, patterns):
        for item in self.itemsets:
            if not item.issubset(patterns):
                new_list = list(patterns.union(item))
                new_list.sort()
                new_set = frozenset(new_list)
                if self.get_support(new_set) >= self.min_sup:
                    self.frequent_patterns.add((tuple(new_set), self.get_support(new_set)))
                    self.frequent_itemsets.add(new_set)
                    self.recur(new_set)
                else:
                    continue

    def dummy(self):
        self.recur(frozenset())
        return self.frequent_patterns

    def subsets(self, s):
        for cardinality in range(len(s) + 1):
            yield from combinations(s, cardinality)

    def generate_rules(self):
        rules = []
        for item in self.frequent_itemsets:
            sub_sets = [set(sub_set) for sub_set in self.subsets(item)]
            for sub in sub_sets:
                if len(sub) == 0 or len(item.difference(sub)) == 0:
                    continue
                confidence = self.get_support(item) / self.get_support(frozenset(sub))
                if confidence >= self.min_conf:
                    rules.append(((tuple(sub), tuple(item.difference(sub))), confidence))
        return rules