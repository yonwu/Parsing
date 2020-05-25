SH = 0;
RE = 1;
RA = 2;
LA = 3;
labels = ["det", "nsubj", "case", "nmod", "root", "test"]


def attach_orphans(arcs, n):
    attached = []
    for (h, d, l) in arcs:
        attached.append(d)
    for i in range(1, n):
        if not i in attached:
            arcs.append((0, i, "root"))


def print_tree(root, arcs, words, indent):
    if root == 0:
        print(" ".join(words[1:]))
    children = [(root, i, l) for i in range(len(words)) for l in labels if (root, i, l) in arcs]
    for (h, d, l) in sorted(children):
        print(indent + l + "(" + words[h] + "_" + str(h) + ", " + words[d] + "_" + str(d) + ")")
        print_tree(d, arcs, words, indent + "  ")


def transition(trans, stack, buffer, arcs):
    if isinstance(trans, int):
        if trans == SH and len(buffer) > 0:
            stack.insert(0, buffer.pop(0))
        # add code for missing transitions: RE, (RA, label), (LA, label)
    elif isinstance(trans, tuple):
        if trans[0] == RA and trans[1] in labels:
            top = stack[0]
            second = stack[1]
            label = trans[1]
            arcs.append((second, top, label))
            stack.pop(0)
        elif trans[0] == LA and trans[1] in labels:
            top = stack[0]
            second = stack[1]
            label = trans[1]
            arcs.append((top, second, label))
            stack.pop(1)


def parse():
    words = "root book me the morning flight".split()
    stack = [0]
    buffer = [x for x in range(1, len(words))]
    arcs = []
    for trans in [SH, SH, (RA, "test"), SH, SH, SH, (LA, "test"), (LA, "test"), (RA, "test"),
                  (RA, "test")]:
        transition(trans, stack, buffer, arcs)
    attach_orphans(arcs, len(words))
    print_tree(0, arcs, words, "")


if __name__ == "__main__":
    parse()
