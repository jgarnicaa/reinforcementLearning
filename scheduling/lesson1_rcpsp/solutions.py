"""
LESSON 1: RCPSP - SOLUTIONS

This file contains complete solutions to the exercises.

Compare your implementation with these solutions to check your understanding.
"""
import random
from typing import List, Dict, Hashable

from discrete_optimization.rcpsp.problem import RcpspProblem, RcpspSolution
from discrete_optimization.rcpsp.parser import get_data_available, parse_file
from discrete_optimization.datasets import fetch_data_from_psplib
from discrete_optimization.rcpsp.solvers.cpm import CpmRcpspSolver

from scheduling.utils.rcpsp_utils import (
    compute_predecessors,
    get_task_durations,
    get_resource_consumption,
    initialize_resource_availability,
    create_empty_schedule,
    compute_makespan,
)


# =============================================================================
# SOLUTION 1: Serial Generation Scheme (SGS)
# =============================================================================

def sgs_algorithm(
    rcpsp_problem: RcpspProblem,
    permutation_of_tasks: List[Hashable]
) -> Dict[Hashable, Dict[str, int]]:
    """
    Serial Generation Scheme implementation.

    Builds a feasible schedule incrementally by scheduling tasks one at a time
    according to the given permutation, respecting precedence and resource constraints.
    """

    # Setup using utility functions
    predecessors = compute_predecessors(rcpsp_problem)
    duration_task = get_task_durations(rcpsp_problem)
    resource_consumption = get_resource_consumption(rcpsp_problem)
    schedule = create_empty_schedule(rcpsp_problem)
    resource_availability = initialize_resource_availability(rcpsp_problem)

    completed_tasks = set()

    # Schedule the source task at time 0
    source_task = rcpsp_problem.source_task
    schedule[source_task] = {"start_time": 0, "end_time": 0}
    completed_tasks.add(source_task)

    # Main scheduling loop
    while len(completed_tasks) < rcpsp_problem.n_jobs:

        # Find next eligible task from permutation
        next_task = None
        for task in permutation_of_tasks:
            if task not in completed_tasks:
                # Check if all predecessors are completed
                if predecessors[task].issubset(completed_tasks):
                    next_task = task
                    break

        if next_task is None:
            raise ValueError("No eligible task found - scheduling is stuck!")

        # Compute earliest start by precedence
        earliest_start_by_precedence = 0
        for pred in predecessors[next_task]:
            earliest_start_by_precedence = max(
                earliest_start_by_precedence,
                schedule[pred]["end_time"]
            )

        # Find feasible start time considering resources
        task_duration = duration_task[next_task]
        task_resources = resource_consumption[next_task]

        start_time = earliest_start_by_precedence
        while True:
            # Check if resources are available for the entire duration
            feasible = True
            for resource in rcpsp_problem.resources_list:
                required = task_resources[resource]
                if required > 0:
                    end_time = start_time + task_duration
                    available = resource_availability[resource][start_time:end_time]
                    if any(available < required):
                        feasible = False
                        break

            if feasible:
                break  # Found a feasible start time

            start_time += 1  # Try next time slot

        # Schedule the task
        schedule[next_task] = {
            "start_time": start_time,
            "end_time": start_time + task_duration
        }

        # Update resource availability
        for resource in rcpsp_problem.resources_list:
            required = task_resources[resource]
            if required > 0:
                end_time = start_time + task_duration
                resource_availability[resource][start_time:end_time] -= required

        # Mark task as completed
        completed_tasks.add(next_task)

    return schedule


# =============================================================================
# SOLUTION 2: Priority Rules
# =============================================================================

def create_priority_permutation(
    rcpsp_problem: RcpspProblem,
    rule: str = "random"
) -> List[Hashable]:
    """
    Create task permutation based on various priority rules.
    """

    tasks = list(rcpsp_problem.tasks_list)

    if rule == "random":
        random.shuffle(tasks)
        return tasks

    elif rule in ["esd", "efd", "lsd", "lfd"]:
        # Compute CPM values
        cpm_solver = CpmRcpspSolver(rcpsp_problem)
        cpm_solver.run_classic_cpm()

        if rule == "esd":
            return sorted(tasks, key=lambda x: cpm_solver.map_node[x]._ESD)

        elif rule == "efd":
            return sorted(tasks, key=lambda x: cpm_solver.map_node[x]._EFD)

        elif rule == "lsd":
            return sorted(tasks, key=lambda x: cpm_solver.map_node[x]._LSD)

        elif rule == "lfd":
            return sorted(tasks, key=lambda x: cpm_solver.map_node[x]._LFD)

    else:
        raise ValueError(f"Unknown priority rule: {rule}")


# =============================================================================
# SOLUTION 3: Random Search
# =============================================================================

def random_search_sgs(
    rcpsp_problem: RcpspProblem,
    n_iterations: int = 1000
) -> RcpspSolution:
    """
    Simple random search: try many random permutations and keep the best.
    """

    best_makespan = float('inf')
    best_schedule = None

    print(f"🔍 Running random search with {n_iterations} iterations...")

    for i in range(n_iterations):
        # Generate random permutation
        permutation = create_priority_permutation(rcpsp_problem, rule="random")

        # Run SGS
        schedule = sgs_algorithm(rcpsp_problem, permutation)

        # Compute makespan
        makespan = schedule[rcpsp_problem.sink_task]["end_time"]

        # Update best solution if better
        if makespan < best_makespan:
            best_makespan = makespan
            best_schedule = schedule
            print(f"   ✓ New best found at iteration {i+1}: makespan = {best_makespan}")

        # Progress update
        if (i + 1) % 100 == 0:
            print(f"   Iteration {i+1}/{n_iterations}, Best so far: {best_makespan}")

    solution = RcpspSolution(problem=rcpsp_problem, rcpsp_schedule=best_schedule)

    print(f"\n✓ Search complete! Best makespan: {best_makespan}")

    return solution


# =============================================================================
# DEMONSTRATION AND TESTING
# =============================================================================

def demonstrate_solutions():
    """Demonstrate all the solution implementations."""

    print("\n" + "="*80)
    print("  LESSON 1: SOLUTIONS DEMONSTRATION")
    print("="*80 + "\n")

    # Load problem
    try:
        files = get_data_available()
    except:
        fetch_data_from_psplib()
        files = get_data_available()

    filepath = [f for f in files if "j301_1.sm" in f][0]
    rcpsp_problem = parse_file(filepath)

    print(f"📁 Loaded: {filepath.split('/')[-1]}")
    print(f"   Tasks: {rcpsp_problem.n_jobs}, Resources: {rcpsp_problem.resources}\n")

    # Test different priority rules
    print("="*80)
    print("Comparing Priority Rules")
    print("="*80 + "\n")

    results = {}

    for rule in ["random", "esd", "efd", "lsd", "lfd"]:
        perm = create_priority_permutation(rcpsp_problem, rule=rule)
        schedule = sgs_algorithm(rcpsp_problem, perm)
        solution = RcpspSolution(problem=rcpsp_problem, rcpsp_schedule=schedule)

        makespan = rcpsp_problem.evaluate(solution)
        is_feasible = rcpsp_problem.satisfy(solution)

        results[rule] = makespan

        print(f"   {rule.upper():8s}: makespan = {makespan:4.1f}  (feasible: {is_feasible})")

    print()

    # Find best rule
    best_rule = min(results, key=results.get)
    print(f"   ✓ Best priority rule: {best_rule.upper()} with makespan = {results[best_rule]}\n")

    # Run random search (small number for demo)
    print("="*80)
    print("Running Random Search")
    print("="*80 + "\n")

    best_solution = random_search_sgs(rcpsp_problem, n_iterations=500)
    best_makespan = rcpsp_problem.evaluate(best_solution)

    print(f"\n   Final best makespan: {best_makespan}")
    print(f"   Improvement over best priority rule: "
          f"{results[best_rule] - best_makespan:.1f} time units\n")

    print("="*80)
    print("  DEMONSTRATION COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    demonstrate_solutions()