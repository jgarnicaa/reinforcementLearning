class D(MDPDomain, Goals, Renderable):
    T_state = Tree.Node  # Type of states
    T_observation = T_state  # Type of observations
    T_event = Tuple[Tree.Node, str]  # Type of events/actions
    T_value = float  # Type of transition values (rewards or costs)
    T_info = None  # Type of additional information in environment outcome


class ProbabilisticGameDomain(D):
    def __init__(
        self,
        game_tree: Tree,
        root_node: Tree.Node,
        opponent_policy: Callable[[Tree.Node], List[Tuple[float, Tree.Node]]],
        max_or_min_player: bool = True,
    ):
        self._game_tree = game_tree
        self._game_root_node = root_node
        self._opponent_policy = opponent_policy
        self._max_or_min_player = max_or_min_player

    def _is_terminal(self, state: D.T_state) -> D.T_predicate:
        return self._game_tree.is_terminal(state)

    def _get_transition_value(
        self,
        memory: D.T_state,
        action: D.T_event,
        next_state: Optional[D.T_state] = None,
    ) -> Value[D.T_value]:
        return Value(
            reward=(
                (2 * int(self._max_or_min_player) - 1) * next_state.terminal_value
                if next_state.terminal and memory != next_state
                else 0.0
            )
        )

    def _get_next_state_distribution(
        self, memory: D.T_state, action: D.T_event
    ) -> DiscreteDistribution[D.T_state]:
        if self._game_tree.is_terminal(action[0]):
            return DiscreteDistribution([(action[0], 1.0)])
        else:
            return DiscreteDistribution(
                [
                    (next_tree_node, probability)
                    for probability, next_tree_node in self._opponent_policy(action[0])
                ]
            )

    def _get_action_space_(self) -> Space[D.T_event]:
        pass

    def _get_applicable_actions_from(self, memory: D.T_state) -> Space[D.T_event]:
        if memory.terminal:
            return ListSpace([(memory, "TERMINAL")])
        else:
            return ListSpace(self._game_tree.get_children(memory))

    def _get_goals_(self) -> Space[D.T_observation]:
        return ImplicitSpace(lambda s: self._game_tree.is_terminal(s))

    def _get_initial_state_(self) -> D.T_state:
        return self._game_root_node

    def _get_observation_space_(self) -> Space[D.T_observation]:
        pass

    def _render_from(self, memory: D.T_state, **kwargs: Any) -> Any:
        self._game_tree.render(memory)
