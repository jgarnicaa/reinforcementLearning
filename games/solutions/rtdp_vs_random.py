tic_tac_toe = TicTacToe(TIC_TAC_TOE)
tic_tac_toe_tree = TicTacToeTree(tic_tac_toe)


def call_game_rtdp(
    tree: Tree,
    node: Tree.Node,
    opponent_policy: Callable[[Tree.Node], List[Tuple[float, Tree.Node]]],
    max_value: float,
) -> None:
    domain_factory = lambda: ProbabilisticGameDomain(tree, node, opponent_policy)
    rtdp_factory = lambda: LRTDP(
        domain_factory=domain_factory,
        heuristic=lambda d, s: Value(reward=max_value),
        discount=1.0,
        epsilon=0.001,
        parallel=False,
        verbose=False,
    )
    with rtdp_factory() as rtdp:
        rtdp.solve()
        node._best_child = rtdp.sample_action(node)


def call_random_player(tic_tac_toe_tree: TicTacToeTree, node: Tree.Node) -> None:
    node._best_child = random.sample(tic_tac_toe_tree.get_children(node), 1)[0]


def random_player_policy(node: Tree.Node) -> List[Tuple[float, Tree.Node]]:
    num_samples = len(tic_tac_toe_tree.get_children(node))
    return [
        (1.0 / float(num_samples), n) for n, _ in tic_tac_toe_tree.get_children(node)
    ]


node = tic_tac_toe_tree.get_node(data=tic_tac_toe.reset())
tic_tac_toe_fig = tic_tac_toe.render(node.data)

while not node.terminal:
    if node.max_player:
        call_game_rtdp(tic_tac_toe_tree, node, random_player_policy, 1)
    else:
        call_random_player(tic_tac_toe_tree, node)

    node = node.best_child[0]
    tic_tac_toe.render(node.data)
