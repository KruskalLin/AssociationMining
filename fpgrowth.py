from collections import defaultdict
from itertools import combinations

# FPTree节点
class TreeNode(object):
    def __init__(self, fp_tree, item, count):
        self.fp_tree = fp_tree
        self.item = item
        self.count = count
        self.parent = None
        self.siblings = None
        self.children = dict()

    def find_children(self, item):
        if self.children.__contains__(item):
            return self.children[item]
        return None

    # 级联打印树，用于测试
    def __str__(self, level=0):
        ret = "\t" * level + repr(self.item) + repr(self.count) + "\n"
        for (item, child) in self.children.items():
            ret += child.__str__(level + 1)
        return ret

class FPTree(object):
    def __init__(self):
        self.root = TreeNode(self, None, None)
        self.header_table = dict() # 头表
        self.itemsets = set() # 物品集

    # 得到所有包含这个物品的树节点
    def get_nodes(self, item):
        if self.header_table.__contains__(item) == False:
            return None
        node = self.header_table[item]
        nodes = []
        while node != None:
            nodes.append(node)
            node = node.siblings
        return nodes

    # 插入树、头表
    def insert_tree(self, transaction):
        current_node = self.root
        for item in transaction:
            children = current_node.find_children(item)
            self.itemsets.add(item)
            if children == None:
                children = TreeNode(self, item, 1)
                current_node.children[item] = children
                children.parent = current_node
                if self.header_table.__contains__(item):
                    children.siblings = self.header_table[item]
                self.header_table[item] = children

            else:
                children.count += 1
            current_node = children

    # 得到前缀路径
    def prefix_paths(self, item):
        paths = []
        node = self.header_table[item]
        siblings = node
        while siblings != None:
            path = []
            current_node = siblings
            while current_node != self.root:
                path.append(current_node)
                current_node = current_node.parent
            path.reverse()
            paths.append(path)
            siblings = siblings.siblings
        return paths

    def print_tree(self):
        print(str(self.root))


class FPGrwoth():
    def __init__(self, min_sup, min_conf, D):
        self.min_sup = min_sup # 最低支持度
        self.min_conf = min_conf # 最低置信度
        self.D = D # 事务集
        self.frequent_itemsets = list() # 频繁项和对应支持度集
        self.itemsets = set() # 频繁项集
        self.frequent_itemsets_count = defaultdict(int) # 频繁项和对应支持度计数
        self.tree = FPTree()

        itemsets_count = defaultdict(int)
        itemsets = set()
        for transaction in D:
            for item in transaction:
                itemsets_count[item] += 1

        for (item, count) in itemsets_count.items():
            if count * 1.0 / len(D) >= min_sup:
                itemsets.add(item)

        for transaction in self.D:
            transaction = filter(lambda v: v in itemsets, transaction)
            transaction = list(transaction)
            transaction.sort(key=lambda v: itemsets_count[v], reverse=True)
            self.tree.insert_tree(transaction)

    # 根据前缀路径构建FPTree
    def build_conditional_FPTree(self, paths):
        tree = FPTree()
        for path in paths:
            last_node = path[-1]
            count = last_node.count
            current_node = tree.root
            for node in path[:-1]:
                children = current_node.find_children(node.item)
                tree.itemsets.add(node.item)
                if children == None:
                    children = TreeNode(tree, node.item, count)
                    current_node.children[node.item] = children
                    children.parent = current_node
                    if tree.header_table.__contains__(node.item):
                        children.siblings = tree.header_table[node.item]
                    tree.header_table[node.item] = children
                else:
                    children.count += count
                current_node = children
        return tree

    # 递归构建子FPTree挖掘频繁项集
    def find_frequent_itemsets(self, tree, patterns):
        for item in tree.itemsets:
            nodes = tree.get_nodes(item)
            count = sum(node.count for node in nodes)
            if item not in patterns and count * 1.0 / len(self.D) >= self.min_sup:
                frequent_patterns = [item] + patterns
                self.itemsets.add(frozenset(frequent_patterns))
                self.frequent_itemsets_count[frozenset(frequent_patterns)] = count
                yield (frequent_patterns, count * 1.0 / len(self.D))
                conditonal_tree = self.build_conditional_FPTree(tree.prefix_paths(item))
                for pattern_pair in self.find_frequent_itemsets(conditonal_tree, frequent_patterns):
                    yield pattern_pair

    def fp_growth(self):
        items = set()
        for (patterns, support) in self.find_frequent_itemsets(self.tree, []):
            patterns = list(patterns)
            patterns.sort()
            items.add((tuple(patterns), support))
        self.frequent_itemsets = items
        return items

    def subsets(self, s):
        for cardinality in range(len(s) + 1):
            yield from combinations(s, cardinality)

    def generate_rules(self):
        rules = []
        for item in self.itemsets:
            sub_sets = [set(sub_set) for sub_set in self.subsets(item)]
            for sub in sub_sets:
                if len(sub) == 0 or len(item.difference(sub)) == 0:
                    continue
                confidence = (self.frequent_itemsets_count[item] * 1.0 / len(self.D))/(self.frequent_itemsets_count[frozenset(sub)] * 1.0 / len(self.D))
                if confidence >= self.min_conf:
                    kulc = (self.frequent_itemsets_count[item] * 1.0 / len(self.D))/(self.frequent_itemsets_count[frozenset(sub)] * 1.0 / len(self.D)) + (self.frequent_itemsets_count[item] * 1.0 / len(self.D))/(self.frequent_itemsets_count[frozenset(item.difference(sub))] * 1.0 / len(self.D))
                    kulc /= 2
                    ir = abs(self.frequent_itemsets_count[frozenset(sub)] - self.frequent_itemsets_count[frozenset(item.difference(sub))]) * 1.0 / (self.frequent_itemsets_count[frozenset(sub)] + self.frequent_itemsets_count[frozenset(item.difference(sub))] - self.frequent_itemsets_count[item])
                    rules.append(((tuple(sub), tuple(item.difference(sub))), confidence, kulc, ir))
        return rules