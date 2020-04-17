from sys import stdin, stderr
from json import loads, dumps


def cnf(tree):
    n = len(tree)
    if n == 2:
        if isinstance(tree[0], str) and isinstance(tree[1], str):
            pass
        elif isinstance(tree[0], str) and isinstance(tree[1], list):
            tree[0] = tree[0] + "+" + tree[1][0]
            tree[1:] = tree[1][1:]

            cnf(tree)
    if n == 3:
        if isinstance(tree[0], str) and isinstance(tree[1], list) and isinstance(tree[2], list):
            cnf(tree[2])
            cnf(tree[1])
    if n > 3:
        if isinstance(tree[0], str) and (isinstance(x, list) for x in [tree[1:]]):
            new_lable = tree[0] + "|" + tree[1][0]
            extral_list = list()
            extral_list.append(new_lable)
            extral_list.extend(tree[2:].copy())
            tree[2:] = []
            tree.append(extral_list)
            cnf(tree)


def is_cnf(tree):
    n = len(tree)
    if n == 2:
        return isinstance(tree[1], str)
    elif n == 3:
        return is_cnf(tree[1]) and is_cnf(tree[2])
    else:
        return False


def words(tree):
    if isinstance(tree, str):
        return [tree]
    else:
        ws = []
        for t in tree[1:]:
            ws = ws + words(t)
        return ws


if __name__ == "__main__":

    for line in stdin:
        tree = loads(line)
        sentence = words(tree)

        input = str(dumps(tree))
        cnf(tree)
        if is_cnf(tree) and words(tree) == sentence:
            print(dumps(tree))
        else:
            print("Something went wrong!", file=stderr)
            print("Sentence: " + " ".join(sentence), file=stderr)
            print("Input: " + input, file=stderr)
            print("Output: " + str(dumps(tree)), file=stderr)
            exit()
