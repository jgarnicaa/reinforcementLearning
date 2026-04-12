def flight_graph_heuristic(flight_graph, n):
    return flight_graph.compute_great_circle_distance(n.data, flight_graph.arrival)


astar_fp = Astar(
    flight_graph,
    lambda n: flight_graph_heuristic(flight_graph, n),
    verbose=False,
    render=False,  # set to true if you want visual rendering of the search
)
solution_fp = astar_fp.solve_from(FlightGraph.Node(flight_graph.departure))
path_fp = [n[0].data for n in solution_fp[1]]
flight_map = flight_graph.render(path_fp[-1], path_fp)
