from collections import defaultdict
from itertools import combinations

class Apriori():
    def __init__(self, min_sup, min_conf, D):
        self.min_sup = min_sup  # 最低支持度
        self.min_conf = min_conf  # 最低置信度
        self.frequent_itemsets_count = defaultdict(int) # 频繁项集支持度计数
        self.L = set() # 频繁项集集合
        self.D = D # 事务集
        self.itemsets = set() # 物品集
        for transaction in D:
            for item in transaction:
                self.itemsets.add(frozenset([item]))

    # 去除支持度低的项集
    def find_frequent_itemsets(self, C):
        L = set()
        for item in C:
            for transaction in self.D:
                if item.issubset(set(transaction)):
                    self.frequent_itemsets_count[item] += 1

        for item in C:
            support = self.frequent_itemsets_count[item] * 1.0 / len(self.D)
            if support >= self.min_sup:
                L.add(item)
        self.L.add(frozenset(L))
        return L

    def apriori_gen(self, L):
        C = set()
        # 连接
        for i in L:
            for j in L:
                if i.issubset(j) & j.issubset(i):
                    continue
                temp = list(i.union(j))
                if len(temp) > len(i) + 1:
                    continue
                temp.sort()
                C.add(frozenset(temp))
        # 剪枝
        L = self.find_frequent_itemsets(C)
        return L

    def apriori(self):
        L = self.find_frequent_itemsets(self.itemsets)
        while(len(L) > 0):
            L = self.apriori_gen(L)

        items = set()
        for L in self.L:
            for item in L:
                item_copy = list(item)
                item_copy.sort()
                items.add((tuple(item_copy), self.frequent_itemsets_count[item] * 1.0 / len(self.D)))
        return items

    def subsets(self, s):
        for cardinality in range(len(s) + 1):
            yield from combinations(s, cardinality)

    def generate_rules(self):
        rules = []
        for L in self.L:
            for item in L:
                sub_sets = [set(sub_set) for sub_set in self.subsets(item)]
                for sub in sub_sets:
                    if len(sub) == 0 or len(item.difference(sub)) == 0:
                        continue
                    confidence = (self.frequent_itemsets_count[item] * 1.0 / len(self.D))/(self.frequent_itemsets_count[frozenset(sub)] * 1.0 / len(self.D))
                    if confidence >= self.min_conf:
                        rules.append(((tuple(sub), tuple(item.difference(sub))), confidence))
        return rules