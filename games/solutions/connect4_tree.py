class Board:
    def __init__(self, board: ArrayLike):
        self._board = board

    def __hash__(self):
        return hash(tuple(self._board.astype(int).flatten()))

    def __eq__(self, other):
        return np.all(np.equal(self._board, other._board))

    def __str__(self):
        return str(self._board)

    def __repr__(self):
        return repr(self._board)

    @property
    def board(self):
        return self._board

    def copy(self):
        return Board(self._board.copy())


class Connect4Tree(Tree):
    # We will store the Connect4 boards in the tree nodes
    # I.e: Tree.Node._data is a Board (i.e. hashable numpy array) as defined in the Connect4 class

    def __init__(self):
        super().__init__()
        self._ax = None
        self._fig = None
        self._image = None

    def reset(self) -> Tree.Node:
        connect4 = Connect4()
        connect4.reset()
        return self.get_node(data=Board(connect4.board))

    def generate_children(self, node: Tree.Node) -> List[Tuple[Tree.Node, str]]:
        connect4 = Connect4()
        connect4.board = node.data.board.copy()

        for action in connect4.legal_actions():
            connect4.player = 2 * int(node.max_player) - 1
            saved_board = connect4.board.copy()
            obs, reward, done = connect4.step(action)
            next_board = connect4.board.copy()
            connect4.board = saved_board

            yield (
                Tree.Node(
                    data=Board(next_board),  # obs is not what we want here
                    max_player=not node.max_player,
                    terminal=done,
                    terminal_value=reward if done else 0,
                ),
                "Player {} on column {}".format(
                    "green" if node.max_player else "red", action
                ),
            )

    def render(self, node: Tree.Node) -> None:
        board_to_render = np.zeros(
            shape=(
                2 * node.data.board[::-1].shape[0] + 1,
                2 * node.data.board[::-1].shape[1] + 1,
            ),
            dtype=np.float32,
        )

        for r in range(int(board_to_render.shape[0] / 2) + 1):
            board_to_render[2 * r, :] = 0.7 * np.ones(board_to_render.shape[1])
        for c in range(int(board_to_render.shape[1] / 2) + 1):
            board_to_render[:, 2 * c] = 0.7 * np.ones(board_to_render.shape[0])

        if self._fig is None:
            self._fig, self._ax = plt.subplots(1)
            self._ax.set_aspect("equal")
            self._ax.set_xticks([])
            self._ax.set_yticks([])
            self._ax.invert_yaxis()
            self._image = self._ax.imshow(board_to_render, cmap="Greys", vmin=0, vmax=1)
        else:
            self._image.set_data(board_to_render)

        for r in range(node.data.board[::-1].shape[0]):
            for c in range(node.data.board[::-1].shape[1]):
                if node.data.board[::-1][r, c] == 1:
                    self._ax.scatter(
                        2 * c + 1, 2 * r + 1, facecolors="green", edgecolors="green"
                    )
                elif node.data.board[::-1][r, c] == -1:
                    self._ax.scatter(
                        2 * c + 1, 2 * r + 1, facecolors="red", edgecolors="red"
                    )

        mo.output.replace(self._fig)
        time.sleep(1)
        return self._fig  # Return figure for Marimo to display


connect4_tree = Connect4Tree()
connect4_fig = connect4_tree.render(connect4_tree.reset())
