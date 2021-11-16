from nltk.grammar import *
from nltk.tree import Tree
from nltk import CFG
import nltk
# nltk.grammar.is_terminal()

class cyk_parser(object):
    def __init__(self):
        self.sentence = []
        self.rules = None
        self.trees = []
        self.is_correct = False

        self.normal_rules = None
        self.matrix = None
    def set_sentence(self, s):
        res = []
        cur = s.split(" ")
        for word in cur:
            if word.isalnum():
                res.append(word.lower())
        self.sentence = res
    def set_rules(self, path):
        with open(path, 'r') as f:
            data = f.readlines()
        g = CFG.fromstring(data)
        rules = g.productions()
        self.rules = rules

    def find_common_nonterminal(self, rule):
        lhs = rule.lhs() # str
        rhs = rule.rhs() #tuple

        # lhs_str = lhs.symbol()
        for s in rhs:
            if s == lhs:
                return s

        return None

    def is_terminal(self, rule):
        return rule.is_lexical()

    def filter_terminals(self, rules):
        # to filter the same non-terminals
        # giving the same terminals a newname
        # S = aS
        # S1 = aS
        res = []
        count = 0
        for rule in rules:
            count += 1
            if self.is_terminal(rule):
                res.append(rule)
                continue
            S = self.find_common_nonterminal(rule)
            if S:
                lhs = Nonterminal('{}_{}'.format(S,count))
                rhs = rule.rhs()
                new_production = Production(lhs, rhs)
                res.append(new_production)
            else:
                res.append(rule)
        return res
    def set_non_terminals(self, rule, count):

        res = []

        lhs = rule.lhs()

        rhs = rule.rhs()
        rule_remain = None
        while (len(rhs) > 2):
            k = Nonterminal('{}_{}'.format(rhs[1], count * 10))
            rule_to_add = Production(lhs, [rhs[0], k])
            rule_remain = Production(k, rhs[1:])
            res.append(rule_to_add)
            lhs = rule_remain.lhs() # k
            rhs = rule_remain.rhs()

        res.append(rule_remain)





        '''
        NP -> DT-plr A-mas-plr-pre N-mas-plr
        A -> BCDE
        
        A -> BK1
        K1 -> CK2
        K2 -> DE
        
        '''



        # new_rule_rem = None
        # cur_rule = rule #  A -> BCDE
        # cur_rhs_len = len(rule.rhs()) # 4
        # index = 0
        # while cur_rhs_len > 2:
        #     print("generating new rules....")
        #     new_rhs = cur_rule.rhs() # BCDE
        #     k = Nonterminal('{}_{}'.format(rhs[index+1], count*10)) #k
        #
        #     new_rule = Production(lhs, [new_rhs[index], k]) #A -> Bk
        #
        #     new_rule_rem = Production(k, rhs[index+1:])# k -> CDE
        #     res.append(new_rule) # res += A -> Bk
        #     cur_rule = new_rule_rem # cur_rule = k -> CDE
        #     cur_rhs_len = len(new_rule.rhs())
        #
        #     lhs = k  # k
        #
        #     index += 1
        #
        # res.append(new_rule_rem)

        # res.append(self.setrule(lhs, (rhs[0], '{}_{}'.format(rhs[1], count*10))))
        # res.append(self.setrule('{}_{}'.format(rhs[1], count*10), (rhs[1],rhs[2])))

        return res
        # rhs = (A B C D)
        #lhs = =(E)
        # E-> ABCD
        # E-> PD
        # P -> AR
        # R -> BC
    def setrule(self, lhs, rhs):
        lhs = Nonterminal('{}'.format(lhs))
        res_rhs_list = [rhs]
        for term in rhs:
            newterm = Nonterminal(term)
            res_rhs_list.append(newterm)
        res_rhs_tuple = tuple(res_rhs_list)
        newproduction = Production(lhs, res_rhs_tuple)
        return newproduction
    def filter_none(self, rules):
        res = []
        for rule in rules:
            if len(rule.rhs())==0:
                continue
            res.append(rule)
        return res
    def is_unary(self, rule):
        if rule.is_nonlexical() and len(rule.rhs()) == 1:
            return True
        return False
    ## non terminal =>
    #

    def remove_generated_terminals(self, tree):
        children = self.children(tree)
        if len(children) == 1 and nltk.grammar.is_terminal(children[0]):
            return tree
        else:
            res = []
            for child in children:
                res.append(self.remove_generated_terminals(child))
            children_refresh = []
            for child in res:
                cur_label = child.label()
                if '_' in str(cur_label):
                    # only generated labels have "_"
                    cur = self.children(child)
                    for n_child in cur:
                        # get the children of the generated labels
                        children_refresh.append(n_child)
                else:
                    children_refresh.append(child)
            return Tree(tree.label(), children_refresh)

                ###





    def replace_unary(self, rules):
        can_extend = True
        to_remove = set()
        # new_rules = list(set(rules))
        res = []
        new_rules = set(rules)
        while (can_extend):
            # new_rules = list(set(self.rules))
            # added = 0
            # new_rules = list(set(new_rules))
            new_rules = set(rules)
            # before_len = len(new_rules)
            # for rule in new_rules:
            for rule in rules:
                # search for the unary rule
                # if self.is_unary(rule) and rule not in to_remove:
                if self.is_unary(rule):
                    # if the unary rule exists
                    rhs = rule.rhs()
                    # from the unary rule's rhs, search for other rules
                    # for other_rule in new_rules:
                    for other_rule in rules:
                        if other_rule.lhs() == rhs[0]:
                            # print("current lhs: {}, currnet rhs: {}".format(other_rule.lhs(), other_rule.rhs()[0]))
                            new_rule = Production(rule.lhs(), other_rule.rhs())
                            # print("new_rule: {}".format(new_rule))
                            # new_rules.append(new_rule)
                            new_rules.add(new_rule)
                            to_remove.add(rule)
            # after_len = len(new_rules)
            # if before_len == after_len:
            #     can_extend = False
            if set(new_rules) == set(rules):
                can_extend = False
            rules = new_rules
        res = list(new_rules)
        for rm in to_remove:

            if rm in new_rules and rm.is_nonlexical():

                res.remove(rm)
                # new_rules.remove(rm)
        return res



    def pseudor(self):
        '''
            can extend = true
            to be removed = a SET
            while can_extend
                new grammar = set(grammar)
                for rule in grammar:
                    if rule is unary ( A -> B, B not lexical)
                    then
                        rhs = rule.rhs
                        for other_rule in grammar:
                            if other_rule.lhs = rhs (B -> something)
                            then
                                new rule = rule.lhs -> other_rule.rhs ( A -> something)
                                new grammar .append new rule
                                to be removed .append rule (A -> B)
                if new grammar == grammar
                then can_extend = false

                grammar = new grammar
        :return:
        '''

        '''
        A-B B-C C-D D-'fd'
        toberemoved = none
        A-B B-C C-D D-'fd' A-C B-D C-'fd'
        toberemoved = A-B B-C C-D
        A-B B-C C-D D-'fd' A-C B-D C-'fd' A-D B-'fd' C-'fd'
        toberemoved = A-B B-C C-D A-C B-D
        A-B B-C C-D D-'fd' A-C B-D C-'fd' A-D B-'fd' C-'fd' A-'fd'
        toberemoved = A-B B-C C-D A-C B-D A-D
        while loop finished
        
        we get D-'fd' C-'fd' B-'fd' A-'fd'
        
        '''
        pass
    # def replace_lex(self, rules):
    #     res = []
    #     for rule in rules:
    #         if rule.is_lexical() and len(rule.rhs() > 1):
    #             cur_rhs = [t for t in list(rule.rhs() if t.) ]
    def to_chomsky_normal(self):
        # print(len(self.rules))
        self.normal_rules = self.rules
        self.normal_rules = self.replace_unary(self.normal_rules)

        res = []
        count = 0
        for rule in self.normal_rules:
            count += 1

            # if the rhs_length > 2
            if len(rule.rhs()) > 2:
                splitted_rules = self.set_non_terminals(rule, count)
                for r in splitted_rules:
                    res.append(r)
            else:
                res.append(rule)
        self.normal_rules = res

        # print("filtering same nonterminals in lhs and rhs ...")
        self.normal_rules = self.filter_terminals(self.normal_rules)
        # print("succeed")
        # print(len(self.normal_rules))

        # print("filter none-pointers in grammar rules...")
        self.normal_rules = self.filter_none(self.normal_rules)
        # print("succeed")



        # print(self.rules)

        # print("filtering unaries...")

        # print("succeed")

        # lhs = nltk.grammar.Nonterminal('PropN')
        # rhs = nltk.grammar.Nonterminal('David')
        # new_production = nltk.grammar.Production(lhs, [rhs])
        # rules = grammar.productions()
        # rules.append(new_production)

        # print("====================================")

        # for i in self.normal_rules:
            # if len(i.rhs()) > 2:
            #     print(i)
        self.normal_rules = self.filter_none(self.normal_rules)
        # print(len(self.normal_rules))

    def cykparse(self):
        S = Nonterminal("S")
        length = len(self.sentence)
        if length == 0:
            print("sentence is not passed to the cyk-parser! please add a sentence!")
            return []
        self.matrix = [[{} for _ in range(length)]for i in range(length)]

        mat = self.matrix
        for m, word in enumerate(self.sentence):
            for rule in self.normal_rules:
                if word in rule.rhs():
                    mat[m][m][rule.lhs()] = word
        ############
        for l in range(1, length):
            # each tag length

            for m in range(0, length-l):
                # each left endpoints

                for k in range(m, m+l):
                    # sentence_fragment splitting point

                    for rule in self.normal_rules:
                        if rule.rhs()[0] in mat[m][k] \
                            and rule.rhs()[1] in mat[k+1][m+l]:
                            mat[m][m+l][rule.lhs()] = k
        # if mat[0][length-1].keys() != None:
        #     self.is_correct = True
        if S in mat[0][length-1].keys():
            self.is_correct = True
            res = []
            for k in mat[0][length-1].values():


                cur = self.Trace_back(0, length-1)
                res.append(cur)
            self.trees = res
            return res
        else:
            self.is_correct = False
            return []
    # def Pick_from(self):

    """
           base case: list of all rules that generate the leaf (in form of trees)
           [Tree(rule, word)]

           inductive step:
           i-j cell
           result = []
           for lhs, k in this cell:

               left-possible trees = traceback(k's left) - list of trees
               right-possible trees = traceback(k's right) - list of trees
               for left in left-possible trees:
                   for right in right-possible trees:
                       if is_a_rule(lhs -> left.root right.root)
                           result.append(Tree(lhs, [left, right])
           return result
           :return:
    """
    def children(self, tree):
        return [children for children in tree]
    def is_rule(self, lhs, rhs):

        if Production(lhs, rhs) in self.normal_rules:
            return True
        return False
    def Trace_back(self, i, j):
        mat = self.matrix
        if j == i:
            res = []
            for non_term in mat[i][i].keys():
                # find all non_terminals in mat[i][i]
                res.append(Tree(non_term, [mat[i][i][non_term]]))
            return res
        else:
            res = []
            cur_cell = mat[i][j]
            # recursive case
            #
            for lhs in cur_cell.keys():
                k = cur_cell[lhs]
                left_possible = self.Trace_back(i, k)
                right_possbile = self.Trace_back(k+1, j)
                # iterate all possible trees in the left and right hand side
                for l in left_possible:
                    for r in right_possbile:
                        if self.is_rule(lhs, [l.label(), r.label()]):
                            res.append(Tree(lhs, [l, r]))

            return res
    def get_trees(self):

        return self.trees[0]
    def printTree(self):
        if self.is_correct:
            trees = self.get_trees()
            for tree in trees:

                print("=================== original tree ======================= ")
                Tree.fromstring(str(tree)).pretty_print()
                print("=============removed own terminals tree ================= ")
                Tree.fromstring(str(self.remove_generated_terminals(tree))).pretty_print()
        else:
            print("The sentence '{}' is not accepted by the french grammar".format(" ".join(self.sentence)))
        # Tree.fromstring(str(self.remove_generated_terminals(self.trees[0][i]))).pretty_print()
        # tree_len = len(self.trees[0])

        # for i in range(tree_len):
        #     # Tree.fromstring(str(self.trees[0][i])).pretty_print()
        #     print("removed own terminals tree ============================")
        #     Tree.fromstring(str(self.remove_generated_terminals(self.trees[0][i]))).pretty_print()
            # Tree.fromstring(str(self.trees[0][i])).pretty_print()









    def pseudo(self):

        pass

    def print_square_mat(self):
        for i in range(len(self.matrix)):
            print(self.matrix[i])

    def run(self, file, sentence):
        self.set_rules(file)
        self.set_sentence(sentence)
        self.to_chomsky_normal()
        self.cykparse()
        print("========================= square matrix =========================")
        self.print_square_mat()
        print("========================= trees =================================")
        self.printTree()





















# class Tree(object):
if __name__ == "__main__":
    test = cyk_parser()
    test.set_rules("french-grammar.txt")
    test.set_sentence('je ne regarde pas la television') ## success
    # test.set_sentence('tu ne regardes pas la television') ## success
    # test.set_sentence('il regarde la television') ## success
    # test.set_sentence('je regarde la television') ## success
    # test.set_sentence('tu regardes la television') ## success
    # test.set_sentence('ju ne regarde pas la television')
    # test.set_sentence('nous ne regardons pas la television') ## success
    test.to_chomsky_normal()
    test.cykparse()
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
    # print(test.trees)
    test.print_square_mat()
    print("===================================================")

    # print(test.trees)
    test.printTree()
    # Tree.fromstring(str(test.trees[0][0])).pretty_print()
    # Tree.fromstring(str(test.remove_generated_terminals(test.trees[0][0]))).pretty_print()
    # for i in test.normal_rules:
    #     print(i)

    # k = Tree().
    test2 = cyk_parser()
    test2.run("french-grammar.txt", "il regarde la television")

    test3 = cyk_parser()
    test3.run("french-grammar.txt", 'les aides aiment')

    test4 = cyk_parser()
    test4.run('french-grammar.txt', 'nous ne regardons pas la television')

    test6 = cyk_parser()
    test6.run("french-grammar.txt", 'jonathan aime le petit chat')

    test7 = cyk_parser()
    test7.run('french-grammar.txt', "les aides aiment Montreal")


    print("incorrect examples:")
    test5 = cyk_parser()
    test5.run("french-grammar.txt", 'je ne regardons pas la television')

