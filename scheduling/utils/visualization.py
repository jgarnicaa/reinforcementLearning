"""
Visualization utilities for scheduling problems.
"""

import matplotlib.pyplot as plt
import networkx as nx
from typing import List, Hashable, Optional
from discrete_optimization.rcpsp.problem import RcpspProblem


def plot_predecessors_graph(
    rcpsp_problem: RcpspProblem,
    path: Optional[List[Hashable]] = None
) -> None:
    """
    Plot the precedence graph of an RCPSP problem.

    Args:
        rcpsp_problem: The RCPSP problem instance
        path: Optional critical path to highlight in red
    """
    graph_nx = rcpsp_problem.graph.to_networkx()

    # Add edge weights (negative duration for shortest path algorithms)
    for edge in graph_nx.edges():
        graph_nx[edge[0]][edge[1]]["neg_min_duration"] = -1
        if edge[1] == rcpsp_problem.sink_task:
            graph_nx[edge[0]][edge[1]]["neg_min_duration"] = -1

    # Compute positions based on longest path
    shortest_path_length = nx.shortest_path_length(
        graph_nx,
        source=rcpsp_problem.source_task,
        weight="neg_min_duration",
        method="bellman-ford"
    )

    length_to_nodes = {}
    for node, length in shortest_path_length.items():
        if -length not in length_to_nodes:
            length_to_nodes[-length] = []
        length_to_nodes[-length].append(node)

    # Determine the maximum layer depth to position the sink task
    max_layer_depth = max(length_to_nodes.keys())

    position = {}
    for length in sorted(length_to_nodes.keys()):
        nodes_in_layer = sorted(length_to_nodes[length])
        for i, node in enumerate(nodes_in_layer):
            position[node] = (length, i * 2)

    # Ensure the sink task is at the rightmost position
    sink_task = rcpsp_problem.sink_task
    if sink_task in position:
        position[sink_task] = (max_layer_depth + 2, 0)

    # Define colors
    sink_source_color = "#FFB000"  # Orange
    normal_task_color = "#648FFF"  # Blue
    node_color = [normal_task_color] * len(graph_nx.nodes())

    if rcpsp_problem.source_task in graph_nx.nodes():
        node_color[list(graph_nx.nodes()).index(rcpsp_problem.source_task)] = sink_source_color
    if rcpsp_problem.sink_task in graph_nx.nodes():
        node_color[list(graph_nx.nodes()).index(rcpsp_problem.sink_task)] = sink_source_color

    # Create figure
    fig, ax = plt.subplots(1, figsize=(18, 10))
    nx.draw_networkx(
        graph_nx,
        pos=position,
        node_color=node_color,
        node_size=1200,
        font_size=9,
        with_labels=True,
        width=1.5,
        edge_color="#A3A3A3",
        alpha=0.7,
        arrows=True,
        arrowsize=15,
        font_weight='bold'
    )

    # Highlight critical path if provided
    if path is not None:
        edges = [(e0, e1) for e0, e1 in zip(path[:-1], path[1:])]
        nx.draw_networkx_edges(
            graph_nx,
            pos=position,
            edgelist=edges,
            edge_color="red",
            width=10,
            ax=ax,
            arrows=True,
            arrowsize=15
        )

        # Highlight critical path nodes
        critical_nodes_set = set(path)
        node_colors_critical = []
        for node in graph_nx.nodes():
            if node in critical_nodes_set:
                node_colors_critical.append("red")
            elif node == rcpsp_problem.source_task or node == rcpsp_problem.sink_task:
                node_colors_critical.append(sink_source_color)
            else:
                node_colors_critical.append(normal_task_color)

        nx.draw_networkx_nodes(
            graph_nx,
            pos=position,
            node_color=node_colors_critical,
            node_size=1300,
            edgecolors="black",
            linewidths=1.5,
            ax=ax
        )

    plt.title("RCPSP Precedence Graph", fontsize=18)
    plt.xlabel("Task Layer/Depth", fontsize=12)
    plt.ylabel("Vertical Spacing (within layer)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()


def plot_gantt_chart(rcpsp_problem: RcpspProblem, solution) -> None:
    """
    Plot a Gantt chart for an RCPSP solution.

    Args:
        rcpsp_problem: The RCPSP problem instance
        solution: The solution to visualize
    """
    from discrete_optimization.rcpsp.utils import plot_task_gantt, plot_ressource_view

    plot_ressource_view(rcpsp_problem, solution)
    plot_task_gantt(rcpsp_problem, solution)
