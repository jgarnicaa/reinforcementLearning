"""
Utilities for Job Shop Scheduling Problems.

This module provides visualization and helper functions for working with
Job Shop problems and solutions.
"""

import os
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon as mpl_Polygon
from matplotlib.font_manager import FontProperties
from shapely.geometry import Polygon

from scheduling.lesson2_cpsat.jobshop_problem import JobShopProblem, SolutionJobshop, Subjob
from scheduling.utils.parsers import parse_jobshop_file


def plot_solution(
    solution: SolutionJobshop,
    problem: JobShopProblem,
    figsize=(12, 6)
):
    """
    Create a Gantt chart visualization of a Job Shop solution.

    Each machine is shown as a horizontal line, with colored rectangles
    representing scheduled operations. Operations are labeled with their
    (job_id, operation_id).

    Args:
        solution: The solution to visualize
        problem: The problem specification
        figsize: Figure size (width, height)

    Returns:
        Tuple of (fig, ax) matplotlib objects

    Example:
        >>> fig, ax = plot_solution(solution, problem)
        >>> plt.show()
    """
    fig, ax = plt.subplots(1, figsize=figsize)
    patches = []

    # For each machine, plot all operations scheduled on it
    for machine in problem.job_per_machines:
        for job_id, subjob_id in problem.job_per_machines[machine]:
            time_start, time_end = solution.schedule[job_id][subjob_id]

            # Create a rectangle for this operation
            polygon = Polygon([
                (time_start, machine - 0.3),
                (time_end, machine - 0.3),
                (time_end, machine + 0.3),
                (time_start, machine + 0.3),
                (time_start, machine - 0.3),
            ])

            # Label with (job_id, operation_id)
            ax.annotate(
                f"({job_id},{subjob_id})",
                xy=((3 * time_start + time_end) / 4, machine),
                font_properties=FontProperties(size=8, weight="bold"),
                verticalalignment="center",
                horizontalalignment="left",
                color="k",
                clip_on=True,
            )

            # Draw rectangle border
            x, y = polygon.exterior.xy
            ax.plot(x, y, zorder=-1, color="b")
            patches.append(mpl_Polygon(xy=polygon.exterior.coords))

    # Add colored patches
    p = PatchCollection(
        patches,
        cmap=matplotlib.colormaps.get_cmap("Blues"),
        alpha=0.4
    )
    ax.add_collection(p)

    # Configure axes
    ax.set_yticks(range(problem.n_machines))
    ax.set_yticklabels(
        [f"Machine {j}" for j in range(problem.n_machines)],
        fontdict={"size": 9}
    )
    ax.set_xlabel("Time", fontsize=11)
    ax.set_title(f"Job Shop Schedule (Makespan: {solution.get_makespan()})", fontsize=13)
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    return fig, ax


def create_simple_example() -> JobShopProblem:
    """
    Create a simple 3-job, 3-machine example problem.

    This is the example used in the notebook:
    - Job 0: Machine 0 (3 units), Machine 1 (2 units), Machine 2 (2 units)
    - Job 1: Machine 0 (2 units), Machine 2 (1 unit), Machine 1 (4 units)
    - Job 2: Machine 1 (4 units), Machine 2 (3 units)

    Returns:
        A small JobShopProblem instance
    """
    job_0 = [
        Subjob(machine_id=0, processing_time=3),
        Subjob(machine_id=1, processing_time=2),
        Subjob(machine_id=2, processing_time=2)
    ]
    job_1 = [
        Subjob(machine_id=0, processing_time=2),
        Subjob(machine_id=2, processing_time=1),
        Subjob(machine_id=1, processing_time=4)
    ]
    job_2 = [
        Subjob(machine_id=1, processing_time=4),
        Subjob(machine_id=2, processing_time=3)
    ]

    return JobShopProblem(list_jobs=[job_0, job_1, job_2])


def load_instance(instance_name: str) -> JobShopProblem:
    """
    Load a Job Shop instance from the standard benchmark instances.

    Available instances include classic benchmarks like:
    - ft06, ft10, ft20: Fisher & Thompson instances
    - la01-la40: Lawrence instances
    - abz5-abz9: Adams, Balas & Zawack instances
    - orb01-orb10: Applegate & Cook instances
    - swv01-swv20: Storer, Wu & Vaccari instances
    - yn1-yn4: Yamada & Nakano instances
    - ta01-ta80: Taillard instances

    Args:
        instance_name: Name of the instance (e.g., "ft06", "la01")

    Returns:
        JobShopProblem object loaded from file

    Example:
        >>> problem = load_instance("ft06")
        >>> print(problem)
        JobShopProblem(jobs=6, machines=6, total_operations=36)
    """
    # Build path to instance file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(current_dir)
    instance_path = os.path.join(repo_root, "data", "jobshop", "instances", instance_name)

    if not os.path.exists(instance_path):
        raise FileNotFoundError(
            f"Instance '{instance_name}' not found at {instance_path}\n"
            f"Available instances are in: {os.path.join(repo_root, 'data', 'jobshop', 'instances')}"
        )

    # Parse the file
    problem_data, nb_jobs, nb_machines = parse_jobshop_file(instance_path)

    # Convert to our data structure
    list_jobs = []
    for job_operations in problem_data:
        job = [
            Subjob(machine_id=op["machine_id"], processing_time=op["processing_time"])
            for op in job_operations
        ]
        list_jobs.append(job)

    return JobShopProblem(list_jobs=list_jobs, n_jobs=nb_jobs, n_machines=nb_machines)


def compute_lower_bound(problem: JobShopProblem) -> int:
    """
    Compute a simple lower bound on the optimal makespan.

    This uses two bounds:
    1. Maximum total processing time across all jobs
    2. Maximum load on any single machine

    Args:
        problem: The job shop problem

    Returns:
        Lower bound on the makespan
    """
    # Bound 1: Longest job
    max_job_length = max(
        sum(subjob.processing_time for subjob in job)
        for job in problem.list_jobs
    )

    # Bound 2: Most loaded machine
    machine_loads = {i: 0 for i in range(problem.n_machines)}
    for job in problem.list_jobs:
        for subjob in job:
            machine_loads[subjob.machine_id] += subjob.processing_time

    max_machine_load = max(machine_loads.values())

    lower_bound = max(max_job_length, max_machine_load)

    return lower_bound


def print_problem_stats(problem: JobShopProblem):
    """
    Print statistics about a Job Shop problem.

    Args:
        problem: The problem to analyze
    """
    total_operations = sum(len(job) for job in problem.list_jobs)
    total_processing = sum(
        subjob.processing_time
        for job in problem.list_jobs
        for subjob in job
    )

    print(f"\n{'='*60}")
    print(f"Job Shop Problem Statistics")
    print(f"{'='*60}")
    print(f"  Number of jobs: {problem.n_jobs}")
    print(f"  Number of machines: {problem.n_machines}")
    print(f"  Total operations: {total_operations}")
    print(f"  Total processing time: {total_processing}")
    print(f"  Lower bound (simple): {compute_lower_bound(problem)}")
    print(f"{'='*60}\n")
