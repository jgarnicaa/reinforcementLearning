tic_tac_toe = TicTacToe(TIC_TAC_TOE)
tic_tac_toe_tree = TicTacToeTree(tic_tac_toe)


def opponent_policy(
    tree_node: Tree.Node,
    opponent_pol: Dict[Tree.Node, Tuple[Tuple[Tree.Node, str], float]],
) -> List[Tuple[float, Tree.Node]]:
    if (
        opponent_pol is not None
        and tree_node in opponent_pol
        and opponent_pol[tree_node][0][0] is not None
    ):
        return [(1.0, opponent_pol[tree_node][0][0])]
    else:
        num_samples = len(tic_tac_toe_tree.get_children(tree_node))
        return [
            (1.0 / float(num_samples), n)
            for n, _ in tic_tac_toe_tree.get_children(tree_node)
        ]


def call_game_rtdp(
    tree: Tree,
    node: Tree.Node,
    opponent_pol: Dict[Tree.Node, Tuple[Tuple[Tree.Node, str], float]],
    max_value: float,
    max_or_min_player: bool,
) -> None:
    domain_factory = lambda: ProbabilisticGameDomain(
        tree,
        node,
        lambda tree_node: opponent_policy(tree_node, opponent_pol),
        max_or_min_player,
    )
    rtdp_factory = lambda: LRTDP(
        domain_factory=domain_factory,
        heuristic=lambda d, s: (
            Value(reward=max_value) if max_or_min_player else Value(cost=max_value)
        ),
        discount=1.0,
        epsilon=0.001,
        parallel=False,
        verbose=False,
    )
    with rtdp_factory() as rtdp:
        rtdp.solve()
        node._best_child = rtdp.sample_action(node)
        policy = rtdp.get_policy()

    return policy


node = tic_tac_toe_tree.get_node(data=tic_tac_toe.reset())
tic_tac_toe.render(node.data)
current_opponent_policy = None

while not node.terminal:
    print("Player {}'s turn".format("Cross" if node.max_player else "Circle"))
    current_opponent_policy = call_game_rtdp(
        tic_tac_toe_tree, node, current_opponent_policy, 1, node.max_player
    )

    node = node.best_child[0]
    tic_tac_toe.render(node.data)
