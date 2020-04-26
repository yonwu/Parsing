"""
CKY algorithm from the "Natural Language Processing" course by Michael Collins
https://class.coursera.org/nlangp-001/class
"""
import sys
from sys import stdin, stderr
from time import time
from json import dumps

from collections import defaultdict
from pprint import pprint

from pcfg import PCFG
from tokenizer import PennTreebankTokenizer


def argmax(lst):
    return max(lst) if lst else (0.0, None)


def backtrace(back, bp):
    if len(back) == 4:
        return list(back[:2])
    elif len(back) == 6:
        c = back[0]
        c1 = back[1]
        c2 = back[2]
        min = back[3]
        mid = back[4]
        max = back[5]
        left_tree = bp[min, mid, c1]
        right_tree = bp[mid, max, c2]
        return [c, backtrace(left_tree, bp), backtrace(right_tree, bp)]


# ADD YOUR CODE HERE
# Extract the tree from the backpointers


def CKY(pcfg_info, norm_words):
    # ADD YOUR CODE HERE
    # IMPLEMENT CKY

    # NOTE: norm_words is a list of pairs (norm, word), where word is the word
    #       occurring in the input sentence and norm is either the same word,
    #       if it is a known word according to the grammar, or the string _RARE_.
    #       Thus, norm should be used for grammar lookup but word should be used
    #       in the output tree.
    # Initialize your charts (for scores and backpointers)
    grammar_preterminal = pcfg_info[0]
    grammar_binary = pcfg_info[1]
    syntax_categores = pcfg_info[2]
    binary_helper = pcfg_info[3]

    scores = defaultdict(float)
    bp = defaultdict(tuple)

    # Code for adding the words to the cahrt
    for index, word_pair in enumerate(norm_words, 1):
        word_norm = word_pair[0]
        for grammar in grammar_preterminal.keys():
            if word_norm in grammar:
                scores[(index - 1, index, grammar[0])] = grammar_preterminal[grammar]
                bp[(index - 1, index, grammar[0])] = (grammar[0], word_pair[1], index, index - 1)

    # Code for the dynamic programming part, where larger and larger subtrees are built
    for max in range(2, len(norm_words) + 1):
        for min in range(max - 2, -1, -1):
            for c in syntax_categores:
                best = 0.0
                back_pointer = tuple()
                for grammar in binary_helper[c]:
                    for mid in range(min + 1, max):
                        t1 = scores[(min, mid, grammar[0])]
                        t2 = scores[(mid, max, grammar[-1])]
                        candidate = t1 * t2 * grammar_binary[(c, grammar[0], grammar[-1])]
                        if candidate > best:
                            best = candidate
                            back_pointer = (c, grammar[0], grammar[-1], min, mid, max)
                scores[(min, max, c)] = best
                bp[(min, max, c)] = back_pointer

    # Below is one option for retrieving the best trees, assuming we only want trees with the "S" category
    # This is a simplification, since not all sentences are of the category "S"
    # The exact arguments also depends on how you implement your back-pointer chart.
    # Below it is also assumed that it is called "bp"
    # return backtrace(bp[0, n, "S"], bp)
    back = tuple()
    if bp[0, len(norm_words), "S"] != ():
        back = (0, len(norm_words), "S")
    else:
        hightest_score = 0
        for x in scores.keys():
            if scores[x] != 0 and x[:2] == (0, len(norm_words)):
                if scores[x] > hightest_score:
                    hightest_score = scores[x]
                    back = x

    return backtrace(bp[back], bp)


class Parser:
    def __init__(self, pcfg):
        self.pcfg = pcfg
        self.tokenizer = PennTreebankTokenizer()
        self.pcfg_info = list()

    def extract_info_from_pcfg(self):
        grammar_preterminal = self.pcfg.q1
        grammar_binary = self.pcfg.q2

        syntax_categores = set([])
        for key in grammar_binary.keys():
            syntax_categores.add(key[0])
        binary_helper = {}
        for c in syntax_categores:
            binary_helper[c] = list()
            for grammar in grammar_binary.keys():
                if grammar[0] == c:
                    binary_helper[c].append((grammar[1], grammar[-1]))

        self.pcfg_info.append(grammar_preterminal)
        self.pcfg_info.append(grammar_binary)
        self.pcfg_info.append(syntax_categores)
        self.pcfg_info.append(binary_helper)

    def parse(self, sentence):
        words = self.tokenizer.tokenize(sentence)
        norm_words = []
        for word in words:  # rare words normalization + keep word
            norm_words.append((self.pcfg.norm_word(word), word))
        tree = CKY(self.pcfg_info, norm_words)
        tree[0] = tree[0].split("|")[0]
        return tree


def display_tree(tree):
    pprint(tree)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("usage: python3 parser.py GRAMMAR")
        exit()

    start = time()
    grammar_file = sys.argv[1]
    print("Loading grammar from " + grammar_file + " ...", file=stderr)
    pcfg = PCFG()
    pcfg.load_model(grammar_file)
    parser = Parser(pcfg)
    # Add one step out of real parsing to extract information from pcfg which takes 13 seconds
    parser.extract_info_from_pcfg()
    print("Time: (%.2f)s\n" % (time() - start), file=stderr)

    print("Parsing sentences ...", file=stderr)
    sentences = [sentence.strip() for sentence in stdin]

    for sentence in stdin:
        print("processing one sentence: ", file=stderr)
        tree = parser.parse(sentence)
        print(dumps(tree))
        print("Time: (%.2f)s\n" % (time() - start), file=stderr)
    print("Time: (%.2f)s\n" % (time() - start), file=stderr)
