def expectiminimax(
    node: ProbabilisticTree.StateNode,
    tree: ProbabilisticTree,
    depth: int,
    maximizing_player: bool,
    evaluate: Callable[[ProbabilisticTree.StateNode], float],
):
    if depth == 0 or tree.is_terminal(node):
        return evaluate(node)
    if maximizing_player:
        value = -float("inf")
        for child in tree.get_children(node):
            tentative = sum(
                cc[2] * expectiminimax(cc[0], tree, depth - 1, False, evaluate)
                for cc in child[0]._children
            )
            if tentative > value:
                node._best_child = child
                value = tentative
        return value
    else:
        value = float("inf")
        for child in tree.get_children(node):
            tentative = sum(
                cc[2] * expectiminimax(cc[0], tree, depth - 1, True, evaluate)
                for cc in child[0]._children
            )
            if tentative < value:
                node._best_child = child
                value = tentative
        return value
