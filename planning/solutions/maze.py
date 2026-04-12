class Maze:
    def __init__(self, maze_str: str = DEFAULT_MAZE):
        maze = []
        for y, line in enumerate(maze_str.strip().split("\n")):
            line = line.rstrip()
            row = []
            for x, c in enumerate(line):
                if c in {" ", "o", "x"}:
                    row.append(1)  # spaces are 1s
                    if c == "o":
                        self._start = State(x, y)
                    if c == "x":
                        self._goal = State(x, y)
                else:
                    row.append(0)  # walls are 0s
            maze.append(row)
        # self._render_maze = deepcopy(self._maze)
        self._maze = maze
        self._num_cols = len(maze[0])
        self._num_rows = len(maze)
        self._ax = None
        self._fig = None
        self._image = None

    def get_transition_state_and_cost(
        self, state: State, action: Action
    ) -> Tuple[State, float]:

        if action == Action.left:
            next_state = State(state.x - 1, state.y)
        if action == Action.right:
            next_state = State(state.x + 1, state.y)
        if action == Action.up:
            next_state = State(state.x, state.y - 1)
        if action == Action.down:
            next_state = State(state.x, state.y + 1)

        # If candidate next state is valid
        if (
            0 <= next_state.x < self._num_cols
            and 0 <= next_state.y < self._num_rows
            and self._maze[next_state.y][next_state.x] == 1
        ):
            return (
                next_state,
                abs(next_state.x - state.x)
                + abs(next_state.y - state.y),  # every move costs 1
            )
        else:
            return (state, 2)  # big penalty when hitting a wall

    def get_initial_state(self) -> State:
        return self._start

    def is_goal(self, state: State) -> bool:
        return state == self._goal

    def render(self, state: State, path: List[State] = None) -> Any:
        maze = deepcopy(self._maze)
        maze[self._goal.y][self._goal.x] = 0.7
        maze[state.y][state.x] = 0.3
        if path is not None:
            for s in path:
                maze[s.y][s.x] = 0.5
        if self._fig is None:
            self._fig, self._ax = plt.subplots(1)
            self._ax.set_aspect("equal")
            self._ax.set_xticks([])
            self._ax.set_yticks([])
            self._ax.invert_yaxis()
            self._image = self._ax.imshow(maze)
        else:
            self._image.set_data(maze)
        mo.output.replace(self._fig)
        time.sleep(0.001)
        return self._fig  # Return figure for Marimo to display


maze = Maze()
maze_fig = maze.render(maze.get_initial_state())
