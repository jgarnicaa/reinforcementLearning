"""
Utility functions for TP1 - RCPSP

Builds on the utilities from Lesson 1 and adds TP-specific helpers.
"""

import os

from discrete_optimization.rcpsp.problem import RcpspProblem, RcpspSolution
from discrete_optimization.rcpsp.parser import parse_file, get_data_available
from discrete_optimization.datasets import fetch_data_from_psplib
from discrete_optimization.rcpsp.utils import plot_task_gantt, plot_ressource_view

from scheduling.utils.rcpsp_utils import (
    compute_predecessors,
    get_task_durations,
    get_resource_consumption,
)


def load_instance(filename: str = None, instance_name: str = "j301_1") -> RcpspProblem:
    """
    Load an RCPSP instance from PSPLib.

    Args:
        filename: Full path to instance file (if provided, instance_name is ignored)
        instance_name: Instance name from PSPLib (e.g., "j301_1")

    Returns:
        Parsed RcpspProblem

    Example:
        >>> problem = load_instance(instance_name="j301_1")
        >>> problem = load_instance(filename="custom_problem.sm")
    """
    # Ensure datasets are available
    try:
        files = get_data_available()
    except:
        print("Downloading PSPLib datasets...")
        fetch_data_from_psplib()
        files = get_data_available()

    # Find the file
    if filename is not None:
        filepath = filename
    else:
        # Search for instance by name
        filepath = next((f for f in files if instance_name in f), None)
        if filepath is None:
            raise FileNotFoundError(f"Instance '{instance_name}' not found in PSPLib")

    # Parse and return
    problem = parse_file(filepath)
    print(f"✓ Loaded: {os.path.basename(filepath)}")
    return problem


def print_problem_stats(problem: RcpspProblem, detailed: bool = False):
    """
    Print statistics about an RCPSP problem.

    Args:
        problem: The RCPSP problem
        detailed: If True, print detailed information
    """
    print(f"\n{'='*60}")
    print(f"RCPSP Problem Statistics")
    print(f"{'='*60}")
    print(f"  Tasks: {problem.n_jobs}")
    print(f"  Resources: {list(problem.resources.keys())}")
    print(f"  Resource capacities: {problem.resources}")

    if detailed:
        print(f"\n  Task details (first 5):")
        for i, task_id in enumerate(list(problem.tasks_list)[:5]):
            mode_details = problem.mode_details[task_id][1]  # Mode 1
            duration = mode_details["duration"]
            resources = {r: mode_details.get(r, 0) for r in problem.resources_list}
            print(f"    Task {task_id}: duration={duration}, resources={resources}")

        print(f"\n  Precedence examples (first 5):")
        for i, task_id in enumerate(list(problem.tasks_list)[:5]):
            successors = problem.successors.get(task_id, [])
            if successors:
                print(f"    Task {task_id} → {successors}")

    print(f"{'='*60}\n")


def visualize_solution(problem: RcpspProblem, solution: RcpspSolution):
    """
    Visualize an RCPSP solution with Gantt charts.

    Args:
        problem: The RCPSP problem
        solution: The solution to visualize
    """
    print("\nGenerating Gantt charts...")
    plot_ressource_view(problem, solution)
    plot_task_gantt(problem, solution)


def compute_simple_lower_bound(problem: RcpspProblem) -> int:
    """
    Compute a simple lower bound on the optimal makespan.

    Uses two bounds:
    1. Sum of task durations on critical path (ignoring resources)
    2. Maximum resource load (total work / capacity)

    Args:
        problem: The RCPSP problem

    Returns:
        Lower bound value
    """
    from discrete_optimization.rcpsp.solvers.cpm import CpmRcpspSolver

    # Bound 1: Critical path (ignoring resources)
    cpm_solver = CpmRcpspSolver(problem)
    cpm_solver.run_classic_cpm()
    critical_path_length = cpm_solver.map_node[problem.sink_task]._EFD

    # Bound 2: Resource bottleneck
    resource_loads = {r: 0 for r in problem.resources_list}

    for task_id in problem.tasks_list:
        duration = problem.mode_details[task_id][1]["duration"]
        for resource in problem.resources_list:
            required = problem.mode_details[task_id][1].get(resource, 0)
            resource_loads[resource] += duration * required

    max_resource_bound = max(
        resource_loads[r] // problem.resources[r]
        for r in problem.resources_list
    )

    lower_bound = max(critical_path_length, max_resource_bound)

    print(f"Lower bounds:")
    print(f"  Critical path: {critical_path_length}")
    print(f"  Resource bottleneck: {max_resource_bound}")
    print(f"  Combined: {lower_bound}")

    return lower_bound


def compare_solutions(
    problem: RcpspProblem,
    solutions: dict,
    time_taken: dict = None
):
    """
    Compare multiple solutions for the same problem.

    Args:
        problem: The RCPSP problem
        solutions: Dict mapping method_name -> RcpspSolution
        time_taken: Optional dict mapping method_name -> time_in_seconds
    """
    print(f"\n{'='*70}")
    print("Solution Comparison")
    print(f"{'='*70}")
    print(f"{'Method':<20} {'Makespan':<12} {'Valid':<8} {'Time (s)':<10}")
    print(f"{'-'*20} {'-'*12} {'-'*8} {'-'*10}")

    for method_name, solution in solutions.items():
        makespan = problem.evaluate(solution)
        is_valid = problem.satisfy(solution)
        time_str = f"{time_taken[method_name]:.2f}" if time_taken and method_name in time_taken else "N/A"

        status = "✓" if is_valid else "✗"
        print(f"{method_name:<20} {makespan:<12.0f} {status:<8} {time_str:<10}")

    print(f"{'='*70}\n")
