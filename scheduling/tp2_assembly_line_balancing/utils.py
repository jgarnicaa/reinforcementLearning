"""
Utility functions for TP2 - Resource-Constrained Assembly Line Balancing

Provides helpers for:
- Creating problem instances
- Visualizing solutions
- Computing lower bounds
"""

from typing import Dict, List, Tuple
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from discrete_optimization.rcpsp.problem import RcpspProblem
from discrete_optimization.rcpsp.parser import get_data_available, parse_file
from discrete_optimization.datasets import fetch_data_from_psplib

from scheduling.tp2_assembly_line_balancing.problem import (
    RCALBPProblem,
    RCALBPSolution,
    Task,
    Station,
    Resource,
)


def create_simple_instance(
    nb_stations: int = 3,
    nb_tasks: int = 10,
    nb_resources: int = 2,
    seed: int = 42,
) -> RCALBPProblem:
    """
    Create a simple random RC-ALBP instance with readable names.

    Args:
        nb_stations: Number of workstations
        nb_tasks: Number of tasks
        nb_resources: Number of resource types
        seed: Random seed for reproducibility

    Returns:
        RCALBPProblem instance
    """
    random.seed(seed)

    # Create readable task names
    tasks = [f"T{i+1}" for i in range(nb_tasks)]
    stations = [f"WS{i+1}" for i in range(nb_stations)]
    resources = [f"R{i+1}" for i in range(nb_resources)]

    # Generate task processing times (1-10 time units)
    task_times = {t: random.randint(1, 10) for t in tasks}

    # Generate precedence constraints (ensure acyclic)
    precedences = []
    for i in range(nb_tasks - 1):
        # Each task can have 0-2 successors
        nb_successors = random.randint(0, min(2, nb_tasks - i - 1))
        successor_indices = random.sample(range(i + 1, nb_tasks), nb_successors)
        for succ_idx in successor_indices:
            precedences.append((tasks[i], tasks[succ_idx]))

    # Generate resource allocation to stations
    station_resources = {}
    for r in resources:
        for s in stations:
            # Random allocation between 2-5 units
            station_resources[(r, s)] = random.randint(2, 5)

    # Generate task resource consumption
    task_resources = {}
    for r in resources:
        for t in tasks:
            # 0-2 units consumption
            task_resources[(r, t)] = random.randint(0, 2)

    return RCALBPProblem(
        task_times=task_times,
        precedences=precedences,
        stations=stations,
        resources=resources,
        station_resources=station_resources,
        task_resources=task_resources,
    )


def create_precedence_example() -> RCALBPProblem:
    """
    Create a small example with clear precedence structure and meaningful names.

    Task structure:
        Prepare → Assemble → Test
           ↓         ↓        ↓
        Cut    →  Join  →  Package

    Returns:
        RCALBPProblem instance
    """
    # Define tasks with meaningful names
    tasks = ["Prepare", "Assemble", "Cut", "Join", "Test", "Package"]

    task_times = {
        "Prepare": 5,
        "Assemble": 3,
        "Cut": 4,
        "Join": 3,
        "Test": 2,
        "Package": 6,
    }

    precedences = [
        ("Prepare", "Assemble"),
        ("Prepare", "Cut"),
        ("Assemble", "Test"),
        ("Assemble", "Join"),
        ("Cut", "Join"),
        ("Test", "Package"),
        ("Join", "Package"),
    ]

    # Define stations and resources with names
    stations = ["Station_A", "Station_B"]
    resources = ["Worker", "Tool"]

    # Resource allocation: {(resource, station): amount}
    station_resources = {
        ("Worker", "Station_A"): 3,
        ("Worker", "Station_B"): 2,
        ("Tool", "Station_A"): 2,
        ("Tool", "Station_B"): 3,
    }

    # Task resource consumption: {(resource, task): amount}
    task_resources = {
        ("Worker", "Prepare"): 1,
        ("Worker", "Assemble"): 0,
        ("Worker", "Cut"): 1,
        ("Worker", "Join"): 0,
        ("Worker", "Test"): 1,
        ("Worker", "Package"): 2,
        ("Tool", "Prepare"): 0,
        ("Tool", "Assemble"): 1,
        ("Tool", "Cut"): 1,
        ("Tool", "Join"): 1,
        ("Tool", "Test"): 1,
        ("Tool", "Package"): 1,
    }

    return RCALBPProblem(
        task_times=task_times,
        precedences=precedences,
        stations=stations,
        resources=resources,
        station_resources=station_resources,
        task_resources=task_resources,
    )


def visualize_solution(
    problem: RCALBPProblem,
    solution: RCALBPSolution,
    show: bool = True,
) -> plt.Figure:
    """
    Visualize the assembly line solution as a Gantt chart.

    Args:
        problem: Problem instance
        solution: Solution to visualize
        show: Whether to display the plot

    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(12, max(6, problem.nb_stations * 1.5)))

    # Color map for tasks
    colors = plt.cm.Set3(range(problem.nb_tasks))
    task_colors = {t: colors[i % len(colors)] for i, t in enumerate(problem.tasks)}

    # Draw tasks as bars
    for station in problem.stations:
        station_tasks = [
            t for t, s in solution.task_assignment.items() if s == station
        ]

        for task in station_tasks:
            if task not in solution.task_schedule:
                continue

            start = solution.task_schedule[task]
            duration = problem.task_times[task]

            # Draw task bar
            ax.barh(
                station,
                duration,
                left=start,
                height=0.6,
                color=task_colors[task],
                edgecolor='black',
                linewidth=1.5,
                alpha=0.8,
            )

            # Add task label
            ax.text(
                start + duration / 2,
                station,
                f'T{task}\n({duration})',
                ha='center',
                va='center',
                fontsize=9,
                fontweight='bold',
            )

    # Format plot
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Station', fontsize=12)
    ax.set_title(f'Assembly Line Schedule (Cycle Time: {solution.cycle_time})', fontsize=14)
    ax.set_yticks(problem.stations)
    ax.set_yticklabels([f'Station {s}' for s in problem.stations])
    ax.grid(axis='x', alpha=0.3)

    # Add cycle time line
    if solution.cycle_time:
        ax.axvline(
            solution.cycle_time,
            color='red',
            linestyle='--',
            linewidth=2,
            label=f'Cycle Time: {solution.cycle_time}',
        )
        ax.legend()

    plt.tight_layout()

    if show:
        plt.show()

    return fig


def create_from_rcpsp(
    rcpsp_problem: RcpspProblem,
    nb_stations: int = 3,
    seed: int = 42,
) -> RCALBPProblem:
    """
    Create a realistic RC-ALBP instance from an RCPSP problem.

    This converts a project scheduling problem into an assembly line balancing
    problem by:
    - Using RCPSP tasks, durations, and precedences
    - Splitting RCPSP global resources across stations
    - Using RCPSP resource consumption per task

    Args:
        rcpsp_problem: RCPSP problem instance
        nb_stations: Number of assembly line stations
        seed: Random seed for resource allocation

    Returns:
        RCALBPProblem instance
    """
    random.seed(seed)

    # Tasks: Use RCPSP tasks with string names
    task_times = {
        f"T{task}": rcpsp_problem.mode_details[task][1]["duration"]
        for task in rcpsp_problem.tasks_list
    }

    # Precedences: Convert RCPSP precedences
    precedences = []
    for task in rcpsp_problem.tasks_list:
        for succ in rcpsp_problem.successors.get(task, []):
            precedences.append((f"T{task}", f"T{succ}"))

    # Stations: Create station names
    stations = [f"WS{i+1}" for i in range(nb_stations)]

    # Resources: Use RCPSP resources
    resources = [f"R{r}" for r in rcpsp_problem.resources_list]

    # Resource allocation: Give each station enough capacity
    # Strategy: Each station gets the FULL global capacity to ensure feasibility
    # This makes the problem easier but more realistic for assembly lines
    # (stations can be equipped with same resource levels)
    station_resources = {}
    for r_idx, r_name in enumerate(rcpsp_problem.resources_list):
        total_capacity = rcpsp_problem.resources[r_name]

        # Give each station the full capacity (or a generous portion)
        # This ensures the problem is feasible
        for s_idx, station in enumerate(stations):
            # Each station gets full capacity
            station_resources[(f"R{r_name}", station)] = total_capacity

    # Task resource consumption: Use RCPSP consumption
    task_resources = {}
    for task in rcpsp_problem.tasks_list:
        for r_name in rcpsp_problem.resources_list:
            consumption = rcpsp_problem.mode_details[task][1].get(r_name, 0)
            task_resources[(f"R{r_name}", f"T{task}")] = consumption

    return RCALBPProblem(
        task_times=task_times,
        precedences=precedences,
        stations=stations,
        resources=resources,
        station_resources=station_resources,
        task_resources=task_resources,
    )


def load_rcpsp_as_albp(
    instance_name: str = "j301_1",
    nb_stations: int = 3,
    seed: int = 42,
) -> RCALBPProblem:
    """
    Load an RCPSP instance from PSPLib and convert to RC-ALBP.

    Args:
        instance_name: Name of RCPSP instance (e.g., "j301_1")
        nb_stations: Number of assembly line stations
        seed: Random seed for resource allocation

    Returns:
        RCALBPProblem instance
    """
    # Load RCPSP instance
    try:
        files = get_data_available()
    except:
        fetch_data_from_psplib()
        files = get_data_available()

    matching_files = [f for f in files if instance_name in f]
    if not matching_files:
        raise ValueError(f"No RCPSP instance found matching '{instance_name}'")

    filepath = matching_files[0]
    rcpsp_problem = parse_file(filepath)

    # Convert to RC-ALBP
    return create_from_rcpsp(rcpsp_problem, nb_stations=nb_stations, seed=seed)


def print_solution_info(problem: RCALBPProblem, solution: RCALBPSolution):
    """
    Print detailed information about a solution.

    Args:
        problem: Problem instance
        solution: Solution to analyze
    """
    print("=" * 60)
    print("SOLUTION INFORMATION")
    print("=" * 60)

    # Evaluation
    eval_dict = problem.evaluate(solution)
    print(f"\nCycle Time: {solution.cycle_time}")
    print(f"Valid: {problem.satisfy(solution)}")

    if eval_dict['penalty_precedence'] > 0:
        print(f"⚠ Precedence violations: {eval_dict['penalty_precedence']}")
    if eval_dict['penalty_resource'] > 0:
        print(f"⚠ Resource violations: {eval_dict['penalty_resource']}")
    if eval_dict['penalty_unscheduled'] > 0:
        print(f"⚠ Unscheduled tasks: {eval_dict['penalty_unscheduled']}")

    # Station workload
    print("\nStation Workloads:")
    for station in problem.stations:
        station_tasks = [
            t for t, s in solution.task_assignment.items() if s == station
        ]
        if station_tasks:
            makespan = max(
                solution.task_schedule.get(t, 0) + problem.task_times[t]
                for t in station_tasks
            )
            total_work = sum(problem.task_times[t] for t in station_tasks)
            print(f"  Station {station}: {len(station_tasks)} tasks, "
                  f"total work={total_work}, makespan={makespan}")

            # Resource usage
            for resource in problem.resources:
                max_usage = 0
                for t in station_tasks:
                    usage = problem.task_resources.get((resource, t), 0)
                    max_usage = max(max_usage, usage)
                capacity = problem.station_resources.get((resource, station), 0)
                print(f"    Resource {resource}: max_usage={max_usage}, capacity={capacity}")

    print("=" * 60)
